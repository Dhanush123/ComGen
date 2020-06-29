import csv

from comgen.constants import docstring_header, ast_header, full_dataset_path


def load_dataset():
    docstring_data, ast_data = [], []
    try:
        with open(full_dataset_path, newline='') as dataset:
            reader = csv.DictReader(dataset)
            for row in reader:
                docstring_data.append(row[docstring_header])
                ast_data.append(row[ast_header])
        return docstring_data, ast_data
    except Exception as e:
        print('Error loading dataset', e)
