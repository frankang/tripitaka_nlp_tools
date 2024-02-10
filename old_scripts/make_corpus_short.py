# -- coding: UTF-8 --
# -*- coding: utf-8 -*-
import sys
import os
import glob
import re
from collections import OrderedDict, defaultdict
from random import shuffle, choice


#word_count = tuple([(10,40),(41,70), (71,99), (101,120),(121,140), (141, 160),(161,180), (181, 200),(201,240), (241, 280), (281, 320),(321,360),(361,400), (401, 450), (451,500),(501, 550),(551,600),(601,650),(651,700), (701,750), (751, 800),(801, 880), (881, 970), (971, 1080), (1081, 1200),(1201,1300),(1300,1400),(1401,1460),(1461,1550),(1551,1700),(1701,1800),(1801,1900),(1901,2049)])
word_count = []
for i in range(20, 2000, 50):
    word_count.append(i)
for i in range(10, 700, 25):
    word_count.append(i)
word_count = tuple(set(word_count))

def get_one_length():
    return choice(word_count)
#h = open("result.txt", "w+")
h=open(sys.argv[1]+".concat", "w+")
to_discard = []
to_adopt = []

def find_element(a):
    for i in reversed(word_count):
        if a > i[0]:
            return i

    else: return word_count[0]


def get_one_range():
    # print "to adopt", to_adopt
    # print "to discard", len(to_discard)
    if to_adopt:
        shuffle(to_adopt)
        return to_adopt.pop()

    one_choice = None
    while not one_choice:
        one_choice = choice(word_count)
        if one_choice in to_discard: 
            to_discard.remove(one_choice)
            one_choice = None
    return one_choice


def processFile(file_addr):

    with open(file_addr, "r") as f:
        #m = get_one_range()
        l = get_one_length()
        big_paragraph = []
        words = 0
        for line in f:
            line_content = line.strip()
            words += len(line_content)
            big_paragraph.append(line_content)

            if l < words:
                _ = h.write("".join(big_paragraph)+"\n")
                del big_paragraph[:]
                words = 0
                l = get_one_length()
                continue

        if big_paragraph:
            _ = h.write("".join(big_paragraph)+"\n")


if __name__ == '__main__':
    if len(sys.argv)>1 :
        path=sys.argv[1]
    else :
        print("usage: preprocess.py dirname")
        sys.exit(1)
    print("building file lists...")
    # filelist = glob.glob(path+"/*")
    filelist = []
    #for root, dirs, files in os.walk(path):
    #    for file in files:
    #        if file.endswith('.txt'):
    #             filelist.append(os.path.join(root, file))
    #print "file lists built"


    unfinished_file_list = []
    # for cursor in sutra_file_info.find({"finished":False}):
    #     unfinished_file_list.append(cursor)
    #unfinished_file_list = filelist
    unfinished_file_list.append(path)
    print("starting process files, the default process number is 2, increase it ")
    #p = Pool(2)
    print("i am here!!before mapping")
    #p.map(processFile, unfinished_file_list)
    shuffle(unfinished_file_list)
    print(len(unfinished_file_list))
    for item in unfinished_file_list:
    #     print item
        processFile(item)
    h.close()
