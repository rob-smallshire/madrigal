import ast

import astor

from madrigal.manipulators import Module


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


def test_introduce_two_variables_and_replace_the_second_one():
    m = Module()
    # Imperative program transformations. Each statement navigates to a
    # specific syntax element and performs one of the transformations
    # available on that element
    m.append_literal_expression_statement(76)
    m.append_literal_expression_statement("Hello, World!")
    m[0].introduce_variable("number")
    m[1].introduce_variable("hello")
    m[1].variable.replace("greeting")

    assert m.to_source() == (
        "number = 76\n"
        "greeting = 'Hello, World!'\n"
    )
