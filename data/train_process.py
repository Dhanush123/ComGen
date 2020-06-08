import os
import ast
import csv
import json
from pathlib import Path

from constants import lang_dir, filtered_dir, ast_dir, all_data_file
from utilities import get_filename_noext
from astdataextractor import ASTDataExtractor

import ray
from tqdm import tqdm


def create_relevant_dirs():
    try:
        if not os.path.exists(filtered_dir):
            Path(filtered_dir).mkdir(parents=True)
        if not os.path.exists(ast_dir):
            Path(ast_dir).mkdir(parents=True)
    except Exception as e:
        print(e)


@ray.remote
def process_file(a_file):
    ast_save_path = os.path.join(ast_dir, f'{get_filename_noext(a_file)}.json')
    ast_extractor = ASTDataExtractor(a_file, ast_save_path)
    ast_extractor.visit(ast_extractor.ast_object)
    ast_extractor.save_ast()


def combine_data(ast_dir):
    for a_file in tqdm(os.scandir(ast_dir)):
        json_data = json.load(open(a_file.path))
        for _, data in json_data.items():
            with open(all_data_file, 'a+') as csvfile:
                csv_writer = csv.writer(csvfile, delimiter=',')
                csv_writer.writerow([data["docstring"], data["ast"]])


if __name__ == '__main__':
    ray.init()
    create_relevant_dirs()
    futures = [process_file.remote(a_file.path)
               for a_file in os.scandir(filtered_dir)]
    ray.get(futures)
    combine_data(ast_dir)
