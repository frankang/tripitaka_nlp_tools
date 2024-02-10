#!/usr/bin/env python
# -*- coding: utf-8 -*-


import sys
import os
import random
import tempfile
import re
from multiprocessing import Pool, cpu_count
from textwrap import wrap

random.seed(1234)

class constants(object):
    def __init__(self):
        self.random_length = [40, 100, 120, 150, 180, 200, 220, 250, 300, 400, 500, 580]
        
    def get_random_length(self):
        return random.choice(self.random_length)
    
    def move_punctuation_from_start_to_end(self, lines):
        new_lines = []
        end_idx = len(lines) - 1
        for i, l in enumerate(lines):
            new_line = l
            if i == end_idx and len(new_line) < 13:
                new_lines[-1] += new_line
                break
            r = re.match("[，。：？、！；”’》〉B]+|<br>", l)
            if r:
                strip_len = len(r.group(0))
                new_lines[-1] += l[:strip_len]
                #print(len(new_lines), r, strip_len)
                #raise ValueError
                new_line = l[strip_len:]
            if i != 0:
                #if re.match("[‘“《〈]", new_line): #让最后一个字输出引号或者书名号的开头感觉不是特别合适
                #    new_lines[-1] += new_line[0]
                #elif re.search("[‘“《〈]$",  new_lines[-1][-10:]):
                r = re.search("[‘“《〈]+$",  new_lines[-1][-5:]) #把句尾引号挪到下句开头
                if r:
                    strip_len = len(r.group(0))
                    new_line = new_lines[-1][-strip_len:] + new_line #两个引号的暂时就不考虑了
                    new_lines[-1] = new_lines[-1][:-strip_len]
            new_line = "￭" + new_line 
            new_lines.append(new_line)
        new_lines[-1] += "\n"
        return new_lines

    def repair_sent(self, line):
        if len(line) > 20:
            idx = line.find("”", 0, 60)
            if idx == -1:
                idx = line.find("。", 0, 60)
            elif idx == -1:
                idx = line.find("？", 0, 60)
            if idx >= 0:
                line = line[idx+1:]
        else:
            line = ''
        return line

    def find_singleton_book_title(self, line):
        singleton_book_title = False
        if re.search("》", line[:7]):
            ind_right = re.search("》", line[:7]).start()
            if re.search("《", line[:7]):
                ind_left = re.search("《", line[:7]).start()
                if ind_left > ind_right:
                    singleton_book_title = True
            else:
                singleton_book_title = True
        return singleton_book_title

    def find_no_punct_sent(self, line):
        if len(line) > 100:
            line = re.sub("《.+?》", "", line)
            line = re.sub("（.+?）", "", line)
            line = re.sub("󲳴", "", line)
            left_punct = len(re.findall("[、，。；！：　]", line[0:65]))
            right_punct = len(re.findall("[、，。；！：　]", line[-60:-1]))
            if left_punct < 2 or right_punct < 2 or (left_punct+right_punct) < 5: 
                return True
        return False

def process_lines(input_name, output_name, num_workers=1):
    with open(input_name) as f:
        size = os.fstat(f.fileno()).st_size
        chunk_size = int(size / num_workers)
        offsets = [0 for _ in range(num_workers + 1)]
        for i in range(1, num_workers):
            f.seek(chunk_size * i)
            pos = f.tell()
            while True:
                try:
                    line = f.readline()
                    break
                except UnicodeDecodeError:
                    pos -= 1
                    f.seek(pos)
            offsets[i] = f.tell()
            assert 0 <= offsets[i] < 1e20, "Bad new line separator, e.g. '\\r'"
    res_files = []
    pool = Pool(processes=num_workers)
    for i in range(num_workers):
        tmp = tempfile.NamedTemporaryFile(delete=False)
        tmp.close()
        res_files.append(tmp)
        pool.apply_async(_process_lines, (input_name, tmp.name, offsets[i], offsets[i + 1]))
    pool.close()
    pool.join()

    tmp_list = [res_files[i].name for i in range(num_workers)]
    tmp_discardfile_list = [res_files[i].name+".discarded" for i in range(num_workers)]
    cmd = "cat {} > {}".format(" ".join(tmp_list), output_name)
    cmd_discard = "cat {} > {}".format(" ".join(tmp_discardfile_list), "discard.txt")
    print("Now cat tmp file to the output file...\n{}".format(cmd))
    os.system(cmd)
    print("Now cat discard info to the discarded.txt file...\n{}".format(cmd_discard))
    os.system(cmd_discard)
    
    for i in range(num_workers):
        os.remove(res_files[i].name)
        os.remove(res_files[i].name+".discarded")

