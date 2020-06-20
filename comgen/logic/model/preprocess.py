import csv

# from .modelconstants import full_dataset_path, docstring_header, ast_header
from ..data import dataconstants

if __name__ == '__main__':
    print(dataconstants.ast_dir)


def create_dataset():
    return "SS"
    # with open(full_dataset_path, newline='') as dataset:
    #     reader = csv.DictReader(csvfile)
    #     for row in reader:
    #         print(row['first_name'], row['last_name'])

    # lines = io.open(path, encoding='UTF-8').read().strip().split('\n')

    # word_pairs = [[preprocess_sentence(w) for w in l.split(
    #     '\t')] for l in lines[:num_examples]]

    # return zip(*word_pairs)
