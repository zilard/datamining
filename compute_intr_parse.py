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

VM_FILE = "collect_20210216_084220.log"
INTR_CSV = "compute_intr_084220.csv"

INTR_LIST = [640, 647, 660, 667, 681, 684, 695, 698]



def ll_sp_value(value1, value2, itv):
    if ((value2 < value1) and (int(value1) <= 0xffffffff)):
        return (float(int(value2 - value1) & 0xffffffff) / itv) * 100
    else:
        return ((value2 - value1) / itv) * 100



def datacrunch():

    date_start = "____DATE"
    procstat_start = "____PROC_STAT"

    intr_list = []
    intr_diff_list = []

    date_rec_started = False
    date_lineno = 0
    date_maxline = 2

    procstat_rec_started = False
    procstat_lineno = 0
    procstat_maxline = 83

    date = ""

    procstat_dict = {}

    prev_date = ""


    p_intr_list = []



    with open(VM_FILE, 'r') as f:
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
                  


                if procstat_start in line:
                    procstat_rec_started = True

                    if prev_date:
                        intr_diff_list = [prev_date]
                    prev_date = date

            
                if procstat_rec_started:
                    procstat_lineno += 1

                    if procstat_lineno == 83:

                        c_intr_list = []

                        irq_line = parse(line.rstrip('\n')) 
 
                        #print("IRQ_LINE %s" % irq_line)

                        for intr in INTR_LIST:
                            c_intr_list.append(irq_line[intr+2])                    
                       
                        #print("INTR_LIST %s" % c_intr_list)


                        if p_intr_list:
                            print("PREV: %s" % p_intr_list)
                            print("CURR: %s\n" % c_intr_list)

                            for idx in range(len(c_intr_list)):
                                intr_diff_list.append(str(int(c_intr_list[idx]) - int(p_intr_list[idx])))
           
 
                        p_intr_list = c_intr_list


                        if procstat_lineno == procstat_maxline:
                            procstat_rec_started = False
                            procstat_lineno = 0
                            if intr_diff_list:
                                intr_list.append(intr_diff_list)
                            intr_diff_list = []

            else:
                break


    i = 0
    with open(INTR_CSV, 'w') as f:
        for intr_diff_list in intr_list:
            #i = procstat_list.index(procstat)
            #print("___i %s" % i)
            #print("%s\n" % procstat)
            
            f.write("%s\n" % ','.join(
                                      [ 
                                        str(i) 
                                      ] +
                                      intr_diff_list
                                     ))
            i += 1
 



def main():
    datacrunch()


if __name__ == '__main__':
    main()

