# -- coding: UTF-8 --
# -*- coding: utf-8 -*-
import sys
import os
#import glob
import re
#import fnmatch
#import chardet
import unicodedata
from collections import defaultdict, OrderedDict
from collections import deque
from bs4 import BeautifulSoup, NavigableString, Tag
from multiprocessing import Pool


tup = ("，","。",".","？","?","」")
endpaddtern = tuple(list(u"，、；。：！？「」『』《》〈〉。，？“”；"))
discard_pattern = re.compile(u'凡例|題解|註解|備釋')
#file:///Users/soar/Documents/tripitaka/foguang/%E7%A6%AA%E8%97%8F/%E5%AE%97%E8%AB%96%E9%83%A8/%E4%BA%BA%E5%A4%A9%E7%9C%BC%E7%9B%AE%E5%A4%96%E5%8D%81%E4%B8%80%E9%83%A8/2CB001.htm
# def processFile(filecursor):



def clean_paragraph(text): #複[QM52]連而埽扌寮
    if 1. * text.count(u"闕")  / len(text.strip()) > 1./30 or text.count(u"闕") > 10 : return ""
    text = re.sub(ur"（闕）|（下闕）|（闕一字）|（上闕）|�|（頌缺）", u"❥", text)
    text = re.sub(ur"\[QM52\]", u"逯", text)
    text = re.sub(ur"扌寮", u"\U00022E18", text)
    text = re.sub(ur"氵自", u"洎", text)
    text = re.sub(ur"（一作.+?）","", text)
    text = re.sub(ur"（一無.+?）","", text)
    text = re.sub(ur"（疑作.+?）","", text)
    text = re.sub(ur"（謹按.+?）","", text) #yao
    text = re.sub(ur"（謹案.+?）","", text) #yao
    text = re.sub(ur"（疑一作.+?）","", text) #yao
    text = re.sub(ur"（其[一二三四五六七八九]）","", text) #yao
    text = re.sub(ur"(?<=（)原注：","", text)

    text = re.sub(ur"〈|〉","", text)

    if u"闕" in text:
        text = re.sub(ur"（闕三字）", u"❥❥❥", text)
        text = re.sub(ur"（闕二字）", u"❥❥", text)
        text = re.sub(ur"（闕四字）", u"❥❥❥❥", text)
        text = re.sub(ur"（闕五字）", u"❥❥❥❥❥", text)
        text = re.sub(ur"（闕六字）", u"❥❥❥❥❥❥", text)
        text = re.sub(ur"（闕.+?字）", u"❥❥❥❥❥❥❥❥❥❥", text)
    return text





def processFile(fileaddr):
    if os.path.getsize(fileaddr) < 1001: return #文件若太小则跳过
    #❥ ҈ ❣ ♡☙ ■￭∾҈这个符号用于替换未知字符



    if len(fileaddr) == 0 : 
        return #if no .txt file, skip

    #print fileaddr 
    
    with open(fileaddr) as f:
        raw_content = f.read()


        #raw_content = re.sub(ur"\[[^\]^\[]+?[@+-\/][^\]^\[]+?\]","❣", raw_content) #[p23]
        #all_p = BeautifulSoup(raw_content, 'lxml').find_all("p")
        all_p = BeautifulSoup(raw_content, 'lxml').find_all("p")

        # filter by content 
        if len(all_p) < 10: return #目前断定至少要10个才会有内容。。。

        
        #strings=defaultdict(lambda: [])


        parsed_contents = [] # well-format lines
        for i in all_p:
            ptext = i.get_text()

            if len(ptext) < 20: 
                continue
            else: 
                parsed_contents.append(clean_paragraph(ptext))




        saved_addr = fileaddr + ".out"
        out = open(saved_addr, "w+") 
        for i in parsed_contents:
            #print i
            out.write(i.encode("utf8")+"\n")

        out.close()







# main field
if __name__ == '__main__':
    if len(sys.argv)>1 :
        path=sys.argv[1]
    else :
        print "usage: preprocess.py dirname"
        sys.exit(1)
    print "building file lists..."
    # filelist = glob.glob(path+"/*")
    filelist = []
    for dirpath, dirnames, files in os.walk(path):
    	if "#" in dirpath and "阿含藏" not in dirpath: continue
        for file in files:
            if file.endswith('html'):
                filelist.append(os.path.join(dirpath, file))


    print "file lists built"
    


    # for item in filelist:
    # 	if os.path.getsize(item) < 1001: continue #文件若太小则跳过
    #     processFile(item)
    p = Pool(2)
    p.map(processFile, filelist)



