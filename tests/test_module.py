import ast

import astor

from madrigal.nodes.module import Module


def test_module_constructor():
    _ = Module()


def test_module_append_literal_constant_expression():
    m = Module()
    m.append_literal_expression_statement(42)


def test_module_append_literal_constant_expression_given_expression_statement():
    m = Module()
    m.append_literal_expression_statement(37)
    expected_ast = ast.Module(body=[ast.Expr(value=ast.Constant(value=37, kind=None))])
    assert astor.dump_tree(m.ast) == astor.dump_tree(expected_ast)


def test_retrieve_last_statement():
    m = Module()
    m.append_literal_expression_statement(76)
    last_statement = m[-1]
    expected_ast = ast.Expr(value=ast.Constant(value=76, kind=None))
    assert astor.dump_tree(last_statement.ast) == astor.dump_tree(expected_ast)


def test_introduce_variable():
    m = Module()
    m.append_literal_expression_statement(76)
    m[-1].introduce_variable("a")
    expected_ast = ast.Module(
        body=[
            ast.Assign(
                targets=[ast.Name(id="a")],
                value=ast.Constant(value=76, kind=None),
                type_comment=None,
            )
        ],
    )
    assert astor.dump_tree(m.ast) == astor.dump_tree(expected_ast)
