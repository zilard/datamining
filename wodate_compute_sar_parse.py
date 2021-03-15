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

VM_FILE = "collect.log"
SAR_CSV = "wodate_compute_sar.csv"

CPU_LIST = ['26', '33', '66', '73']



def datacrunch():

    date_start = "____DATE"
    sar_start = "____SAR"

    sar = []
    sar_list = []


    date_rec_started = False
    date_lineno = 0
    date_maxline = 2

    sar_rec_started = False
    sar_lineno = 0
    sar_maxline = 85

    date = ""




    with open(VM_FILE, 'r') as f:
        while True:
            line = f.readline()
            if line:


                """
                if date_start in line:
                    date = ""
                    date_rec_started = True
                
                if date_rec_started:
                    date_lineno += 1

                    if date_lineno == date_maxline:
	                date = line.rstrip('\n')
                        date_rec_started = False
                        date_lineno = 0
                """
                  


                if sar_start in line:
                    sar_rec_started = True
                    sar = []
                    #sar = [date]

            
                if sar_rec_started:
                    sar_lineno += 1

                    if sar_lineno > 5:
                        sar_line = parse(line.rstrip('\n'))
                
                        #print("____%s" % sar_line)

                        if sar_line[2] in CPU_LIST:

                            user = sar_line[3]
                            nice = sar_line[4]
                            system = sar_line[5]
                            iowait = sar_line[6]

                            #print("sys: %s\n" % system)

                            sar += [user, nice, system, iowait]
                            #sar += [system]


                        if sar_lineno == sar_maxline:
                            sar_rec_started = False
                            sar_lineno = 0
                            sar_list.append(sar)
                            sar = []

            else:
                break


    i = 0
    with open(SAR_CSV, 'w') as f:
        for sar in sar_list:
            #i = sar_list.index(sar)
            #print("___i %s" % i)
            #print("%s\n" % sar)
            
            f.write("%s\n" % ','.join(
                                      [ 
                                        str(i) 
                                      ] +
                                      sar
                                     ))
            i += 1
 



def main():
    datacrunch()


if __name__ == '__main__':
    main()


