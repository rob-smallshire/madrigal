import ast
from itertools import chain

from les_iterables.augmenting import append, prepend, replace_at


class OneShotAppendConstantExpressionStatementVisitor(ast.NodeTransformer):
    def __init__(self, value):
        self._expr = ast.Expr(value=(ast.Constant(value=value)))

    def generic_visit(self, node):
        ast.NodeVisitor.generic_visit(self, node)

    def visit_Module(self, node):
        if self._expr is not None:
            new_node = ast.Module(list(append(node.body, self._expr)))
            ast.copy_location(new_node, node)
            node = new_node
            self._expr = None
        self.generic_visit(node)
        return node


class ManipNode:
    def __init__(self, parent):
        self._parent = parent

    @property
    def parent(self):
        return self._parent

    @property
    def root(self):
        node = self
        while True:
            parent = node.parent
            if parent is None:
                return node
            node = parent


class Module(ManipNode):
    def __init__(self):
        super().__init__(parent=None)
        self._module = ast.Module(body=[])

    @property
    def ast(self):
        return self._module

    def __getitem__(self, index):
        expr_node = self._module.body[index]
        assert isinstance(expr_node, ast.Expr)
        return Expr(parent=self, node=expr_node)

    def append_literal_expression_statement(self, i: int):
        self._append_literal_int(i)

    def _append_literal_int(self, i):
        visitor = OneShotAppendConstantExpressionStatementVisitor(i)
        new_ast = visitor.visit(self._module)
        ast.fix_missing_locations(new_ast)
        self._module = new_ast

    def _introduce_variable(self, node, identifier):
        if not identifier.isidentifier():
            raise ValueError(f"{identifier!r} is not a valid identifier")
        visitor = OneShotIntroduceVariableVisitor(expr=node, identifier=identifier)
        new_ast = visitor.visit(self.root.ast)
        ast.fix_missing_locations(new_ast)
        self._module = new_ast


class OneShotIntroduceVariableVisitor(ast.NodeTransformer):
    def __init__(self, expr, identifier):
        self._name = ast.Name(id=identifier)
        self._expr = expr

    def generic_visit(self, node):
        ast.NodeVisitor.generic_visit(self, node)

    def visit_Module(self, node):
        if self._expr is not None:
            if self._expr in node.body:
                index = node.body.index(self._expr)

                new_node = ast.Module(
                    list(
                        replace_at(
                            node.body,
                            index,
                            ast.Assign(targets=[self._name], value=self._expr.value),
                        )
                    )
                )
                node = new_node
                self._expr = None
            self.generic_visit(node)
            return node


class Expr(ManipNode):
    def __init__(self, parent, node):
        # TODO: Refer with a path
        super().__init__(parent)
        self._expr = node

    @property
    def ast(self):
        return self._expr

    def introduce_variable(self, identifier: str):
        self.root._introduce_variable(self.ast, identifier)
