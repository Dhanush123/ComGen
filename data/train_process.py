import os
import ast
import csv

from constants import lang_dir, filtered_dir, sbt_dir
from utilities import get_filename_from_path

import ray


def save_methods_data(filename, methods_data):
    sbt_file_path = os.path.join(sbt_dir, f'{filename}.csv')
    with open(sbt_file_path, 'w') as csvfile:
        spamwriter = csv.writer(csvfile, delimiter=',')
        for method_data in methods_data:
            spamwriter.writerow(method_data)


def ast_to_sbt(node):
    return ''


@ray.remote
def process_file(a_file):
    filename = get_filename_from_path(a_file)
    tree = ast.parse(a_file)
    methods_data = []
    for node in ast.walk(tree):  # bfs traversal
        if isinstance(node, ast.FunctionDef) and ast.get_docstring(node):
            docstring = ast.get_docstring(node)
            sbt = ast_to_sbt(node)
            # TODO: will need to check if docstring ''' strings need to be removed or not
            methods_data.append([docstring, sbt])
    save_methods_data(filename, methods_data)


if __name__ == '__main__':
    ray.init()
    futures = [process_file(a_file) for a_file in os.listdir(filtered_dir)]
    ray.get(futures)
