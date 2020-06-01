from redbaron import RedBaron
import sys

filename = sys.argv[1]
with open(filename, 'r') as a_file:
    data = a_file.read()

red = RedBaron(data)

# for i, node in enumerate(red):
#     print(i)
#     node.help()
#     print("--------------")

# print(red[13].help(10))

print(red.fst())
