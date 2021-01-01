'''
Module to record the final result files from aggregate files
'''

import os
import re
import csv
import fnmatch
from operator import itemgetter
from datetime import date, datetime, timedelta
from test.test_decimal import file
import requests
from unittest import case

def initial_env_check(DATA_FIRST_SET):
    '''
    Check whether the environment is stable or login error occurs
    '''
    
    count = 0 # to check environment is stable or not
    for folders, dirs, files in os.walk(DATA_FIRST_SET):
        for agg_file in fnmatch.filter(files,'*.aggregate.csv'):
            with open(os.path.join(folders,agg_file),'r') as aggregate_file:
                agg_reader = csv.DictReader(aggregate_file,delimiter=',')
                for row in agg_reader:
                    if row['Label'] == 'LoginAndHomePage' and row['Error'] == '100%':
                        count += 1
    return count

def check_execute_time(agg_file, start, jmx_file):
    '''
    Generate execution time of the jmx file
    '''
    curr_time=[]
    for jmx in jmx_file:
        if jmx in agg_file:
            index_val= jmx_file.index(jmx)
    start_time = timedelta(hours=int(start[index_val][0]),
                           minutes=int(start[index_val][1]),
                           seconds=int(start[index_val][2]))
    if index_val == len(jmx_file)-1:
        curr_val = str(datetime.time(datetime.now()))
        curr_val = curr_val('.')[0]
        curr_time.append(curr_val.split(':'))
        curr_time_val = timedelta(hours=int(curr_time[index_val][0]),
                                  minutes=int(curr_time[index_val][1]),
                                  seconds=int(curr_time[index_val][2]))
        val = curr_time_val - start_time
    else:
        end_time = timedelta(hours=int(start[index_val+1][0]),
                             minutes=int(start[index_val+1][1]),
                             seconds=int(start[index_val+1][2]))
        val = end_time - start_time
    val_split = str(val).split(':')
    diff = int(val_split[0])*60+int(val_split[1])*1+int(val_split[2])/60
    return round(diff), start_time

def get_label(folders, agg_file, final_list, cm_label, loop):
    '''
    Parse the aggregate file and get all the target requests
    '''
    full_list = []
    with open(os.path.join(folders, agg_file), 'r')as aggregate_file:
        aggregate_reader = csv.DictReader(aggregate_file, delimiter=',')
        for row in aggregate_reader:
            if int(row['# Samples']) == loop and row['Label'] != r'':
                if row['Label'] not in cm_label:
                    full_list.append(row['Label'])
        for label in full_list:
            if '[target]' in label:
                target = full_list.index(label)
                final_list = full_list[target:]
    return final_list

def get_aggregate_file(folders, agg_file, final_list, file_writer, server):
    '''
    Get the maximum response time, error percentage values for 
    the target requests from aggregate file
    '''
    result = 1 # result of success case
    exec_status = 'OK' # execution status of success case
    avg_list, row_list, target_error = [], [], []
    val = r'[\d]+-([\d][2])([\d][2])([\d][2])([a-zA-Z0-9_.()-]+).jmx'
    res = re.match(val, agg_file)
    start = timedelta(hours=int(res.group(1)),
                      minutes=int(res.group(2)),
                      seconds=int(res.group(3)))
    jmx_file= res.group(4)+'.jmx'
    with open(os.path.join(folders,agg_file), 'r')as aggregate_file:
        aggregate_reader = csv.DictReader(aggregate_file)
        for row in aggregate_reader:
            if row['Label'] in final_list:
                avg_list.append(int(row['Average']))
    max_value =  max(enumerate(avg_list), key=itemgetter(1))
    with open(os.path.join(folders, agg_file), 'r')as aggregate_file:
        aggregate_reader=csv.DictReader(aggregate_file)
        for row in aggregate_reader:
            full_error = row['Error %']
            full_error = full_error.replace('%','')
            compare_max = (row['Average'] == str(max_value[1]))
            if row['Label'] in final_list:
                target_error.append(row['Error %'])
            if row['Label'] in final_list and compare_max:
                average = row['Average']
                median = row['Median']
                nine_fifth = row['95% Line']
        for error in target_error:
            if error!='0.00%':
                result=0
                exec_status='Error:InTarget'
                break
    row_list.append([server, result, average, median, nine_fifth, full_error, exec_status])
    write_results_to_file(jmx_file, row_list, start, file_writer)
        
def write_results_to_file(jmx_file, row_list, start, file_writer):
    '''
    Save success results to the file
    '''
    file_writer.writerow({'Jmx':jmx_file,
                          'Date':date.today(),
                          'Environment':row_list[0][0],
                          'Result':row_list[0][1],
                          'Average':row_list[0][2],
                          'Median':row_list[0][3],
                          'Nine fifth':row_list[0][4],
                          'Error':row_list[0][5],
                          'Exec_Status':row_list[0][6],
                          'ExecTime': date.today.strftime("Y-%m-%d")+" "+str(start)})


def main(server, DATA_SET, loop, start_time, jmx_file):
    diff =0
    dt = datetime.now()
    skip_row, Err_row = [],[]
    skip_row.append([server, '0', '-1', '-1', '-1', '-1', 'Over 1min'])
    Err_row.append([server, '0', '-1', '-1', '-1', '-1', 'Try Re-execution'])
    data_execute = str(dt.strftime('%m%d-%H%M%S'))
    RESULT_FILE = data_execute + server + 'Aggregate_Result.csv'
    JTL_FILE = data_execute + server + 'Detail_Result.csv'
    final_file = open(RESULT_FILE, 'W',newline='')
    detail_file = open(JTL_FILE, 'W', newline='')
    column_list = ['JMX', 'Date', 'Environment', 'Result', 'Average', 'Median', 'Nine_fifth', 'Error']
