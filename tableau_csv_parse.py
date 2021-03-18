import csv
from datetime import datetime
from datetime import timedelta
from dateutil import tz
import yaml
import json

from enum import Enum

class Stat(Enum):
    DATE = 0
    OLD_STAT = 1
    NEW_STAT = 2
    CASE_ID = 3
    SUBJECT = 4

class Severity(Enum):
    DATE = 0
    OLD_SEV = 1
    NEW_SEV = 2
    CASE_ID = 3
    SUBJECT = 4

class Created(Enum):
    DATE = 0
    CASE_ID = 1
    SUBJECT = 2
    OPENING_SEV = 3


WEEKDICT = {
    0: 'Monday',
    1: 'Tuesday',
    2: 'Wednesday',
    3: 'Thursday',
    4: 'Friday',
    5: 'Saturday',
    6: 'Sunday' 
}



SLA = {
    'L1': 48 * 60,       # 48 hours 
    'L2': 10 * 9 * 60,   # 10 business days
    'L3': 20 * 9 * 60    # 20 business days
}


STATUS_FILE="2019_2020_status_simple.csv"
SEVERITY_FILE="2019_2020_severity_simple.csv"
CREATED_FILE="2019_2020_created_simple.csv"


wous_time_dict = {}

case_severity_dict = {}

wous_time_sev_dict = {}

case_timediffmins = {}





def add_timeslot(caseid, start_time, end_time, timediff):

    if caseid not in wous_time_dict:
        wous_time_dict[caseid] = []

    wous_time_dict[caseid].append([start_time, end_time, timediff])




def collectmins(caseid, timediff):

    if caseid not in case_timediffmins:
        case_timediffmins[caseid] = 0

    casemins = case_timediffmins[caseid]
    casemins += timediff

    case_timediffmins[caseid] = casemins




def add_to_dict(caseid, start_date, stop_date, timediff_minutes):

    if caseid in case_severity_dict:

        if caseid not in wous_time_sev_dict:
            wous_time_sev_dict[caseid] = {}

        for severity_period in case_severity_dict[caseid]:
     
            severity = severity_period[0]
            start_sev_date = severity_period[1]
            stop_sev_date = severity_period[2]


            if stop_sev_date is not None:

                if ((start_date >= start_sev_date and stop_date <= stop_sev_date) or
                    (start_date < stop_sev_date and stop_date > stop_sev_date) or 
                    (start_date < start_sev_date and stop_date <= stop_sev_date) or
                    (start_date < start_sev_date and stop_date > stop_sev_date)):

                   if severity not in wous_time_sev_dict[caseid]:
                       wous_time_sev_dict[caseid][severity] = []

                   wous_time_sev_dict[caseid][severity].append([start_date, stop_date, timediff_minutes])
                   break

            else:

                if ((start_date >= start_sev_date) or
                    (stop_date > start_sev_date)):

                   if severity not in wous_time_sev_dict[caseid]:
                       wous_time_sev_dict[caseid][severity] = []

                   wous_time_sev_dict[caseid][severity].append([start_date, stop_date, timediff_minutes])
                   break





