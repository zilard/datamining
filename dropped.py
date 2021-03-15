#!/usr/bin/python

from datetime import datetime
from itertools import islice
import time
import subprocess
import os
import re
import sys


BUDDYINFO_CMD = "cat ovs_pmd_stat.log"
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

    prev = [] 

    res = buddyinfo_parse(BUDDYINFO_CMD)

    date = ""

    for line in res:

        if "2021-01-29" in line:
            #print("LINE %s" % line)
            date = ' '.join([line[0], line[1]])
       
        if "TX" in line:

            #pkt = line[1].split(':')
            drp = line[3].split(':')

            if drp[0] == "dropped":
                dropped = int(drp[1])
                if dropped != 0:
                    if prev:
                        prev_date = prev[0]
                        prev_dropped = prev[1]
                        if dropped > prev_dropped:
                            print("Timeframe: %s - %s  dropped: %s" % (prev_date, date, (dropped - prev_dropped))) 
                    prev = [date, dropped]


        """
        if prev:

           cur_time = ' '.join([line[3], line[4], line[5], line[7]])
           prev_time = ' '.join([prev[3], prev[4], prev[5], prev[7]])
 
           cur_time = datetime.strptime(cur_time,'%b %d %H:%M:%S %Y')
           prev_time = datetime.strptime(prev_time,'%b %d %H:%M:%S %Y')

           diff = int((cur_time - prev_time).total_seconds())

           if diff > 1:
               print("%-8s %s" % ("PREV:", prev_time))
               print("%-8s %s" % ("CURRENT:", cur_time))
               print("%-8s %s\n" %  ("DIFF:", diff))     
 
        prev = line

        """




if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        sys.exit(0)


