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


VM_FILE = "vm-collect-iocpu.log_20210218_034517"
IRQ_CSV = "vm_interrupts_034517.csv"

IRQ_WATCH_LIST = [10, 24, 25, 26, 27, 28, 29, 30, 31, 32, 33, 34]



def datacrunch():

    date_start = "____DATE"
    ps_start = "____PS_THREADS"
    ps_end = "@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@"


    irq_list = []
    irq_cpu_list = []

    irq_ps_list = []

    irq_dict = {}



    date_rec_started = False
    date_lineno = 0
    date_maxline = 2

    ps_rec_started = False
    ps_lineno = 0
    aps_maxline = 9

    date = ""


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

                if date:

                    if (ps_rec_started and (ps_end in line)):
                        ps_rec_started = False
                        for irq in IRQ_WATCH_LIST:
                            irq_cpu_list.append(irq_dict[irq])
                        date = ""
                        irq_list.append(irq_cpu_list)
                        irq_cpu_list = []
                        irq_dict = {}               



                    if ps_rec_started:
                        if "irq/" in line and "-virtio" in line:
                            irq_line = parse(line.rstrip('\n'))
                            irq = int(irq_line[12].split('/')[1].split('-')[0])
                            cpu = irq_line[3]
                            irq_dict[irq] = cpu
                             
                            

                    if ps_start in line:
                        ps_rec_started = True
                        irq_cpu_list = [date]
                       
                
                    """

                    if ps_rec_started:
                        ps_lineno += 1

                        if ps_lineno > 1:
                            ps_line = parse(line.rstrip('\n'))
                
                            usr = "%.2f" % float(ps_line[2])
                            sys = "%.2f" %  float(ps_line[4])
                            iowait = "%.2f" % float(ps_line[5])
                            hardirq = "%.2f" % float(ps_line[6])
                            softirq = "%.2f" % float(ps_line[7])
                            steal = "%.2f" % float(ps_line[8])
                         
                            ps += [usr, sys, iowait, hardirq, softirq, steal]

                            if ps_lineno == ps_maxline:
                                ps_rec_started = False
                                ps_lineno = 0
                                ps_list.append(ps)
                                ps = []
 
                     """

                      


            else:
                break



    i = 0
    with open(IRQ_CSV, 'w') as f:
        for irq_cpu_list in irq_list:
            f.write("%s\n" % ','.join(
                                      [ 
                                        str(i) 
                                      ] +
                                      irq_cpu_list
                                     ))
            i += 1
 



def main():
    datacrunch()


if __name__ == '__main__':
    main()