def main():




    #============================================================================================================

    with open(CREATED_FILE) as csv_file:

        csv_reader = csv.reader(csv_file, delimiter=',')

        for line in csv_reader:
            utctime = line[Created.DATE.value]
            date = datetime.strptime(utctime,'%m/%d/%Y %I:%M:%S %p')
            date = date.replace(tzinfo=tz.gettz('UTC'))
            date = date.astimezone(tz.tzlocal())

            caseid = line[Created.CASE_ID.value]
            opening_sev = line[Created.OPENING_SEV.value]

            if caseid not in case_severity_dict:
                case_severity_dict[caseid] = [[opening_sev, date, None]]


    #============================================================================================================


    with open(SEVERITY_FILE) as csv_file:

        csv_reader = csv.reader(csv_file, delimiter=',')

        for line in csv_reader:
            utctime = line[Severity.DATE.value]
            date = datetime.strptime(utctime,'%m/%d/%Y %I:%M:%S %p')
            date = date.replace(tzinfo=tz.gettz('UTC'))
            date = date.astimezone(tz.tzlocal())

            caseid = line[Severity.CASE_ID.value]

            old_sev = line[Severity.OLD_SEV.value].split('-')[0]
            new_sev = line[Severity.NEW_SEV.value].split('-')[0]


            if caseid in case_severity_dict:
                if case_severity_dict[caseid][-1][0] == old_sev:
                    case_severity_dict[caseid][-1][2] = date
                    case_severity_dict[caseid].append([new_sev, date, None])


    #print("SEV %s" % case_severity_dict)



    #============================================================================================================


    case_dict = {}

    with open(STATUS_FILE) as csv_file:

        csv_reader = csv.reader(csv_file, delimiter=',')

        time_s = []

        for line in csv_reader:
            #print(line)

            utctime = line[Stat.DATE.value]
            #print(utctime)

            d = datetime.strptime(utctime,'%m/%d/%Y %I:%M:%S %p')
            #print('UTC %s' % d.strftime('%Y%m%d%H%M%S'))

            d = d.replace(tzinfo=tz.gettz('UTC'))
            d = d.astimezone(tz.tzlocal())
            #print('CET %s' % d.strftime('%Y%m%d%H%M%S'))

            case = line[Stat.CASE_ID.value]

            if case not in case_dict: 
                case_dict[case] = []

            new_stat = line[Stat.NEW_STAT.value]

            start_date = 0
            stop_date = 0

            if new_stat == 'Waiting on Support' or new_stat == 'Waiting on Engineering':
                start_date = d
                #start_date = d.strftime('%Y%m%d%H%M%S')

            if new_stat == 'Waiting on Customer' or new_stat == 'Resolved':
                stop_date = d
                #stop_date = d.strftime('%Y%m%d%H%M%S')


            time_pair_series = case_dict[case]


            if len(time_pair_series) == 0:
                if start_date != 0:
                    time_pair = []
                    time_pair.append(start_date)
                    time_pair_series.append(time_pair)
            else:
                if len(time_pair_series[len(time_pair_series)-1]) == 1:
                    if stop_date != 0:
                        time_pair_series[len(time_pair_series)-1].append(stop_date)

                else:
                    if start_date != 0:
                        time_pair = []
                        time_pair.append(start_date)
                        time_pair_series.append(time_pair)

            case_dict[case] = time_pair_series
                    
    '''                      
    with open("out.txt", 'w') as out_file:
        out_file.write("%s" % case_dict)
        
    print("CASE DICT: %s" % case_dict)
    '''
  
    #===============================================================================================



    for caseid, time_pair_series in case_dict.items():

        print("____%s\n" % caseid)

        for timepair in time_pair_series:

            if len(timepair) > 1:

                diff = (timepair[1] - timepair[0]).total_seconds()/60

                print("        %s %s - [%s] - %s %s\n" % (timepair[0], WEEKDICT[timepair[0].weekday()],
                                                          diff,
                                                          timepair[1], WEEKDICT[timepair[1].weekday()]))

            elif len(timepair) == 1:
                print("        %s %s\n" % (timepair[0], WEEKDICT[timepair[0].weekday()]))


        print("        -----------------\n")

        if caseid in case_severity_dict:

            for severity_period in case_severity_dict[caseid]:

                if severity_period[2] is not None:
                    print("%s      %s %s - %s %s\n" % (severity_period[0],
                                                      severity_period[1], WEEKDICT[severity_period[1].weekday()],
                                                      severity_period[2], WEEKDICT[severity_period[2].weekday()]))
 
                else:
                    print("%s      %s %s - CONT\n" % (severity_period[0],
                                                     severity_period[1], WEEKDICT[severity_period[1].weekday()]))

        print("\n")



    #==============================================================================================




    #print(yaml.dump(case_dict, default_flow_style=False))

    #print(json.dumps(case_dict, indent=4))


    #for caseid, time_pair_series in case_dict.items():

    caseid_list = case_dict.keys()

    for caseid in sorted(caseid_list):

        total_minutes = 0

        time_pair_series = case_dict[caseid]         


        for time_pair in time_pair_series:

            start_date = time_pair[0]
            stop_date = time_pair[1]            
 
            start_date_lower_boundary = start_date.replace(hour=8, minute=0, second=0)
            start_date_upper_boundary = start_date.replace(hour=17, minute=0, second=0)

            stop_date_lower_boundary = stop_date.replace(hour=8, minute=0, second=0)
            stop_date_upper_boundary = stop_date.replace(hour=17, minute=0, second=0)


            if ((start_date < start_date_lower_boundary and stop_date < start_date_lower_boundary) or
                (start_date > start_date_upper_boundary and stop_date > stop_date_upper_boundary)):

                timediff_minutes = 0
 
            else:

                if start_date < start_date_lower_boundary:
                    start_date = start_date_lower_boundary

                if start_date > start_date_upper_boundary:
                    start_date += timedelta(days=1)
                    start_date = start_date.replace(hour=8, minute=0, second=0)

                if stop_date > stop_date_upper_boundary:
                    stop_date = stop_date_upper_boundary

                if stop_date < stop_date_lower_boundary:
                    stop_date -= timedelta(days=1)
                    stop_date = stop_date.replace(hour=17, minute=0, second=0)


                dayofweek = start_date.weekday()
                if dayofweek >= 5:
                    #print("start date in WEEKEND")
                    start_date += timedelta(days=(7-dayofweek))
                    start_date = start_date.replace(hour=8, minute=0, second=0)
 
                dayofweek = stop_date.weekday()           
                if dayofweek >= 5:
                    #print("stop date in WEEKEND")
                    stop_date += timedelta(days=(7-dayofweek))
                    stop_date = stop_date.replace(hour=8, minute=0, second=0)





                #print("%s - %s" % (start_date.strftime('%Y%m%d%H%M%S'), stop_date.strftime('%Y%m%d%H%M%S')))

                #timediff_minutes = 0




                if stop_date.day > start_date.day:

                    day_diff = stop_date.day - start_date.day - 1

                    #timediff_minutes = day_diff * 8 * 60
                    total_timediff_minutes = 0

                    for day in range(day_diff):
                     
                        count_date = start_date + timedelta(days=(day+1))

                        if count_date.weekday() >= 5:
                            continue
                        else:
                            count_date_start_time = count_date.replace(hour=8, minute=0, second=0)
                            count_date_stop_time = count_date.replace(hour=17, minute=0, second=0)
                            count_date_timediff_minutes = (count_date_stop_time - count_date_start_time).total_seconds()/60
                            total_timediff_minutes += count_date_timediff_minutes


                    start_date_upper_boundary = start_date.replace(hour=17, minute=0, second=0)
                    stop_date_lower_boundary = stop_date.replace(hour=8, minute=0, second=0)  

                    #timediff_minutes += (start_date_upper_boundary - start_date).total_seconds()/60
                    #timediff_minutes += (stop_date - stop_date_lower_boundary).total_seconds()/60                   
                    total_timediff_minutes += (start_date_upper_boundary - start_date).total_seconds()/60
                    total_timediff_minutes += (stop_date - stop_date_lower_boundary).total_seconds()/60

                    collectmins(caseid, total_timediff_minutes)


                    #start_day_slot_timediff_minutes = (start_date_upper_boundary - start_date).total_seconds()/60
                    #add_to_dict(caseid, start_date, start_date_upper_boundary, start_day_slot_timediff_minutes)

                    #stop_day_slot_timediff_minutes = (stop_date - stop_date_lower_boundary).total_seconds()/60
                    #add_to_dict(caseid, stop_date_lower_boundary, stop_date, stop_day_slot_timediff_minutes)

                    #add_timeslot(caseid, start_date, stop_date, timediff_minutes)



                    start_day_slot_timediff_minutes = (start_date_upper_boundary - start_date).total_seconds()/60
                    add_to_dict(caseid, start_date, start_date_upper_boundary, start_day_slot_timediff_minutes)


                    for day in range(day_diff):

                        count_date = start_date + timedelta(days=(day+1))

                        if count_date.weekday() >= 5:
                            continue 
                        else:
                            count_date_start_time = count_date.replace(hour=8, minute=0, second=0)
                            count_date_stop_time = count_date.replace(hour=17, minute=0, second=0)
                            count_date_timediff_minutes = (count_date_stop_time - count_date_start_time).total_seconds()/60

                            add_to_dict(caseid, count_date_start_time, count_date_stop_time, count_date_timediff_minutes)


                    stop_day_slot_timediff_minutes = (stop_date - stop_date_lower_boundary).total_seconds()/60
                    add_to_dict(caseid, stop_date_lower_boundary, stop_date, stop_day_slot_timediff_minutes)





                if stop_date.day == start_date.day:

                    timediff_minutes = (stop_date - start_date).total_seconds()/60   

                    collectmins(caseid, timediff_minutes)



                    add_to_dict(caseid, start_date, stop_date, timediff_minutes)


                    #add_timeslot(caseid, start_date, stop_date, timediff_minutes)




   
                #print("MINUTES %s\n" % timediff_minutes)



            #total_minutes += timediff_minutes


        #print("CASE %s:  %d mins, %d hours, %.2f days\n" % (caseid, int(total_minutes), 
        #                                                  int(total_minutes/60),
        #                                                  (float(total_minutes)/60/24)))


    #print("TIME_SEV_DICT %s\n" % wous_time_sev_dict)

    for caseid, sevtimeslotsdict in wous_time_sev_dict.items():

        print("____%s\n" % caseid)

        for sev in ['L1', 'L2', 'L3', 'L4']:

            if sev in sevtimeslotsdict:

                print("        %s\n" % sev)

                for timeslot in sevtimeslotsdict[sev]:
                    print("            %s - [%s] - %s   %s\n" % (timeslot[0], timeslot[2], timeslot[1], WEEKDICT[timeslot[0].weekday()]))
                 

                    if (timeslot[0].weekday() != timeslot[1].weekday()):
                        print("!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!! ====>  %s  %s" % (WEEKDICT[timeslot[0].weekday()], WEEKDICT[timeslot[1].weekday()]))
                     
                    if (timeslot[0].weekday() >= 5 or timeslot[0].weekday() >= 5):
                        print("!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!! ====>  %s  %s" % (WEEKDICT[timeslot[0].weekday()], WEEKDICT[timeslot[1].weekday()]))


        print("\n \n")
 

                                              
    #============================================================================================================


    caseminsperseveritydict = {}

    for caseid, sevtimeslotsdict in wous_time_sev_dict.items():

        sevlist = ['L1', 'L2', 'L3', 'L4']
        for sev in sevlist:

            if sev in sevtimeslotsdict:

                if caseid not in caseminsperseveritydict:
                    caseminsperseveritydict[caseid] = {}


                totalmins_persev = 0

                for timeslot in sevtimeslotsdict[sev]:

                    totalmins_persev += timeslot[2]

                caseminsperseveritydict[caseid][sev] = totalmins_persev

                

                '''
                altsevlist = ['L1', 'L2', 'L3', 'L4']
                for altsev in altsevlist:

                    if sevlist.index(sev) > altsevlist.index(altsev):

                        if altsev in caseminsperseveritydict[caseid]:
                            sevmins = caseminsperseveritydict[caseid][sev]
                            altsevmins = caseminsperseveritydict[caseid][altsev]
                    
                            caseminsperseveritydict[caseid][sev] = sevmins + altsevmins                  
                '''


    for caseid, totalminspersevdict in caseminsperseveritydict.items():

        print("____%s\n" % caseid)

        for sev in ['L1', 'L2', 'L3', 'L4']:

            if sev in totalminspersevdict:

                if sev in SLA:
                    if totalminspersevdict[sev] > SLA[sev]:
                        slaexceedmins = totalminspersevdict[sev] - SLA[sev]
                        slaexceedperc = (slaexceedmins / SLA[sev]) * 100
                        print("        %s:  %s min    SLA EXCEEDED !!! with %s minutes %s %\n" % (sev, round(totalminspersevdict[sev]), slaexceedmins, slaexceedperc))
                    else:
                        print("        %s:  %s min\n" % (sev, round(totalminspersevdict[sev])))
                else:
                    print("        %s:  %s min\n" % (sev, round(totalminspersevdict[sev])))



        print(" Total Mins:  %s min\n" % round(case_timediffmins[caseid]))


        print("\n")



    print("SLAs: %s" % SLA)

    #============================================================================================================

    '''
    with open(CREATED_FILE) as csv_file:

        csv_reader = csv.reader(csv_file, delimiter=',')

        for line in csv_reader:
            utctime = line[Created.DATE.value]
            date = datetime.strptime(utctime,'%m/%d/%Y %I:%M:%S %p')
            date = date.replace(tzinfo=tz.gettz('UTC'))
            date = date.astimezone(tz.tzlocal())

            caseid = line[Created.CASE_ID.value]
            opening_sev = line[Created.OPENING_SEV.value]

            if caseid not in case_severity_dict:
                case_severity_dict[caseid] = [[opening_sev, date, None]]
    '''

    #============================================================================================================


    '''
    with open(SEVERITY_FILE) as csv_file:

        csv_reader = csv.reader(csv_file, delimiter=',')

        for line in csv_reader:
            utctime = line[Severity.DATE.value]
            date = datetime.strptime(utctime,'%m/%d/%Y %I:%M:%S %p')
            date = date.replace(tzinfo=tz.gettz('UTC'))
            date = date.astimezone(tz.tzlocal())

            caseid = line[Severity.CASE_ID.value]

            old_sev = line[Severity.OLD_SEV.value].split('-')[0]
            new_sev = line[Severity.NEW_SEV.value].split('-')[0]
 

            if caseid in case_severity_dict:
                if case_severity_dict[caseid][-1][0] == old_sev:
                    case_severity_dict[caseid][-1][2] = date
                    case_severity_dict[caseid].append([new_sev, date, None])


    print("SEV %s" % case_severity_dict)
    '''


    #============================================================================================================


    '''
    # wous_time_sev_dict

    for caseid in case_severity_dict.keys():

        if caseid in wous_time_dict:

            wous_time_sev_dict[caseid] = {}

            timeslot_list = wous_time_dict[caseid]

            sevperiod_list = case_severity_dict[caseid]



            for timeslot in timeslot_list:
                timeslot_start = timeslot[0]
                timeslot_stop = timeslot[1]
                timeslot_diff = timeslot[2]

                match = 0

                for period in reversed(sevperiod_list):
                    severity = period[0]
                    period_start = period[1]
                    period_stop = period[2]


                    if period_stop == None:

                        if timeslot_start >= period_start:

                            match += 1

                            if severity not in wous_time_sev_dict[caseid]:
                                wous_time_sev_dict[caseid][severity] = [timeslot_diff]
                            else:
                                wous_time_sev_dict[caseid][severity].append(timeslot_diff)

                            break

                    else:
 
                        if timeslot_start >= period_start and timeslot_stop <= period_stop:

                            match += 1

                            if severity not in wous_time_sev_dict[caseid]:
                                wous_time_sev_dict[caseid][severity] = [timeslot_diff]
                            else:
                                wous_time_sev_dict[caseid][severity].append(timeslot_diff)

                            break

                        elif timeslot_start <= period_stop:

                            match += 1

                            if severity not in wous_time_sev_dict[caseid]:
                                wous_time_sev_dict[caseid][severity] = [timeslot_diff]
                            else:
                                wous_time_sev_dict[caseid][severity].append(timeslot_diff)

                            break

                        elif timeslot_stop >= period_start:

                            match += 1

                            if severity not in wous_time_sev_dict[caseid]:
                                wous_time_sev_dict[caseid][severity] = [timeslot_diff]
                            else:
                                wous_time_sev_dict[caseid][severity].append(timeslot_diff)
                            
                            break


                if match == 0:
                    if 'NOMATCH' not in wous_time_sev_dict[caseid]:
                        wous_time_sev_dict[caseid]['NOMATCH'] = [[timeslot_start, timeslot_stop, timeslot_diff]]
                    else:
                        wous_time_sev_dict[caseid]['NOMATCH'].append([timeslot_start, timeslot_stop, timeslot_diff])

    '''
                   
    #print("%s" % wous_time_sev_dict)                




if __name__ == '__main__':
    main()
