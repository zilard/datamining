#!/usr/bin/python

from datetime import datetime
from itertools import islice
import time
import subprocess
import os
import re
import sys


BUDDYINFO_CMD = "cat interrupts"
BUDDYINFO_CSV = "buddyinfo.csv"

SLEEP_TIME = 1


def parse(printout):
    parsed_list = []
    parsed = []
    for l in printout.strip().splitlines():
        parsed = []

        cluttered = [e.strip() for e in l.split(' ')]

        for p in cluttered:
            if p:
                parsed.append(p)
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




def buddyinfo_parse(parse_cmd):
    res = []
    r = parse(exec_cmd(parse_cmd))

    return r




def main():
 

    res = buddyinfo_parse(BUDDYINFO_CMD)


    print("%5s %10s %10s %10s %10s" % (" ", res[0][26], res[0][33], res[0][66], res[0][73]))          
    for r in res[1:-20]:
        if sum(map(int, [r[27], r[34], r[67], r[74]])) != 0:
            print("%5s %10s %10s %10s %10s %s %s %s" % (r[0], r[27], r[34], r[67], r[74], r[81], r[82], r[83])) 




if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        sys.exit(0)


