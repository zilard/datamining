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


COMPUTE_FILE = "zoneinfo.log"
COMPSTAT_CSV = "flame_zoneinfo.csv"

DATE_PATTERN = "2021."


def fetchval(search_list, searchline_nr, searchcolons, f, compstat, scale=0, div=0):

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
          
                    if DATE_PATTERN in search_list:      
                        if i == (len(searchcolons) - 1):
                       
                            #print("%s" % parsed_line)

                            fetchtxt += parsed_line[searchcol]
                        else:
                            fetchtxt += parsed_line[searchcol] + " "
                    else:
                        search_val = parsed_line[searchcol]
                        if scale and div:
                            val = float(search_val) * scale / div
                            search_val = "%.2f" % val
                        fetch_list.append(search_val)
                      


                if DATE_PATTERN in search_list:
                    compstat.append(fetchtxt)
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
    scale = 4
    div = 1024


    with open(COMPUTE_FILE, 'r') as f:

        while True:

            line = fetchval([DATE_PATTERN], 1, [0], f, compstat)

            line = fetchval(["Node 0, zone   Normal"], 10, [1], f, compstat, scale, div)
            line = fetchval(["Node 0, zone    DMA32"], 10, [1], f, compstat, scale, div)
            line = fetchval(["Node 1, zone   Normal"], 38, [1], f, compstat, scale, div)

            #line = fetchval(["cswch/s"], 2, [3], f, compstat)
            #line = fetchval(["fault/s", "pgsteal/s"], 2, [4, 9], f, compstat)
            #line = fetchval(["kbmemfree", "kbmemused", "kbcached", "kbactive", "kbinact", "kbdirty"], 2, [2, 3, 6, 9, 10, 11], f, compstat)

            if len(compstat) == 4:
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



