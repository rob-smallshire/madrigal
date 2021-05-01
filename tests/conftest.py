"""Configuration for pytest.

Place configuration for py.test, such as custom assertions
representations into this file.
"""
import ast
from itertools import zip_longest

import astor


try:
    # Workaround for https://youtrack.jetbrains.com/issue/PY-37268
    import teamcity.pytest_plugin
except ImportError:
    def pycharm_compare(op, left, right):
        return None
else:
    pycharm_compare = teamcity.pytest_plugin.EchoTeamCityMessages.pytest_assertrepr_compare
    del teamcity.pytest_plugin.EchoTeamCityMessages.pytest_assertrepr_compare


def pytest_assertrepr_compare(op, left, right):
    if isinstance(left, bytes) and isinstance(right, bytes) and op == "==":
        return ['Comparing bytes collections:',
                ' left: {}'.format(' '.join(format(b, '02X') for b in left)),
                'right: {}'.format(' '.join(format(b, '02X') for b in right)),
                '       {}'.format(' '.join('  ' if l==r else '^^' for l, r in zip_longest(left, right)))
                ]
    elif isinstance(left, ast.Module) and isinstance(right, ast.Module) and op == "==":
        return ['Comparing ast.Module objects:',
                ' left: {}'.format(astor.dump_tree(left)),
                'right: {}'.format(astor.dump_tree(right)),
                ]
    #return pycharm_compare(op, left, right)

