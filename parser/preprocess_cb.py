# -- coding: UTF-8 --
# -*- coding: utf-8 -*-
import sys
import os
import glob
import re
from collections import OrderedDict, defaultdict

#class OrderedDefaultDict(OrderedDict, defaultdict):
#    def __init__(self, default_factory=None, *args, **kwargs):
#        #in python3 you can omit the args to super
#        super(OrderedDefaultDict, self).__init__(*args, **kwargs)
#        self.default_factory = default_factory

# for multi processes
from multiprocessing import Pool

tup  =  ("，","。",".","？","?","」","：","』")

# def processFile(filecursor):
def processFile(fileaddr):
    if os.path.getsize(fileaddr) < 1001: return #文件若太小则跳过
    #❥ ҈ ❣ ♡☙ ■￭∾҈这个符号用于替换未知字符

    if len(fileaddr) == 0 : 
        return #if no .txt file, skip

    # try: 
    #print fileaddr 
    with open(fileaddr) as f :
        contents = defaultdict(list)
        lines = f.read()
        lines = lines.lower()
        if len(lines) < 4200: 
            print("skipping short file ", fileaddr)
            return
        # article_word_counts_median = len(lines) /2
        # if lines[article_word_counts_median:article_word_counts_median+900].count("。") < 15: return
        if lines[:2000].count("□") > 20:
            print("#abc skipping file:  ", fileaddr)
        if lines[:2000].count("。") < 5 or lines[:2000].count("，") < 5: 
            print("#bcd skipping file: ", fileaddr)
            return #ignore no mark file
        if lines[-2000:].count("。") < 5 or lines[:2000].count("，") < 5: 
            print("#cdf skipping file: ", fileaddr)
            return #ignore no mark file
        #lines = re.sub(r'\[([^;]*);[^\] ]{0,20}?\]','\\1', lines) #[䠒跪;胡跪]
        lines = re.sub(r"\[\d+\]", "", lines) #性性空聖性[05]聖智為首
        lines = re.sub(r"\[＊\]", "", lines) #[*]
        lines = re.sub("<mj \d{0,5}>", "", lines) #[*] <mj 006>,卷分界
        lines = re.sub(r"<j>|<t>|<u>", "", lines) #[*]
        lines = re.sub(r"<t,0,1>", "，", lines) #[*]
        #lines = re.sub(r'◎','',lines)
        #lines = re.sub(r'<\w{0,10}?>','',lines)
        lines = re.sub(r'\[\d+[a-z]{0,10}?\]','',lines) #heritage
        #lines = re.sub(r'□',u'❥',lines) #heritage 不主动替换unk

        #lines = re.sub(r"\[[^\]^\[]{1,8}?[@+*\/-][^\]^\[]{1,8}?\]","❣", lines) #[p23]
        lines = re.sub(r"\[[^\]^\[]{0,20}?>(.*?)\]", "\\1", lines) #[却>劫]
        lines = lines.split("\n")

        grouped_lines = filter_and_add_contents(lines, contents)
        process_article(fileaddr, grouped_lines)

def filter_and_add_contents(lines, contents):
    printed = False
    for line in lines:
        if len(line) < 10: continue
        if line[8] != "_": #ZW08n0067_p0021a07_
            raise f"the 8th position isn't _, line content {line}"
            if not printed:
                print(line)
                printed = True
            continue
        article = line[0:8]
        line_type = line[17:20]
        line_content = line[20:]
        if len(line_content) == 0: continue
        if line_content[0] == "#":
            if not printed: 
                print(line)
                printed = True
            continue
        contents[article].append((line_type, line_content))

    return contents


def process_article(fileaddr, contents):
    saved_addr = fileaddr + ".out"
    h = open(saved_addr,"w+")
    for key, items in contents.items():
        if len(items) < 20 : continue
        #saved_addr = fileaddr + "."+ key + ".out"
        # h = open(saved_addr,"w+")
        i = 0
        first_s = False
        one_article_content = []
        for j, line in enumerate(items):
            if not first_s and line[0][0] == "s": 
                first_s = True
                one_article_content.append(items[i:j])
                i = j


            if line[0][0] != "_":
                if first_s and line[0][0] == "s": 
                    continue

                one_article_content.append(items[i:j])
                i = j
                first_s = False

        i = None

        for index, i in enumerate(one_article_content):
            if len(i) == 0: continue
            if i[0][0][0] not in "pvs": continue
            if i[0][0][0] in "pv":
                if len(i) == 1 and i[0][0][0] == "p" \
                and index < len(one_article_content)-1 \
                and one_article_content[index+1][0][0][0] == "p":
                    continue

                complete_sent = "".join(j[1] for j in i)
                complete_sents=re.split(r"<p>|<z>|<p,1>", complete_sent)
                for j in complete_sents:
                    #if not j.endswith(tup):
                    #    j = j + "。"
                    j = re.sub(r"(?<=[\u4e00-\u9fff])[\s\u3000\t]+(?=[\u4e00-\u9fff])","，", j)
                    j = re.sub(r"[\s\u3000\t]+","", j)
                    h.write(j+"\n")


            if i[0][0][0] == "s":
                def add_period(sent):
                    return sent+"，" if not sent.endswith(tup) else sent
                
                complete_sent = "".join(add_period(j[1]) for j in i)
                complete_sent = re.sub(r"(?<=[\u4e00-\u9fff])[\t\s\u3000]+(?=[\u4e00-\u9fff])","，",complete_sent)
                complete_sent = re.sub(r"[\s\u3000\t]+","",complete_sent)
                h.write(complete_sent+"\n")

    h.close()#sys.exit(0)




