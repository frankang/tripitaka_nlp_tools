# -*- coding: utf-8 -*-
import codecs
import random
import sys
import re
import unicodedata
import random
import os
from multiprocessing import Pool
import time

def is_han(uchar):
        """判断一个unicode是否是汉字"""
        #if uchar >= '\u2e80' and uchar<='\u9fff':
        if '\u2762'< uchar <'\U000fffff':
                return True
        else:
                return False
def normalize(text, mode = 'NFKC', ignore = ''):
    #from __future__ import unicode_literals
    '''
    https://github.com/ikegami-yukino/jaconv/blob/master/jaconv/jaconv.py
    '''
    text = text.replace('〜', 'ー').replace('～', 'ー')
    text = text.replace('―', ' - ').replace('‐', ' - ').replace('˗', ' - ').replace('֊', ' - ')
    text = text.replace('‐', ' - ').replace('‑', ' - ').replace('‒', ' - ').replace('–', ' - ')
    text = text.replace('⁃', ' - ').replace('⁻', ' - ').replace('₋', ' - ').replace('−', ' - ')
    text = text.replace('﹣', 'ー').replace('－', 'ー').replace('―', 'ー')
    text = text.replace('━', 'ー').replace('─', 'ー')
    #return unicodedata.normalize(mode, text)
    return text

def generate_splited_file(filename, fname, partnumber=4):
    random.seed(hash(filename))
    tmp_name = str(random.randint(1, 99999))+fname
    cmd = "split -a 2 -d -n l/{} {} {}".format(partnumber, filename, tmp_name)
    os.system(cmd)
    tmp_namelist = ["{}{:02d}".format(tmp_name,i) for i in range(0, partnumber)]
    tmp_outnamelist = [i+".padded" for i in tmp_namelist]

    return tmp_namelist, tmp_outnamelist
#TODO【，皇甫谧作，见刘昭注补后汉郡国志。】
def process_single_file(filepath):
    s   = open(filepath).read()
    ##s = " ".join(s.split())
    ##
    #s = normalize(s.lower().decode("utf8"))
    s = normalize(s)
    s = re.sub("■","￭", s)
    s = re.sub("\u200b|\u000b|\u00A0|\u2029|\u2028|\ufeff"," ", s)
    s = re.sub('。+','。',s)
    s = re.sub('，+','，',s)
    s = re.sub('(，|。|？|”|“|’|‘|；|：|》|《|（|）|、|□|※|>|◎|○|●|⊙|‖|‡|▭|▧|∩|∪|×|│|△|≡|◇|◆|·|★)',' \\1 ',s)
    s = re.sub('[˗֊‐‑‒–⁃⁻₋−]+', '-', s)  # normalize hyphens
    s = re.sub('-{2,}', ' -- ', s)  # normalize hyphens
    s = re.sub('—+', ' ——  ', s)  # 破折号————
    #s = re.sub('—{3,}', ' -- ', s)  # 破折号————
    s = re.sub('[﹣－ｰ―─━ー]+', 'ー', s)  # normalize choonpus
    #s = re.sub('[~∼∾〜〰～]', '', s)  # remove tildes
    #s = re.sub(u"(?<=[\u4e00-\u9fff])[\t \u3000]+(?=[\u4e00-\u9fff])",u" , ", s) #han之间空格变成，
    s = re.sub("(?<=[a-z0-9\u2762-\u9ffff])-(?=[a-zA-Z0-9\u2762-\u9ffff])"," - ", s)
    s = re.sub('\.\.\.+','...',s)
    s = re.sub('([!#$%&()*+,\/:;\[\]=?@^`{|}~…])',' \\1 ',s)
    #< _ > -rmed hyphenation is handled to bpe
    s = re.sub('`  `','``',s)
    s = re.sub('(\'\'|``|…|\")','  \\1 ',s)
    # pending
    #s = re.sub(ur"(?<=[ ])-(?=[0-9\u2762-\u9ffff])",r"- ", s)#顺序很重要
    print("begin substituting numbers")
    s = re.sub('(\d)',' \\1 ',s)
    print("begin substituting han characters")
    s = re.sub('([\u2630-\U000fffff])',' \\1 ',s)
    s = re.sub('([\u0000-\u0009])','',s)
    s = re.sub('[ \u3000]+',' ',s) #remove double spaces
    #sys.exit()
    # replacement
    
    with open(filepath+'.padded','w+') as saving_file:
        _=saving_file.write(s)
    print("done! "+filepath)

def combine_files(tmp_list, origin_path):
    cmd = "cat {} > {}".format(" ".join(tmp_list), origin_path+".padded")
    print(cmd)
    os.system(cmd)

def delete_tmp_file(alist):
    for f in alist:
        if os.path.exists(f):
            os.remove(f)
        else:
            print("The file {} does not exist, unable to delete it.".format(f))
    print("File removed.")

if __name__ == '__main__':
    if len(sys.argv) == 3 :
        filepath=sys.argv[1]
        lang=sys.argv[2]
    else :
        print("usage: python add_space.py filepath language-type('zh', etc.)")
        sys.exit(1)
    workers = 16
    base = os.path.basename(filepath)
    fname = os.path.splitext(base)[0]
    tmp_namelist, tmp_outnamelist = generate_splited_file(filepath, fname, workers)
    print("file splitted")
    time.sleep(6)
    if workers > 1:
        with Pool(workers // 2) as p:
            p.map(process_single_file, tmp_namelist)
            combine_files(tmp_outnamelist, filepath)
            delete_tmp_file(tmp_namelist)
            delete_tmp_file(tmp_outnamelist)
    else:
        process_single_file(filepath)

