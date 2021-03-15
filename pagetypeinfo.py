#!/usr/bin/python

from datetime import datetime
from itertools import islice
import time
import subprocess
import os
import re
import sys


PAGETYPEINFO_CMD = "cat /proc/pagetypeinfo"
PAGETYPEINFO_CSV = "pagetypeinfo.csv"

SLEEP_TIME = 1

TYPE = ['Unmovable', 'Movable', 'Reclaimable']
NUMA = ['0', '1']
ZONETYPE = ['Normal']



def parse(printout):
    parsed_list = []
    parsed = []
    for l in printout.strip().splitlines():
        parsed = []

        cluttered = [e.strip() for e in l.split(' ')]

        for p in cluttered:
            if p:
                parsed.append(p.rstrip(','))
        if len(parsed):
            parsed_list.append(parsed)
    return parsed if len(parsed_list) == 1 else parsed_list




def exec_cmd(cmd, check=False):
    nul_f = open(os.devnull, 'w')
    process = subprocess.Popen(cmd,
                               stdout=subprocess.PIPE,
                               stderr=nul_f,
                               shell=True)
    nul_f.close()
    response = process.communicate()[0].strip()
    return response




def pagetypeinfo_parse(parse_cmd):
    res = []
    r = parse(exec_cmd(parse_cmd))

    for line in r:

        #print("LINE: %s" % line)

        if len(line) == 17:

            if line[0] == "Node":

                if ((line[4] == "type") and
                    (line[1] in NUMA) and
                    (line[3] in ZONETYPE) and
                    (line[5] in TYPE)):

                    res = res + line[6:]

    #print("%s" % res)

    return sum(map(int, res)), res




def main():
 
    prev = 0
    idx = 0
   
    with open(PAGETYPEINFO_CSV, 'w') as f:

        while True:
            now = datetime.now()
            date = now.strftime('%Y%m%d%H%M%S')

            sumres, res = pagetypeinfo_parse(PAGETYPEINFO_CMD)
           
            #print("RES %s\n" % res)

            if sumres != prev:
               prev = sumres
               idx += 1
             
               print("%s\n" % res)

               f.write("%s\n" % ','.join([
                                          str(idx),
                                          date
                                         ] +
                                         res
                                        ))

            time.sleep(SLEEP_TIME)


if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        sys.exit(0)


