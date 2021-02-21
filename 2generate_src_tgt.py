# -*- coding: utf-8 -*-
import sys
import re
from multiprocessing import Pool
import os
import random
import time
discard = open("/tmp/discarded{}.txt".format(str(random.randint(11111, 99999))), "w+")
if len(sys.argv) == 2 :
    filepath=sys.argv[1]
else :
    print("usage: scripy.py filepath ")
    sys.exit(1)
def is_han(uchar):
        """判断一个unicode是否是汉字"""
        if uchar >= u'\u2e80' and uchar<=u'\u9fff':
                return True
        else:
                return False

def check_punct(s):
    ls = len(s)
    if ls > 180:
        if not re.search("[、，。；！]", s[:60]):
            return True
        elif not re.search("[、，。！；：]", s[-60:-2]):
            return True
    elif 100 < ls <= 180  and not re.search("[、，。！：；]", s[:70]):
        return True
    elif 50 < ls <= 100 and not re.search("[、，。！？：]", s[:-2]):
        return True
    return False
def process_single_file(filepath):
    max_sentlen_threshold = 501
    offset = 0
    def determine_split_num(n, max_threshold=600):
        count = 1
        new_n = n
        while new_n >= max_threshold:
            count += 1
            new_n = n / count
        return count
    def get_sent_seg_idx(l, split_n, offset=0): 
        avgl = l // split_n + 1
        split_idx = [i for i in range(0, l, avgl)]
        if avgl * split_n < l: split_idx = split_idx[:-1] # [0, 249, 498, 747, 996]remove the last one
        sent_seg_idx = []
        start_idx = 0
        for i in split_idx[1:]:
            sent_seg_idx.append((start_idx, i+offset))
            start_idx = i-offset
        sent_seg_idx.append((start_idx, l))
        return sent_seg_idx

    origin = open(filepath)
    h1 = open(filepath+".source", "w+")
    h2 = open(filepath+".target", "w+")
    count = 0
    for s in origin:
        s = s.strip()
        #s = re.sub("『』「」：、；《》“”‘’", "", s)
        if re.search("[A-Za-zТеаЙЩЪ\?Οк]", s): continue
        s = re.sub("[”“’‘「」》《『』〈〉]","",s)
        s = re.sub('\s+',' ',s)
        splited_sentence_batch = []
        no_punctuation = check_punct(s)
        if no_punctuation: 
            discard.write(s+"\n")
            continue
        if len(s) > max_sentlen_threshold*2:
            sil = s.split() #  sentence in list
            l = len(sil)
            #print(s[:40], " length: ", l)
            split_n = determine_split_num(l, max_sentlen_threshold)
            sent_seg_idx = get_sent_seg_idx(l, split_n, offset=offset)
            assert split_n == len(sent_seg_idx), "splitted sentence number doesn't match {}, {}, {}".format(l, split_n, sent_seg_idx)
            for count, i in enumerate(sent_seg_idx):
                if count > 0 and sil[i[0]] in ("，","。","：","？","！","、","；"):
                    #print("this sentence was spitted at punct sign. ")
                    #print(sil[i[0]:(i[0]+20)])
                    assert offset == 0, "otherwise below logic needs to be changed"
                    splited_sentence_batch[-1] = splited_sentence_batch[-1] + " " + sil[i[0]]
                    sil[i[0]] = ""

                splited_sentence_batch.append(" ".join(sil[i[0]:i[1]]))
        else:
            splited_sentence_batch.append(s)
        for s in splited_sentence_batch:

            target = re.sub('——|--|__', 'C', s)
            target = re.sub('[^，。：？！、；\s\n]', 'C', target)
            target = re.sub('C (?=[，。：？！、；])', '', target)
            if re.search("CC|C，|C、|C。", target): continue
            source = re.sub('[，。：？！、；]', '', s)
            if len(source.split()) != len(target.split()):
                continue
            _ = h1.write(source+"\n")
            _ = h2.write(target+"\n")
        #print("count = ", count)
        #del tgt[:]

def generate_splited_file(filename, fname, partnumber=4):
    random.seed(hash(filename))
    tmp_name = str(random.randint(1, 99999))+fname
    cmd = "split -a 2 -d -n l/{} {} {}".format(partnumber, filename, tmp_name)
    os.system(cmd)
    tmp_namelist = ["{}{:02d}".format(tmp_name,i) for i in range(0, partnumber)]
    tmp_outnamelist_src = [i+".source" for i in tmp_namelist]
    tmp_outnamelist_tgt = [i+".target" for i in tmp_namelist]

    return tmp_namelist, tmp_outnamelist_src, tmp_outnamelist_tgt

def combine_files(tmp_list, origin_path, suffix):
    cmd = "cat {} > {}".format(" ".join(tmp_list), origin_path+suffix)
    #print(cmd)
    os.system(cmd)

def delete_tmp_file(alist):
    for f in alist:
        if os.path.exists(f):
            os.remove(f)
        else:
            print("The file {} does not exist, unable to delete it.".format(f))


if __name__ == '__main__':
    if len(sys.argv) == 2 :
        filepath=sys.argv[1]
    else :
        raise "Error, args = 1"
        sys.exit(1)
    workers = 32
    base = os.path.basename(filepath)
    fname = os.path.splitext(base)[0]
    tmp_namelist, tmp_outnamelist_src, tmp_outnamelist_tgt = generate_splited_file(filepath, fname, workers)
    print("file splitted")
    time.sleep(4)
    if workers > 1:
        with Pool(workers // 2) as p:
            p.map(process_single_file, tmp_namelist)
            combine_files(tmp_outnamelist_src, filepath, ".source")
            combine_files(tmp_outnamelist_tgt, filepath, ".target")
            delete_tmp_file(tmp_namelist)
            delete_tmp_file(tmp_outnamelist_src)
            delete_tmp_file(tmp_outnamelist_tgt)
    else:
        process_single_file(filepath)
