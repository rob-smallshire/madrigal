import ast
from functools import singledispatch

import astor
from les_iterables.augmenting import append

from madrigal.visitors import OneShotAppendConstantExpressionStatementVisitor, \
    OneShotIntroduceVariableVisitor, OneShotReplaceAssignmentNameVisitor


class ManipNode:

    def __init__(self, root, path):
        self._root = root
        self._path = path

    @property
    def root(self):
        return self._root

    @property
    def ast(self):
        # Follow the path from the root
        return self._resolve_path(self._path)

    def to_source(self):
        return astor.code_gen.to_source(self.ast)

    def _resolve_path(self, path):
        node = self.root._ast_module()
        for op, args, kwargs in path:
            node = op(node, *args, **kwargs)
        return node

    def _ast_module(self):
        return None

    def _child_path(self, op, *args, **kwargs):
        return tuple(append(self._path, (op, args, kwargs)))

    def _create(self, func, *args, **kwargs):
        path = self._child_path(func, *args, **kwargs)
        ast_node = self._resolve_path(path)
        return make_manip_node(ast_node, self.root, path)

    def _append_literal_int(self, i):
        visitor = OneShotAppendConstantExpressionStatementVisitor(i)
        new_ast = visitor.visit(self._module)
        ast.fix_missing_locations(new_ast)
        self._module = new_ast

    def _introduce_variable(self, manip_node, identifier):
        if not identifier.isidentifier():
            raise ValueError(f"{identifier!r} is not a valid identifier")
        visitor = OneShotIntroduceVariableVisitor(expr=manip_node.ast, identifier=identifier)
        new_ast = visitor.visit(self.root.ast)
        ast.fix_missing_locations(new_ast)
        self._module = new_ast

    def _replace_assignment_name(self, manip_node, identifier):
        if not identifier.isidentifier():
            raise ValueError(f"{identifier!r} is not a valid identifier")
        visitor = OneShotReplaceAssignmentNameVisitor(target=manip_node.ast, identifier=identifier)
        new_ast = visitor.visit(self.root.ast)
        ast.fix_missing_locations(new_ast)
        self._module = new_ast

class Module(ManipNode):
    def __init__(self):
        super().__init__(root=self, path=())
        self._module = ast.Module(body=[])

    def _ast_module(self):
        return self._module

    def __getitem__(self, index):
        return self._create(lambda ast_node, i: ast_node.body[i], index)

    def append_literal_expression_statement(self, i: int):
        self._append_literal_int(i)


@singledispatch
def make_manip_node(ast_node, root, path):
    raise NotImplementedError(f"No ManipNode for {type(ast_node).__name__}")


@make_manip_node.register(ast.Expr)
def _(ast_node, root, path):
    return Expr(root, path)


@make_manip_node.register(ast.Assign)
def _(ast_node, root, path):
    return Assign(root, path)


@make_manip_node.register(ast.Name)
def _(ast_node, root, path):
    return Name(root, path)


class Expr(ManipNode):

    def introduce_variable(self, identifier: str):
        self.root._introduce_variable(self, identifier)


class Assign(ManipNode):

    @property
    def variable(self):
        return self._create(lambda node: node.targets[0])

    # TODO: Access to the value, which oddly is not an expression


class Name(ManipNode):

    def replace(self, identifier):
        """Replace the name to which the assignment binds.

        Note: This is not a *rename* operation.
        """
        self._root._replace_assignment_name(self, identifier)