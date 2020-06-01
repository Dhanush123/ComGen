import sys
import ast
import astpretty
import io


class DocstringWriter(ast.NodeTransformer):
    # def __init__(self):
    #     ast.NodeTransformer.__init__()
    #     self.sbt = ''

    # def node_to_sbt(self, node):
    #     sbt = ''
    #     children = [child for child in ast.iter_child_nodes(node)]
    #     if not children:
    #         seq =

    def visit_FunctionDef(self, node):
        with open('ast.txt', 'a+') as filey:
            filey.write(astpretty.pformat(node)+"\n---------------------\n")
        docstring = ast.get_docstring(node)
        print('docstring!!!:', docstring)
        print('node')
        for key, value in ast.iter_fields(node):
            print('-->', key, value)
            # if key == 'value':
            #     print("debug1", value.__class__.__name__,
            #           value._fields)
            # if value.__class__.__name__ == 'Constant':
            #     print(value.value)
            # if value.__class__.__name__ == 'Call':
            #     print(value.func)
        for child in ast.iter_child_nodes(node):
            print('child')
            for key, value in ast.iter_fields(child):
                print('-->', key, value)
                # if key == 'value':
                #     print("<->", type(value).__name__,
                #           type(value).__bases__)
                # if key == 'value':
                #     print("debug2", value.__class__.__name__,
                #           value._fields)
                # if value.__class__.__name__ == 'Constant':
                #     print(value.value)
                # if value.__class__.__name__ == 'Call':
                #     print(value.func)
        print('---')
        return node


if __name__ == '__main__':
    tree = ast.parse(open('ex.py').read())
    transformer = DocstringWriter()
    new_tree = transformer.visit(tree)