def split_by_article(lines):

    uniformity = False
    if lines[2].find("_",6,13) == lines[-2].find("_",6,13):
        uniformity = True
    else:
        print("malform text!!!!!\n","file content is \n", lines[2])
        print("need to use reg to extract the id for each line")
    #assert uniformity

    id_end_pos = lines[2].find("_",6,13) 
    id_start_pos = lines[2].find("_",6,13) -4

    # temp_grouped_content = defaultdict(lambda: [])
    temp_grouped_content = defaultdict(lambda: deque())
    sent_start_pos = None
    sent_type = None
    sent_content  = None
    for line in lines:
        id_ = line[id_start_pos:id_end_pos]
        sent_start_pos = line.find("#",14,23) + 1
        if sent_start_pos == 0:
            continue
        sent_type = line[sent_start_pos-2]
        try:
            while line[sent_start_pos] in ("#","1","2","3","4","5","6","k","l"):
                sent_start_pos += 1
        except Exception as e:
            #raise e
            continue

        sent_content = line[sent_start_pos:] 
        temp_grouped_content[id_].append(\
            [sent_type, sent_content])


    return temp_grouped_content

def remove_no_xb_article(grouped):
    temp_list = []
    for k in grouped:
        num_delimitation = 0 #full-width comma ，

        for sent in grouped[k]:
            num_delimitation += sent[1].count("，")

        if num_delimitation < 20:
            temp_list.append(k)

    for i in temp_list:
        grouped.pop(i,None)

    return grouped


def process_line(l_type,l_content):#l = line
    if l_type == "_":
        return process_normal_line(l_content)
#
    elif l_type == "p":
        return "p" + process_normal_line(l_content)

    elif l_type == "s":
        return process_chant_line(l_content)

    elif l_type == "q":
        return  "p"+process_normal_line(l_content)+"p"
    elif l_type == "v":
        return  "p"+process_normal_line(l_content)+"p"
    elif l_type == "d":#T14n0425_p0004c13D##行品第二
        return  "p"+process_normal_line(l_content)+"p"
    elif l_type  == "j":#卷的开头和结束

        return ""
    elif l_type  == "a":#author
        return ""  
    elif l_type  == "n":#number
        return ""  
    elif l_type  == "y":#yizhe
        return ""  
    else:
        return ""

#todo remove ◎,[12]在最开始的时候
def process_normal_line(l_content):
    #todo 现在会吧行末的换行去除，开头和结束的只会保留结束的换行符
    l_content = re.sub('<p.*?>','p',l_content)
    l_content = re.sub('<l.*?>','，',l_content)
    #l_content = re.sub('<p[^>]+>', 'p','l_content')
    l_content = re.sub('\[.*?\+.*?\]', '□',l_content) #[]把含有 +的[]换成□
    l_content = re.sub('\[\d+[a-z]?\]', '',l_content) # 去掉校勘註標, 例 [01], [02A]
    #l_content = re.sub('\[([^; ]*);[^\] ]*\]','\\1',l_content) #[䠒跪;胡跪]
    l_content = re.sub("\[(?:\[[^\]]+\]|[^\[\]])*>((?:\[[^\]]+\]|[^\[\]])*)\]",'\\1',l_content) #[A>B]
    l_content = re.sub('<[^>]+>', '',l_content)
    l_content = re.sub('(（【◇】）|\(【◇】\)|【◇】|（◇）|◇)+', '【◇】',l_content)
    return l_content

def process_chant_line(line):
    
    splitted_line  =  line.split()
    for i in range(len(splitted_line)):
        if not splitted_line[i].endswith(tup):
            splitted_line[i]  =  splitted_line[i]+"，"
    return process_normal_line("".join(splitted_line))

def checkEncoding(content):
    return chardet.detect(content[:700])["encoding"]


if __name__ == '__main__':
    if len(sys.argv)>1 :
        path=sys.argv[1]
    else :
        print("usage: preprocess.py dirname")
        sys.exit(1)
    print("building file lists...")
    # filelist = glob.glob(path+"/*")
    filelist = []
    for root, dirs, files in os.walk(path):
        for file in files:
            if file.endswith('new.txt'):
                 filelist.append(os.path.join(root, file))
    print("file lists built")
    # print "init language detector ..."
    # file_extension = "/*.[Tt][Xx][Tt]"

    # # connect to the mongo database and open the corresponding collection
    # print "connecting to Mongo Database"
    # client = MongoClient()
    # db = client.sutradb
    # sutra_file_info = db.sutra_file_info_collection

    # # if folder name/(movie info) is not in the database, then add it into the DB
    # print "updating Database"
    # for file in filelist:
    #     fileid = file.split('/')[-1]
    #     if not sutra_file_info.find_one({"_id": fileid}):
    #         sutra_file_info.insert_one({"_id": fileid, "finished": False,"address": file}) #"no_en_subtitle": False})


    # print "getting unfinished file paths"
    unfinished_file_list = []
    # for cursor in sutra_file_info.find({"finished":False}):
    #     unfinished_file_list.append(cursor)
    unfinished_file_list = filelist
    workers = 16
    print("starting process files, the default process number is {}".format(workers))
    p = Pool(16)
    print("i am here!!before mapping")
    p.map(processFile, unfinished_file_list)
    for item in unfinished_file_list:
        processFile(item)
    #p.map(processFile, unfinished_file_list)

