#!/usr/bin/env python
# -*- coding: utf-8 -*-


import sys
import os
import random
import tempfile
import re
from multiprocessing import Pool, cpu_count
from textwrap import wrap

error_file = open("error.txt", "w+")
class constants(object):
    def __init__(self):
        self.special_sent_begin = "￭" #uffed
        self.punctuation_pattern = re.compile("[^，。：？、！；“”‘’《》〈〉B￯D]") # D用于标记连续标点

    def replace_list(self, l, orig_str, target_str):
        for i,j in enumerate(l):
            if j == orig_str:
                l[i] = target_str

def callback_error(result):
    print('error', result)

def process_lines(input_name, source_output, target_output, num_workers=1):
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
        pool.apply_async(_process_lines, (input_name, tmp.name, offsets[i], offsets[i + 1]), error_callback=callback_error)
    pool.close()
    pool.join()

    tmp_source_list = [res_files[i].name + ".source" for i in range(num_workers)]
    tmp_target_list = [res_files[i].name + ".target" for i in range(num_workers)]
    cmd_source = "cat {} > {}".format(" ".join(tmp_source_list), source_output)
    cmd_target = "cat {} > {}".format(" ".join(tmp_target_list), target_output)
    print("Now cat tmp file to the output file...\n{}\n{}\n".format(cmd_source, cmd_target))
    os.system(cmd_source)
    os.system(cmd_target)
    
    for i in range(num_workers):
        os.remove(res_files[i].name+".source")
        os.remove(res_files[i].name+".target")

def _process_lines(filename, outfile, begin, end):
    const = constants()
    fs = open(outfile+".source", "w+") 
    ft = open(outfile+".target", "w+") 
    with open(filename, encoding="utf-8") as f:
        f.seek(begin)
        line = f.readline()
        while line:
            pos = f.tell()
            assert 0 <= pos < 1e20, "Bad new line separator, e.g. '\\r'"
            if end > 0 and pos > end:
                break
            s, t = process_line(const, line)
            _ = fs.write(s)
            _ = ft.write(t)
            line = f.readline()
    if isinstance(outfile, str):
        fs.close()
        ft.close()

def process_line(const, line):
    line = line.strip()
    special_sign = "￯" #\uffef
    pattern = const.punctuation_pattern
    has_special_string = False
    source = list(re.sub("[，。：？、！；“”‘’《》〈〉B]|<br>", "", line))
    target_raw = re.sub("[^，。：？、！；“”‘’《》〈〉B](?=[，。：？、！；“”‘’《》〈〉B])", "Y", line) #清除标点号前面的一个字
    target_raw = re.sub("(?<=[，。：？、！；“”‘’《》〈〉B])([，。：？、！；“”‘’《》〈〉B])", "D\g<1>", target_raw)#给连续标点附加标记D
    if re.search("<br>", line[-10:]):
        has_special_string = True
        if re.search(special_sign, line):
            special_sign = "￮" #\uffee
            pattern = re.compile("[^，。：？、！；“”‘’《》〈〉B￮]")
            #if re.search(special_sign, line): #comment out to save time, we dont have this sign in our dataset
            #    error_file.write(f"line contain special chars {line}")
            #    raise ValueError("line contain special chars ")
        line = re.sub("<br>", special_sign, line)
        target_raw = re.sub("[^，。：？、！；“”‘’《》〈〉B￯](?=[，。：？、！；“”‘’《》〈〉B￯])", "Y", line) #TODO, to include the logic for new special_sign
        target_raw = re.sub("(?<=[，。：？、！；“”‘’《》〈〉B￯])([，。：？、！；“”‘’《》〈〉B￯])", "D\g<1>", target_raw)#给连续标点附加标记D
    target_raw = re.sub("Y", "", target_raw)
    target = list(pattern.sub("C", target_raw))
    if has_special_string: 
        const.replace_list(target, special_sign, "<br>")
    if not re.search("[“”‘’《》〈〉]", line):
        assert len(source) == len(target), f"for sent dont contain “”‘’《》〈〉, the length should match\n {len(source)} {len(target)}\n {line}\n {source}\n {target}\n"
    else:
        #TODO may be add check for <br>/￯ in the middle
        assert len(target) - len(source) == 2*(len(re.findall("(?<=[，。：？、！；“”‘’《》〈〉B￯])[，。：？、！；“”‘’《》〈〉B￯]", line))), f"for sent contain  “”‘’《》〈〉, the length difference between source and target should equal to the occurrences of this pattern.\n {line}\n {len(source)} {len(target)} \n"

    return " ".join(source)+"\n", " ".join(target)+"\n"



if __name__ == '__main__':
    num_workers = 40
    input_name = sys.argv[1]
    output_s = input_name + ".source"
    output_t = input_name + ".target"

    if num_workers > 1:
        process_lines(input_name, output_s, output_t, num_workers=num_workers)
    else:
        const = constants()
        with open(output_s, "w+") as os, open(output_t, "w+") as ot, open(input_name) as input_file:
            for line in input_file:
                source, target = process_line(const, line)
                os.write(source)
                ot.write(target)

