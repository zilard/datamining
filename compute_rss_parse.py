#!/usr/bin/python

from itertools import islice
import time
import subprocess
import os
import re

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



COMPUTE_FILE = "host-collect-cpu.log_20210209_102918"
RSS_CSV = "compute_qemu_rss_102918.csv"

CPU_WATCH_LIST = ['26', '33', '66', '73']

QEMU_PID_WATCH_LIST = ['63982']


PID_IDX = 0
SPID_IDX = 1
CPU_IDX = 3
RSS_IDX = 6


def datacrunch():

    date_start = "____DATE"
    ps_start = "____PS_THREADS"
    ps_end = "____IOSTAT"


    cpu_list = []
    cpu_usage_list = []
    cpu_usage_dict = {}


    rss_list = []
    rss_usage_list = []
    rss_usage_dict = {}



    date_rec_started = False
    date_lineno = 0
    date_maxline = 2

    ps_rec_started = False
    ps_lineno = 0

    date = ""


    with open(COMPUTE_FILE, 'r') as f:
        while True:
            line = f.readline()
            if line:

                if date_start in line:
                    date = ""
                    date_rec_started = True
                
                if date_rec_started:
                    date_lineno += 1

                    if date_lineno == date_maxline:
	                date = line.rstrip('\n').split('.')[0]
                        date_rec_started = False
                        date_lineno = 0

                if date:

                    if (ps_rec_started and (ps_end in line)):
                        ps_rec_started = False
                        for pid in QEMU_PID_WATCH_LIST:
                            rss_usage_list.append("%d" % rss_usage_dict[pid])
                        date = ""
                        rss_list.append(rss_usage_list)
                        rss_usage_list = []
                        rss_usage_dict = {}               


                    if ps_rec_started:

                        if "qemu-system-x86_64" in line:
                            ps_line = parse(line.rstrip('\n'))
                            pid = ps_line[PID_IDX]  
                            spid = ps_line[SPID_IDX] 

                            if pid in QEMU_PID_WATCH_LIST and pid == spid:
                                rss = int(ps_line[RSS_IDX])
                                rss_usage_dict[pid] = rss 
                          

                    if ps_start in line:
                        ps_rec_started = True
                        rss_usage_list = [date]
             
          
            else:
                break



    with open(RSS_CSV, 'w') as f:
        for rss_usage_list in rss_list:
            f.write("%s\n" % ','.join(
                                      rss_usage_list
                                     ))
 



def main():
    datacrunch()


if __name__ == '__main__':
    main()

