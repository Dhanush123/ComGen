import os
import ast
import csv
import json
from pathlib import Path
import glob

from comgen.constants import lang_dir, filtered_dir, ast_dir, full_dataset_path, docstring_prefix, ast_prefix, docstring_header, ast_header
from comgen.utilities import get_filename_noext, get_filename_from_path
from comgen.logic.data.astdataextractor import ASTDataExtractor

import ray
from tqdm import tqdm


def create_relevant_dirs():
    try:
        if not os.path.exists(filtered_dir):
            Path(filtered_dir).mkdir(parents=True)
        if not os.path.exists(ast_dir):
            Path(ast_dir).mkdir(parents=True)
    except Exception as e:
        print(f'Issue creating relevant dirs for processing:\n{e}')


@ray.remote
def process_file(a_file):
    try:
        # to avoid path name problems, removing spaces
        filename = get_filename_noext(a_file).replace(' ', '')
        parsed_file_dir = os.path.join(ast_dir, filename)
        if not os.path.exists(parsed_file_dir):
            Path(parsed_file_dir).mkdir(parents=True)
        docstring_save_path = os.path.join(
            parsed_file_dir, f'{docstring_prefix}{filename}.txt')
        ast_save_path = os.path.join(
            parsed_file_dir, f'{ast_prefix}{filename}.txt')
        ast_extractor = ASTDataExtractor(
            a_file, docstring_save_path, ast_save_path)
        ast_extractor.visit(ast_extractor.ast_object)
        print(f'Saved and processed {get_filename_from_path(a_file)}')
    except (SyntaxError, IsADirectoryError, UnicodeDecodeError, UnicodeEncodeError, RecursionError):
        # may find python 2 files, non-english comments, very long methods
        pass


def combine_data(ast_dir):
    total = 0
    errs = 0
    with open(full_dataset_path, 'a+') as all_data_file:
        csv_writer = csv.writer(all_data_file, delimiter=',')
        csv_writer.writerow([docstring_header, ast_header])
    for item in tqdm(os.scandir(ast_dir)):
        if os.path.isdir(item.path):
            total += 1
            try:
                docstring_file_path = glob.glob(
                    f'{item.path}/{docstring_prefix}*')
                ast_file_path = glob.glob(f'{item.path}/{ast_prefix}*')
                if docstring_file_path and ast_file_path:
                    with open(docstring_file_path[0], 'r') as docstring_file:
                        docstring_data = docstring_file.read()
                    with open(ast_file_path[0], 'r') as ast_file:
                        ast_data = ast_file.read()
                    with open(full_dataset_path, 'a+') as all_data_file:
                        csv_writer = csv.writer(all_data_file, delimiter=',')
                        csv_writer.writerow([docstring_data, ast_data])
            except Exception as e:
                errs += 1
    print(f'Finished saving all data into 1 file! {full_dataset_path}')
    print(f'Had an issue saving {errs}/{total} files pair folders')
