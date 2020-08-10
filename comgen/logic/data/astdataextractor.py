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

    def visit_FunctionDef(self, node):
        try:
            # only want docstrings that are in ascii so I can read + simplifies project
            temp_docstring = ast.get_docstring(node)
            if temp_docstring:
                self.function_docstring = temp_docstring.encode(
                    'ascii').decode('utf-8')
            # for training set, only want functions that have docstring since it's the training label
            if self.function_docstring:
                self.node_visit(node)
                self.single_function_ast_str = self.single_function_ast_str.encode(
                    'ascii').decode('utf-8')
                if self.single_function_ast_str:
                    self.save_data()
            self.single_function_ast_str = ''
        except (UnicodeDecodeError, UnicodeEncodeError):
            pass

    def args_to_str(self, args):
        return f'args{len(args)}'

    def assign_to_str(self, node):
        return type(node.value).__name__

    def expr_to_str(self, node):
        return node.value.__class__.__name__

    def constant_to_str(self, node):
        return f'{type(node.value).__name__}'

    def node_to_str(self, node):
        ast_set = ("Delete", "For", "AsyncFor",
                   "While", "If", "With", "AsyncWith", "Raise",
                   "Try", "Assert", "Global", "Nonlocal", "Pass",
                   "Break", "Continue", "ExceptHandler",
                   "BoolOp", "NamedExpr", "BinOp", "UnaryOp", "Lambda",
                   "IfExp", "Dict", "Set", "ListComp", "SetComp", "DictComp",
                   "GeneratorExp", "Await", "Compare", "FormattedValue", "JoinedStr"
                   "Constant", "Attribute", "Subscript", "Starred", "Name"
                   "List", "Tuple")
        if isinstance(node, ast.AST):
            fields_list = []
            if node.__class__.__name__ == "FunctionDef":
                fields_list.append(node.__class__.__name__)
                if node.args.args:
                    fields_list.append(self.args_to_str(node.args.args))
            elif node.__class__.__name__ in ("Assign", "AugAssign"):
                fields_list.append("Assign")
            elif node.__class__.__name__ in ("Yield", "YieldFrom"):
                fields_list.append("Yield")
            elif node.__class__.__name__ == "Expr":
                fields_list.append(self.expr_to_str(node))
            elif node.__class__.__name__ == "Constant":
                fields_list.append(self.constant_to_str(node))
            elif node.__class__.__name__ == "Call":
                fields_list.append(self.args_to_str(node.args))
            else:
                fields_list.append(node.__class__.__name__)
            return f"{' '.join(fields_list)}" if fields_list else ""
        else:
            return repr(node)

    def node_visit(self, node):
        node_str = self.node_to_str(node).strip()
        for field, value in ast.iter_fields(node):
            if isinstance(value, list):
                for value_item in value:
                    if isinstance(value_item, ast.AST):
                        self.node_visit(value_item)
            elif isinstance(value, ast.AST):
                self.node_visit(value)

    def save_data(self):
        with open(self.docstring_file_path, 'w+') as docstring_file:
            docstring_file.write(self.function_docstring)
        with open(self.ast_file_path, 'w+') as ast_file:
            ast_file.write(self.single_function_ast_str)
