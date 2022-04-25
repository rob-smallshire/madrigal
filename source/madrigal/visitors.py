import ast

from les_iterables.augmenting import append, replace_at


class OneShotAppendConstantExpressionStatementVisitor(ast.NodeTransformer):
    def __init__(self, value):
        self._expr = ast.Expr(value=(ast.Constant(value=value)))

    def visit_Module(self, node):
        if self._expr is not None:
            new_node = ast.Module(list(append(node.body, self._expr)))
            ast.copy_location(new_node, node)
            node = new_node
            self._expr = None
        self.generic_visit(node)
        return node


class OneShotIntroduceVariableVisitor(ast.NodeTransformer):
    def __init__(self, expr, identifier):
        self._name = ast.Name(id=identifier)
        self._expr = expr

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


class OneShotReplaceAssignmentNameVisitor(ast.NodeTransformer):
    def __init__(self, target, identifier):
        self._name = ast.Name(id=identifier)
        self._target = target

    def visit_Assign(self, node):
        if self._target is not None:
            if self._target in node.targets:

                new_node = ast.Assign(
                    targets=[self._name],
                    value=node.value,
                )

                node = new_node
                self._target = None
        self.generic_visit(node)
        return node