def _process_lines(filename, outfile, begin, end):
    const = constants()
    fo = open(outfile, "w+") 
    fd = open(outfile+".discarded", "w+") 
    with open(filename, encoding="utf-8") as f:
        f.seek(begin)
        line = f.readline()
        while line:
            pos = f.tell()
            assert 0 <= pos < 1e20, "Bad new line separator, e.g. '\\r'"
            if end > 0 and pos > end:
                break
            fo.write(process_line(const, line, fd))
            line = f.readline()
    if isinstance(outfile, str):
        fo.close()
        fd.close()

def process_line(const, line, discard_h):
    if len(line) == 1: return ""
    if re.match("[，。：？、！；”’》〉]+|<br>", line):
        discard_h.write(f"wrongly start: {line[:20]}\n")
        line = const.repair_sent(line)
        if re.match("[，。：？、！；”’》〉]+|<br>", line) or len(line) < 14:
            discard_h.write(f"cant repair sent: {line}\n")
            return ""
        discard_h.write(f"reuse sent: {line[:20]}\n")
    
    if const.find_singleton_book_title(line):
        discard_h.write(f"singleton_book_title: {line[:20]}\n")
        line = const.repair_sent(line)
        if re.match("[，。：？、！；”’》〉]+|<br>", line) or len(line) < 14:
            discard_h.write(f"cant repair sent: {line}\n")
            return ""
        discard_h.write(f"reuse sent: {line[:20]}\n")

    if const.find_no_punct_sent(line):
        discard_h.write(f"no punctuation: {line}\n")
        return ""

    line = re.sub(" +", "　", line)
    line = re.sub("\u200b|\u000b|\u00A0|\u2029|\u2028|\ufeff","", line)
    line = re.sub('。+','。',line)
    line = re.sub('[﹣－ｰ―─━ー]+', 'ー', line)
    line = re.sub('([\u0000-\u0009])','',line)
    line = re.sub("(?<=[\u2762-\u9ffff]),","，", line)
    line = re.sub("(?<=[\u2762-\u9ffff])\?","？", line)
    line = re.sub("(?<=[\u2762-\u9ffff])!","！", line)
    line = re.sub("(?<=[\u2762-\u9ffff]):","：", line)
    line = re.sub("(?<=[\u2762-\u9ffff]);","；", line)
    line = line.lower()
    line = re.sub("》·《", "·", line)
    if random.random() < 0.97:
        line = re.sub("([《〈][^》〉]*?)[•.·]([^《]*?[》〉])","\g<1>B\g<2>", line)
        line = re.sub("([《〈][^》〉]*?)[•.·]([^《]*?[》〉])","\g<1>B\g<2>", line)
        line = re.sub("([《〈][^》〉]*?)[•.·]([^《]*?[》〉])","\g<1>B\g<2>", line)
    if re.search("[，。：？、！；]{2,}", line):
        discard_h.write(f"multiple punctuation: {line}")
        return ""

    #if True: #制作valid文件用
    #    if len(line) > 1500: 
    #        return ""
    #    line = "￭" + line # to make sure line don't start with puncts
    #    return line

    #if len(line) > 600:
    if  (len(line) > 250 and random.randrange(4) == 0) or len(line) > 640:
        split_unit_length = const.get_random_length()
        split_unit_length += random.randint(-5,16) # add for randomness
        #print(f"line sample = {line[:20]}, split_unit = {split_unit_length}")
        splitted = wrap(line, split_unit_length, expand_tabs=False, replace_whitespace=False)
        splitted_enhanced = const.move_punctuation_from_start_to_end(splitted)
        if len(splitted) != len(splitted_enhanced):
            discard_h.write(f"short ending... content: {splitted_enhanced[0][:20]}\n")
        return "\n".join(splitted_enhanced)
    else:
        line = "￭" + line # to make sure line don't start with puncts
        return line



if __name__ == '__main__':
    num_workers = 40
    input_name = sys.argv[1]
    output_name = input_name + ".output"

    if num_workers > 1:
        process_lines(input_name, output_name, num_workers=num_workers)
    else:
        discard_h = open("discard.txt", "w+")
        const = constants()
        with open(output_name, "w+") as fout, open(input_name) as input_file:
            for line in input_file:
                fout.write(process_line(const, line, discard_h))

