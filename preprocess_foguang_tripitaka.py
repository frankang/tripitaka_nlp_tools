# -- coding: UTF-8 --
# -*- coding: utf-8 -*-
import sys
import os
#import glob
import re
#import fnmatch
#import chardet
from collections import defaultdict, OrderedDict
from collections import deque
from bs4 import BeautifulSoup, NavigableString, Tag
from multiprocessing import Pool


tup = ("，","。",".","？","?","」")
endpaddtern = tuple(list(u"，、；。：！？「」『』《》〈〉。，？“”；"))
discard_pattern = re.compile(u'凡例|題解|註解|備釋')
#file:///Users/soar/Documents/tripitaka/foguang/%E7%A6%AA%E8%97%8F/%E5%AE%97%E8%AB%96%E9%83%A8/%E4%BA%BA%E5%A4%A9%E7%9C%BC%E7%9B%AE%E5%A4%96%E5%8D%81%E4%B8%80%E9%83%A8/2CB001.htm
# def processFile(filecursor):

def get_content(fileaddr):
    parsed_content = BeautifulSoup(open(fileaddr), 'lxml').find_all("tr")

    content = max(parsed_content, key=lambda item: len(item.get_text()))
    return content

def get_text(tags, attributes={}):
    
    for tag in tags:
        attr = attributes.copy()
        #print tag
        if isinstance(tag, Tag) and tag.name == "font":
            attr.update(tag.attrs)

        if isinstance(tag, Tag) and tag.name == "br":
            strings[hash(tuple(attr.items()))].append(6885077) #一个数字，用来代表换行
            continue

        if isinstance(tag, NavigableString):
            #print attr, tag
            strings[hash(tuple(attr.items()))].append(tag)
            continue

        sub_tags = tag.contents
        if not sub_tags: 
            continue
        else:
            get_text(sub_tags, attributes=attr)

def check_ratio(a_dict):
    keys = []
    for key, values in a_dict.iteritems():
        signs = 0
        words = 0
        for i in values:
            if i == 6885077: continue
            cleaned = i.strip()
            words = words + len(cleaned)
            signs = signs + cleaned.count(u"，") + cleaned.count(u"。") + cleaned.count(u"？")

        if words == 0: 
            keys.append(key)
            continue
        if 1. * signs / words < 1./20: keys.append(key)

    return keys


def processFile(fileaddr):
    if os.path.getsize(fileaddr) < 1001: return #文件若太小则跳过
    #❥ ҈ ❣ ♡☙ ■￭∾҈这个符号用于替换未知字符
    def get_text(tags, attributes=OrderedDict()):
    
        for tag in tags:
            attr = attributes.copy()
            #print tag
            if isinstance(tag, Tag) and tag.name == "font":
                attr.update(tag.attrs)

            if isinstance(tag, Tag) and tag.name == "br":
                for key, values in strings.iteritems():
                    values.append(6885077)
                #strings[hash(tuple(attr.items()))].append(6885077) #一个数字，用来代表换行
                continue

            if isinstance(tag, NavigableString):
                #print attr, tag
                #print attr.items()
                strings[hash(tuple(attr.items()))].append(tag)
                continue

            sub_tags = tag.contents
            if not sub_tags: 
                continue
            else:
                get_text(sub_tags, attributes=attr)


    if len(fileaddr) == 0 : 
        return #if no .txt file, skip

    #print fileaddr 
    
    with open(fileaddr) as f:
        raw_content = f.read()


        #raw_content = re.sub(ur"\[[^\]^\[]+?[@+-\/][^\]^\[]+?\]","❣", raw_content) #[p23]
        parsed_content = BeautifulSoup(raw_content, 'lxml').find_all("tr")

        # filter by content 
        if len(parsed_content) < 4: return #目前断定至少要4个才会有内容。。。
        for tag in parsed_content[0:4]: #discard 凡例|題解|註解|備釋 in titles
            #print tag.get_text()
            if discard_pattern.search(tag.get_text()): 
                #print "matched" 
                return
        saved_addr = fileaddr + ".out"
        out = open(saved_addr, "w+") 
        # get longest tr element, which is the text
        content = max(parsed_content, key=lambda item: len(item.get_text()))


        anchors = content.findAll('a') 
        for anchor in anchors:
            # anchor.replace_with("") #remove all links
            anchor.unwrap() #remove all links
        anchors = content.findAll('sup') #remove all link parent
        for anchor in anchors:
            # anchor.replace_with("")
            anchor.unwrap()
        anchors = content.findAll('b')     #remove all bold style
        for anchor in anchors:
            anchor.unwrap()

        
        strings = defaultdict(lambda: [])
        #stop = False
        get_text(content)
        for key, values in strings.iteritems(): # 保险起见，为配合后面逻辑，最后再加一个br
            values.append(6885077)
       
        # delete content which has a low content:mark ratio
        keys_to_delete = check_ratio(strings)
        for key in keys_to_delete: del(strings[key])

        parsed_contents = [] # well-format lines
        for key, value in strings.iteritems():
            one_sent = ""
            parsed_contents.append("\n")
            for i in value:
                #print i
                if i == 6885077:
                    if len(one_sent.strip()) == 0 : 
                        one_sent = ""
                        continue
                    one_sent = re.sub(ur"\?(?!$)", u"❥", one_sent.strip())
                    one_sent = re.sub(ur"\[p\d+\]","", one_sent) #[p23]
                    one_sent = re.sub(ur"\(\d+\)","", one_sent) # (23)
                    one_sent = re.sub(ur"\[[^\]^\[]{1,6}?[@+\/-][^\]^\[]{1,6}?\]",u"❣", one_sent) #[p23]
                    if one_sent == "" : continue
                    if not one_sent.endswith(endpaddtern):
                        one_sent += u'，'#TODO ,是改成全角逗号还是句号？
                    parsed_contents.append(one_sent)
                    one_sent = ""
                    continue
                else:
                    clean_sent = i.strip()
                    clean_sent = re.sub(ur"\t+", u"\t", clean_sent)
                    clean_sent = re.sub(ur"\s+", u" ", clean_sent)
                    clean_sent = re.sub(ur"\s\t", u"\t", clean_sent)
                    clean_sent = re.sub(ur"\t\s", u"\t", clean_sent)
                    #TODO 把中文字之间的标点保留，但是不保留和标点连接的空格？
                    one_sent = one_sent + clean_sent

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
            if file.endswith('htm'):
            	if "-" in file and "阿含藏" not in dirpath: continue
            	if file.lower().endswith(("b.htm","d.htm","e.htm","f.htm","r.htm")): continue
                filelist.append(os.path.join(dirpath, file))


    print "file lists built"
    


    # for item in filelist:
    # 	if os.path.getsize(item) < 1001: continue #文件若太小则跳过
    #     processFile(item)
    p = Pool(2)
    p.map(processFile, filelist)



