import os
import ast
import csv
import json
from pathlib import Path
import glob

from constants import lang_dir, filtered_dir, ast_dir, all_data_file, docstring_prefix, ast_prefix
from utilities import get_filename_noext, get_filename_from_path
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
    except (SyntaxError, IsADirectoryError, UnicodeDecodeError, UnicodeEncodeError):
        # may find python 2 files and non-english comments
        pass


def combine_data(ast_dir):
    for item in tqdm(os.scandir(ast_dir)):
        if os.path.isdir(item.path):
            try:
                docstring_file = glob.glob(
                    f'{item.path}/{docstring_prefix}*')[0]
                ast_file = glob.glob(f'{item.path}/{ast_prefix}*')[0]
                with open(docstring_file, 'r') as docstring_file:
                    docstring_data = docstring_file.read()
                with open(ast_file, 'r') as ast_file:
                    ast_data = ast_file.read()
                with open(all_data_file, 'a+') as csvfile:
                    csv_writer = csv.writer(csvfile, delimiter=',')
                    csv_writer.writerow([docstring_data, ast_data])
            except Exception as e:
                print(
                    f'Problem with extracting and saving data from: {docstring_file},{ast_file}\n{e}')
    print(f'Finished saving all data into 1 file! {all_data_file}')


if __name__ == '__main__':
    ray.init()
    create_relevant_dirs()
    futures = [process_file.remote(a_file.path)
               for a_file in os.scandir(filtered_dir)]
    ray.get(futures)
    print("Shutting down Ray...")
    ray.shutdown()
    print(f'Processed {len(futures)} files')
    combine_data(ast_dir)
    print("done")
