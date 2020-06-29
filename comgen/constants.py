import os

values_dir = os.path.join(os.getcwd(), 'comgen', 'values')
repos_path = os.path.join(values_dir, 'repos.txt')
lang_dir = os.path.join(values_dir, 'Python')

raw_dir = os.path.join(lang_dir, 'raw')
filtered_dir = os.path.join(lang_dir, 'filtered')
ast_dir = os.path.join(lang_dir, 'ast2')

full_dataset_path = os.path.join(values_dir, 'alldata2.csv')

docstring_prefix = 'docstring_'
ast_prefix = 'ast_'

docstring_header = "docstring"
ast_header = "ast"
