# -- coding: UTF-8 --
# -*- coding: utf-8 -*-
import sys
import os
import glob
import re
from collections import OrderedDict, defaultdict
from random import shuffle, choice


word_count = tuple([(100,140), (141, 180), (181, 245), (246, 300), (301, 350),(351,400),
                    (401, 460), (461, 520), (521, 580), (581, 650), (651, 730), (731, 800),
                    (801, 880), (881, 970), (971, 1080), (1081, 1200), (1201, 1300), (1301, 1400), 
                    (1401, 1500), (1501, 1620), (1621, 1730), (1731, 1850), (1851, 1900), (1901, 2030),
                    (2031, 2200), (2201, 2380), (2381, 2500), (2501, 2700), (2701, 2900), (2901, 3100), 
                    (3101, 3250)])
h = open("result.txt", "w+")
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
        word_count = 0
        m = get_one_range()
        big_paragraph = []
        for line in f:
            line_content = line.strip()
            word_count += len(line_content)
            big_paragraph.append(line_content)

            if m[0] < word_count/3 < m[1]:
                h.write("".join(big_paragraph)+"\n")
                word_count = 0
                del big_paragraph[:]
                m = get_one_range()
                continue

            if word_count/3 > m[1]:
                h.write("".join(big_paragraph)+"\n")
                del big_paragraph[:]
                to_adopt.append(m)
                to_discard.append(find_element(word_count/3))
                m = get_one_range()
                word_count = 0
                continue

        if big_paragraph:
            to_adopt.append(m)
            if word_count / 3 < 100: return 
            to_discard.append(find_element(word_count/3))
            #print m, to_discard[-1]
            h.write("".join(big_paragraph)+"\n")




if __name__ == '__main__':
    if len(sys.argv)>1 :
        path=sys.argv[1]
    else :
        print "usage: preprocess.py dirname"
        sys.exit(1)
    print "building file lists..."
    # filelist = glob.glob(path+"/*")
    filelist = []
    for root, dirs, files in os.walk(path):
        for file in files:
            if file.endswith('.txt'):
                 filelist.append(os.path.join(root, file))
    print "file lists built"


    # print "getting unfinished file paths"
    unfinished_file_list = []
    # for cursor in sutra_file_info.find({"finished":False}):
    #     unfinished_file_list.append(cursor)
    unfinished_file_list = filelist
    print "starting process files, the default process number is 2, increase it "
    #p = Pool(2)
    print "i am here!!before mapping"
    #p.map(processFile, unfinished_file_list)
    shuffle(unfinished_file_list)
    print len(unfinished_file_list)
    for item in unfinished_file_list:
    #     print item
        processFile(item)
    h.close()
