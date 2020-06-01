import os
import json
import collections
import sys
from pathlib import Path

import javalang
from tqdm import tqdm
import ray

# core logic for this file comes from https://github.com/xing-hu/EMSE-DeepCom/blob/master/data_utils/get_ast.py
# I made minor modifications to suit my project


def process_source(file_name, save_file):
    with open(file_name, 'r', encoding='utf-8') as source:
        lines = source.readlines()
    with open(save_file, 'w+', encoding='utf-8') as save:
        for line in lines:
            # print(">", line)
            # print("----------")
            code = line.strip()
            tokens = list(javalang.tokenizer.tokenize(code))
            tks = []
            for tk in tokens:
                if tk.__class__.__name__ == 'String' or tk.__class__.__name__ == 'Character':
                    tks.append('STR_')
                elif 'Integer' in tk.__class__.__name__ or 'FloatingPoint' in tk.__class__.__name__:
                    tks.append('NUM_')
                elif tk.__class__.__name__ == 'Boolean':
                    tks.append('BOOL_')
                else:
                    tks.append(tk.value)
            save.write(" ".join(tks) + '\n')


def create_ast(file_name, w):
    with open(file_name, 'r', encoding='utf-8') as f:
        lines = f.readlines()
    with open(w, 'w+', encoding='utf-8') as wf:
        ign_cnt = 0
        for line in tqdm(lines):
            code = line.strip()
            tokens = javalang.tokenizer.tokenize(code)
            token_list = list(javalang.tokenizer.tokenize(code))
            length = len(token_list)
            parser = javalang.parser.Parser(tokens)
            try:
                tree = parser.parse_member_declaration()
            except (javalang.parser.JavaSyntaxError, IndexError, StopIteration, TypeError):
                continue
            flatten = []
            for path, node in tree:
                flatten.append({'path': path, 'node': node})

            ign = False
            outputs = []
            stop = False
            for i, Node in enumerate(flatten):
                d = collections.OrderedDict()
                path = Node['path']
                node = Node['node']
                children = []
                for child in node.children:
                    child_path = None
                    if isinstance(child, javalang.ast.Node):
                        child_path = path + tuple((node,))
                        for j in range(i + 1, len(flatten)):
                            if child_path == flatten[j]['path'] and child == flatten[j]['node']:
                                children.append(j)
                    if isinstance(child, list) and child:
                        child_path = path + (node, child)
                        for j in range(i + 1, len(flatten)):
                            if child_path == flatten[j]['path']:
                                children.append(j)
                d["id"] = i
                d["type"] = str(node)
                if children:
                    d["children"] = children
                value = None
                if hasattr(node, 'name'):
                    value = node.name
                elif hasattr(node, 'value'):
                    value = node.value
                elif hasattr(node, 'position') and node.position:
                    for i, token in enumerate(token_list):
                        if node.position == token.position:
                            pos = i + 1
                            value = str(token.value)
                            while (pos < length and token_list[pos].value == '.'):
                                value = value + '.' + token_list[pos + 1].value
                                pos += 2
                            break
                elif type(node) is javalang.tree.This \
                        or type(node) is javalang.tree.ExplicitConstructorInvocation:
                    value = 'this'
                elif type(node) is javalang.tree.BreakStatement:
                    value = 'break'
                elif type(node) is javalang.tree.ContinueStatement:
                    value = 'continue'
                elif type(node) is javalang.tree.TypeArgument:
                    value = str(node.pattern_type)
                elif type(node) is javalang.tree.SuperMethodInvocation \
                        or type(node) is javalang.tree.SuperMemberReference:
                    value = 'super.' + str(node.member)
                elif type(node) is javalang.tree.Statement \
                        or type(node) is javalang.tree.BlockStatement \
                        or type(node) is javalang.tree.ForControl \
                        or type(node) is javalang.tree.ArrayInitializer \
                        or type(node) is javalang.tree.SwitchStatementCase:
                    value = 'None'
                elif type(node) is javalang.tree.VoidClassReference:
                    value = 'void.class'
                elif type(node) is javalang.tree.SuperConstructorInvocation:
                    value = 'super'

                if value is not None and type(value) is type('str'):
                    d['value'] = value
                if not children and not value:
                    ign = True
                    ign_cnt += 1
                outputs.append(d)
            if not ign:
                wf.write(json.dumps(outputs))
                wf.write('\n')


@ray.remote
def run_tokenize_and_ast(a_file):
    filename_without_ext = os.path.splitext(a_file)[0]
    tokenized_file_path = os.path.join(
        tokenized_dir, f'{filename_without_ext}.txt')
    ast_file_path = os.path.join(
        ast_dir, f'{filename_without_ext}.json')

    file_path = os.path.abspath(a_file)
    # process and tokenize the source code: strings -> STR_, numbers-> NUM_, Booleans-> BOOL_
    process_source(a_file, tokenized_file_path)
    # generate ast file from tokenized source code
    create_ast(tokenized_file_path, ast_file_path)


def aggregate_asts(ast_dir):
    # put all ast files data into 1 file for convenience in model training
    with open('finalast.json', 'a+') as repo_file:
        repo_file.write(
            f'{repo.full_name},{repo.html_url},{repo.stargazers_count}\n')


if __name__ == '__main__':
    # ray.init()

    # filtered_dir = os.path.join(os.getcwd(), 'Java', 'filtered')
    # processed_dir = os.path.join(os.getcwd(), 'Java', 'processed')
    # tokenized_dir = os.path.join(processed_dir, 'tokenized')
    # ast_dir = os.path.join(processed_dir, 'ast')
    # Path(processed_dir).mkdir(parents=True)

    # # if check technically isn't necessary, but better to be safe
    # futures = [run_tokenize_and_ast.remote(a_file) for a_file in os.listdir(filtered_dir)
    #            if os.path.isfile(a_file) and os.path.splitext(a_file)[1] == 'java']
    # ray.get(futures)

    process_source(sys.argv[1], 'source.code')
    create_ast('source.code', sys.argv[2])
