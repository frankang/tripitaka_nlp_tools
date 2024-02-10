import sys
import re
import random
filein = sys.argv[1]
fileout = open(filein + ".splitted", "w+")

def dash(m):
    if random.randint(0,4) == 0:
        return m.group(0)+"\n"
    else:
        return m.group(0)
def dash1(m):
    if random.randint(0,10) == 0:
        return m.group(0)+"\n"
    else:
        return m.group(0)
for line in open(filein):
    line = line.strip()
    if len(line) == 0:continue
    #new_line = re.sub("([。！？])", "\g<1>\n",line)
    new_line = re.sub("([。！？])", dash, line)
    new_line = re.sub("([:：；])", dash1, new_line)
    #for i in new_line:
    _ = fileout.write(new_line)

