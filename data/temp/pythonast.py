import ast
import astpretty

with open("example.py") as fd:
    file_contents = fd.read()
    # print(file_contents)

# module = ast.parse(file_contents)
# function_definitions = [
#     node for node in module.body if isinstance(node, ast.FunctionDef)]
# print(function_definitions)
# print(str(module))

astpretty.pprint(ast.parse(file_contents))
with open("ast.txt", "w") as fd:
    fd.write(astpretty.pformat(ast.parse(file_contents)))
    # print(ast.dump(ast.parse(file_contents)))
