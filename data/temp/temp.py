import javalang
import sys
import re
# data = None
filename = sys.argv[1]
with open(filename, 'r') as a_file:
    data = a_file.read()  # .replace('\n', '')

# tokens = javalang.tokenizer.tokenize(data)
# parser = javalang.parser.Parser(tokens)
tree = javalang.parse.parse(data)
# print("raw:")
# print(data)
# print(len(data))
# print("parsed code:")
# i = set()
# for path, node in tree:
#     i.add(str(path))
# print(node.__class__.__name__)
# print(len(i))
# print(dir(tree))
# print(len(str(tree)))
print("PROCESSED")
with open("temp.txt", "w+") as text_file:
    text_file.write(str(tree))
    # for path in i:
    #     print(len(path))
    # print("\n\n")
    # print(re.findall(r'\*\*(.*?)\*\/', data, re.S))
