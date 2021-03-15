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



FWORK = "flush_workqueue.txt"
FUT = "futex_wait_queue_me.txt"
OFWORK = "other_flush_workqueue.txt"
OFUT = "other_futex_wait_queue_me.txt"
HANG = "hangtime.txt"

EVENTS_CSV = "events.csv"


timestamp_dict = {}


def parse_hang_timestamp(l):

    datetime = ""

    dt_list = l.split('T')
    date = dt_list[0]
    time = dt_list[1]

    datetime += ''.join(date.split('-'))
    datetime += ''.join(time.split(':'))

    return int(datetime)





def parse_svg_timestamp(l):

    datetime = ""

    dt_list = l.split('_')
    date = dt_list[0]
    time = dt_list[1]

    datetime += ''.join(date.split('-'))
    datetime += time

    return int(datetime)





def datacrunch(datafile, pointer_idx, bit_array_length):

    with open(datafile, 'r') as f:

        while True:

            line = f.readline()

            if line:

                timestamp = 0
                if datafile == HANG:
                    timestamp = parse_hang_timestamp(line.rstrip('\n'))
                else:
                    timestamp = parse_svg_timestamp(line.rstrip('\n'))

                if timestamp in timestamp_dict:
                    timestamp_dict[timestamp][pointer_idx] = '1'
                else:
                    bit_array = ['0'] * bit_array_length
                    bit_array[pointer_idx] = '1'
                    timestamp_dict[timestamp] = bit_array

            if not line:
                break







def main():

    datacrunch(HANG, 0, 5)
    datacrunch(FWORK, 1, 5)
    datacrunch(FUT, 2, 5)
    datacrunch(OFWORK, 3, 5)
    datacrunch(OFUT, 4, 5)

    timestamp_list = [t for t in timestamp_dict.keys()]
    timestamp_list.sort()


    i = 0
    with open(EVENTS_CSV, 'w') as f:
        for timestamp in timestamp_list:

            f.write("%s\n" % ','.join(
                                      [
                                        str(i)
                                      ] +
                                      [
                                        str(timestamp)
                                      ] +
                                      timestamp_dict[timestamp]
                                     ))
            i += 1



if __name__ == '__main__':
    main()


