# coding: utf-8
import random
import os
def get_line_number(file_addr):
    return os.popen("wc -l " + file_addr).readline().split()[0]


import sys
if sys.version_info[0] > 3:
    raise Exception("Must be using Python 2.7")


file_addr = sys.argv[1]
line_count = int(sys.argv[2])
sample_num = int(sys.argv[3])


if not isinstance(line_count, int):
    raise Exception("the second argu must be an integer")

real_line_count = int(get_line_number(file_addr))
if real_line_count != line_count:
    print(real_line_count, line_count)
    raise Exception("currently, the line_count should match the file line count!")


f1 = open(file_addr + ".valid", "w+")
f2 = open(file_addr + ".train", "w+")

random.seed(1234)
sample_set = set(random.sample(range(line_count), sample_num))

with open(file_addr) as f:
    count = 0
    for line in f:
        if count in sample_set:
            _=f1.write(line)
        else:
            _=f2.write(line)
        count += 1

f1.close()
f2.close()

