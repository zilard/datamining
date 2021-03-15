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
COMPSTAT_CSV = "marked_compute_102918.csv"

VM_HANG_TIMES = ["2021-02-09 10:50", "2021-02-09 11:18"]

MARK_SPIKE = 10000


vm_is_hanging = False


def fetchval(search_list, searchline_nr, searchcolons, f, compstat, div=1):

    rec_started = False
    lineno = 0
    fetch_list = []
    fetchtxt = ""
    line = ""

    while True:

        line = f.readline()

        if line:

            if all([searchtxt in line for searchtxt in search_list]):
                rec_started = True
                #print("FOUND  %s  IN   %s" % (search_list, line))

            if rec_started:
                lineno += 1


            if lineno == searchline_nr:
            
                parsed_line = parse(line.rstrip('\n'))

                for i, searchcol in enumerate(searchcolons):
          
                    if "____DATE" in search_list:      
                        if i == (len(searchcolons) - 1):
                       
                            #print("%s" % parsed_line)

                            fetchtxt += parsed_line[searchcol]
                        else:
                            fetchtxt += parsed_line[searchcol] + " "
                    else:
                        val = parsed_line[searchcol]
                        if div > 1:
                            val = "%.2f" % (float(val) / div)
                        fetch_list.append(val)
                      


                if "____DATE" in search_list:

                    date = fetchtxt.split('.')[0]

                    for hung_time in VM_HANG_TIMES:
                        if hung_time in date:
                            vm_is_hanging = True
                            break
                        else:
                            vm_is_hanging = False
 

                    mark = 0
                    if vm_is_hanging:
                        mark = MARK_SPIKE
                    compstat += [str(mark), date]
                else:
                    compstat += fetch_list


                break
 

        else:
            break
    
    #print("compstat: %s" % compstat)
    
    
    return line




def datacrunch():

    compstat = []
    compstat_list = []


    with open(COMPUTE_FILE, 'r') as f:

        while True:

            line = fetchval(["____DATE"], 2, [0, 1], f, compstat)
            line = fetchval(["Node 0 MemFree:"], 1, [3], f, compstat, 1024)
            line = fetchval(["Node 0 MemUsed:"], 1, [3], f, compstat, 1024)
            line = fetchval(["Node 1 MemFree:"], 1, [3], f, compstat, 1024)
            line = fetchval(["Node 1 MemUsed:"], 1, [3], f, compstat, 1024)
            line = fetchval(["pgsteal/s"], 2, [9], f, compstat)


            if len(compstat) == 7:
                compstat_list.append(compstat)
            #print("line %s" % line)

            compstat = []

            if not line:
                break


    i = 0
    with open(COMPSTAT_CSV, 'w') as f:
        for compstat in compstat_list:
            
            f.write("%s\n" % ','.join(
                                      [ 
                                        str(i) 
                                      ] +
                                      compstat
                                     ))
            i += 1
 



def main():
    datacrunch()


if __name__ == '__main__':
    main()

