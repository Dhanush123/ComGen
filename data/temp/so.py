import ast
import io
# import astunparse

from unparse import Unparser
import astpretty


class DocstringWriter(ast.NodeTransformer):
    def __init__(self):
        self.sbt = ""

    def visit_FunctionDef(self, node):
        if isinstance(node, ast.FunctionDef):
            docstring = ast.get_docstring(node)
            # print("docstring!!!:", docstring)
            # print(astpretty.pformat(node))
            new_docstring_node = make_docstring_node(docstring)
            if docstring:
                # Assumes the existing docstring is the first node
                # in the function body.
                node.body[0] = new_docstring_node
            else:
                node.body.insert(0, new_docstring_node)
            return node


def make_docstring_node(docstring):
    if docstring is None:
        content = "A new docstring"
    else:
        content = docstring + " -- MODIFIED"
    s = ast.Str(content)
    return ast.Expr(value=s)


if __name__ == "__main__":
    tree = ast.parse(open("example.py").read())
    transformer = DocstringWriter()
    new_tree = transformer.visit(tree)
    ast.fix_missing_locations(new_tree)
    buf = io.StringIO()
    Unparser(new_tree, buf)
    buf.seek(0)
    # print(buf.read())
    with open("output.py", "w") as filey:
        filey.write(astunparse.unparse(tree))
