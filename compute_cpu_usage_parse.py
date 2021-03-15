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


#COMPUTE_FILE = "collect_20210217_174103.log"             # 1.
#CPU_USAGE_CSV = "compute_cpu_usage_174103.csv"           # 1.

COMPUTE_FILE = "host-collect-cpu.log_20210218_083526"     # 2.
CPU_USAGE_CSV = "compute_cpu_usage_083526.csv"            # 2.

CPU_WATCH_LIST = ['26', '33', '66', '73']


CPU_IDX = 3
#CPU_USAGE_IDX = 6                 # 1.
CPU_USAGE_IDX = 10                 # 2.


def datacrunch():

    date_start = "____DATE"
    ps_start = "____PS_THREADS"
    
    #ps_end = "____MPSTAT"         # 1.
    ps_end = "____IOSTAT"          # 2.


    cpu_list = []
    cpu_usage_list = []
    cpu_usage_dict = {}


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
                        for cpu in CPU_WATCH_LIST:
                            cpu_usage_list.append("%.2f" % cpu_usage_dict[cpu])
                        date = ""
                        cpu_list.append(cpu_usage_list)
                        cpu_usage_list = []
                        cpu_usage_dict = {}               


                    if ps_rec_started:
                        ps_line = parse(line.rstrip('\n'))
                        #print("%s" % ps_line)
                        cpu = ps_line[CPU_IDX]
                        if cpu in CPU_WATCH_LIST:
                            cpu_usage = float(ps_line[CPU_USAGE_IDX])

                            if cpu_usage > 0.0:
                                if cpu in cpu_usage_dict:
                                    cpu_usage_dict[cpu] += cpu_usage
                                else:
                                    cpu_usage_dict[cpu] = cpu_usage
                            

                    if ps_start in line:
                        ps_rec_started = True
                        cpu_usage_list = [date]
             
          
            else:
                break



    i = 0
    with open(CPU_USAGE_CSV, 'w') as f:
        for cpu_usage_list in cpu_list:
            f.write("%s\n" % ','.join(
                                      [ 
                                        str(i) 
                                      ] +
                                      cpu_usage_list
                                     ))
            i += 1
 



def main():
    datacrunch()


if __name__ == '__main__':
    main()


