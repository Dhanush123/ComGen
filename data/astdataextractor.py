import sys
import ast
import io

import os


class ASTDataExtractor(ast.NodeVisitor):

    def __init__(self, python_file_path, docstring_file_path, ast_file_path):
        self.docstring_file_path = docstring_file_path
        self.ast_file_path = ast_file_path
        self.ast_object = ast.parse(open(python_file_path).read())
        self.single_function_ast_str = ''
        self.function_docstring = ''

    def visit_Load(self, node):
        # load field is too common & generic -> doesn't provide value to include
        pass

    def visit_FunctionDef(self, node):
        # only want docstrings that are in ascii so I can read + simplifies project
        self.function_docstring = ast.get_docstring(node).encode('ascii')
        # for training set, only want functions that have docstring since it's the training label
        if function_docstring:
            self.node_visit(node)
            self.single_function_ast_str = self.single_function_ast_str.encode(
                'ascii')
            self.save_data()
        self.single_function_ast_str = ''

    def node_to_str(self, node):
        if isinstance(node, ast.AST):
            fields_list = [self.node_to_str(val).replace("'", "") for name, val in ast.iter_fields(
                node) if name in ('name', 'attr', 'id', 'arg')]
            str_fields_list = f"-{','.join(fields_list)}" if fields_list else ""
            rv = f'({node.__class__.__name__}{str_fields_list})'
            return rv
        else:
            return repr(node)

    def node_visit(self, node, level=0):
        self.single_function_ast_str += f"({self.node_to_str(node)}"
        for field, value in ast.iter_fields(node):
            if isinstance(value, list):
                for item in value:
                    if isinstance(item, ast.AST):
                        self.node_visit(item, level=level+1)
            elif isinstance(value, ast.AST):
                self.node_visit(value, level=level+1)
        self.single_function_ast_str += ')'

    def save_ast(self):
        with open(self.docstring_file_path, 'w+') as docstring_file:
            docstring_file.write(self.function_docstring, docstring_file)
        with open(self.ast_file_path, 'w+') as ast_file:
            ast_file.write(self.single_function_ast_str, ast_file)
