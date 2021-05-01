import sys
from exit_codes import ExitCode

import astor

def dump_python(filepath):
    tree = astor.parse_file(filepath)
    dump = astor.dump_tree(tree)
    print(dump)


def main(argv=None):
    if argv is None:
        argv = sys.argv[1:]
    try:
        filepath = argv[0]
    except IndexError:
        print("Usage: show_ast <python-filepath>", file=sys.stderr)
        return ExitCode.NOINPUT

    dump_python(filepath)
    return ExitCode.OK


if __name__ == "__main__":
    sys.exit(main())

