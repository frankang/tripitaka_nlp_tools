# -*- coding: utf-8 -*-
import re
import os
import sys
import random

filein = sys.argv[1]
fileout = open(filein + ".processed", "w+")


def dash(m):
    if random.randint(0,4) == 0:
        return m.group(0)+"\n"
    else:
        return m.group(0)


for line in open(filein, encoding="utf8", errors='replace'):
    line = line.strip()
    if len(line) == 0:continue
    line = re.sub(",", "，", line)
    line = re.sub("\?", "？", line)
    line = re.sub("\!", "！", line)
    line = re.sub(":", "：", line)
    line = re.sub("^(<p>|<juan>|<sec>)", "", line)
    line = re.sub("(?<=[。，！？：；、』」】”])<br>", "", line)
    if line.startswith("（"):
        line = re.sub("(?<=）)<br>$", "", line) #（《舊唐書》卷一百九十八《西戎．天竺國傳》5307）<br>
    if re.search("[。？！][(（]", line):
        line = re.sub("(?<=[）)])<br>$", "", line) #且坐毘城效一默。默，默，留與人天為軌則。(杜則林居士請叉手趺坐。)<br>

    line = re.sub("<br>", "。", line)
    #字产数据
    line = re.sub("(?<=[\u4e00-\u9ffff\d〉])(<sec>|<p>|<pin>)", "。", line)#太微南極長生大帝〈御前〉<sec>東極一詞。東極宮中大慈仁者太
    line = re.sub("(?<=[。，！？：；、』」】”])<sec>", "", line)
    line = re.sub("❥","□", line)
    line = re.sub("(?<=卷\d\d\d\d)全唐文", "", line)
    line = re.sub("((<p>|<sec>))", dash, line)
    line = re.sub("(<p>|<juan>|<pin>|<sec>)", "", line)

    #gxds
    line = re.sub("\u000d","",line)
    line = re.sub("^\u0040","",line)
    line = re.sub(r"(?<=[\u4e00-\u9ffff（）])[\s\u3000\t]+(?=[\u4e00-\u9ffff（）])","。", line)

    #line = re.sub("(?<=[。，！？：；、])[<p>|<br>|<sec>|<juan>|<pin>]", "", line)
    #局内括号
    #字体也让我喜欢（那是旧字形明体。）。
    #句外括号
    #前括号跟在标点（通常是句号）后；括号内通常为完整句子，可加任意标点；后括号后无需加标点。（我想句外括号的后括号）
    #line = re.sub("(?<![。，！？：；、])[<p>|<br>|<sec>|<juan>|<pin>]$", "。", line)
    #line = re.sub("(?<=[。，！？：；、）］〕】])[<p>|<br>|<sec>|<juan>|<pin>]", "", line)
    #line = re.sub("[<p>|<br>|<sec>|<juan>|<pin>](?<=[（［〔【])", "", line)
    #new_line = re.sub("(<p>)", "\g<1>\n", line)
    #for i in new_line:
    _ = fileout.write(line+"\n")
