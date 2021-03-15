#!/usr/bin/python

from datetime import datetime
from itertools import islice
import time
import subprocess
import os
import re
import sys


BUDDYINFO_CMD = "cat host-collect-cpu.log_20210209_102918"
BUDDYINFO_CSV = "buddyinfo.csv"

SLEEP_TIME = 1


COMPUTE_FILE = "host-collect-cpu.log_20210209_102918"



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


def parse_simple(printout):
    parsed_list = []
    parsed = []
    for l in printout.strip().splitlines():
        parsed_list.append(l)

    return parsed_list





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
    r = parse_simple(exec_cmd(parse_cmd))

    return r



SEARCH = "____PS_THREADS"
END_SEARCH = "____"            # ____IOSTAT

OCCURENCE = 4


def main():

    collect_lines = [] 

    start_rec = False

    #res = buddyinfo_parse(BUDDYINFO_CMD)

    occ = 0

    with open(COMPUTE_FILE, 'r') as f:
        while True:
            line = f.readline()
            if line:
 
                line = line.rstrip('\n')

                if (start_rec and (END_SEARCH in line)):
                    start_rec = False
                    break

                if start_rec:
                    collect_lines.append(line)

                if SEARCH in line:
                    occ += 1

                if occ == OCCURENCE:
                    start_rec = True
   


    for line in collect_lines:
        print("%s" % line)



    
   

if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        sys.exit(0)



