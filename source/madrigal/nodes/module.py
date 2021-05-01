import ast

from les_iterables.augmenting import append, replace_at


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

    def __init__(self, root, path):
        self._root = root
        self._path = path

    @property
    def root(self):
        return self._root

    @property
    def ast(self):
        # Follow the path from the root
        node = self.root._ast_module()
        for op, *args in self._path:
            node = op(node, *args)
        return node

    def _ast_module(self):
        raise NotImplementedError

    def _child_path(self, op, *args):
        return tuple(append(self._path, (op, *args)))

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


class Module(ManipNode):
    def __init__(self):
        super().__init__(root=self, path=())
        self._module = ast.Module(body=[])

    def _ast_module(self):
        return self._module

    def __getitem__(self, index):
        expr_node = self._module.body[index]
        assert isinstance(expr_node, ast.Expr)
        child_path = self._child_path(lambda node, i: node.body[i], index)
        return Expr(root=self.root, path=child_path)

    def append_literal_expression_statement(self, i: int):
        self._append_literal_int(i)


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
    def __init__(self, root, path):
        super().__init__(root, path)

    def introduce_variable(self, identifier: str):
        self.root._introduce_variable(self, identifier)
