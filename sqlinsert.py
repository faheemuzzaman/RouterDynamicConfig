from flask import Flask, request, render_template, Response, jsonify, flash, redirect
from netmiko import ConnectHandler
import re
import os
import csv
import MySQLdb
from datetime import datetime
import pymysql
from app import app
from tables import Results
from db_config import mysql

now = datetime.now()
dt_string = now.strftime("(%d-%m-%Y) %H-%M-%S")

f=open("router.txt", "r")
_output = f.read()

_raw_data = _output.splitlines()
_file_data = ""
for _list in _raw_data:
    _check_count = 0
    _with_out_left_space = _list.lstrip()
    if _with_out_left_space.find("10GE  XFP") != -1:
        _with_out_left_space = _with_out_left_space.replace(
            "10GE  XFP", "10GE XFP")
        print(_with_out_left_space)

    _double_space = re.sub("\s\s+", ",", _with_out_left_space)
    new_lines = re.sub("\s+", "", _double_space)
    _check_count = int(new_lines.count(","))
    if _check_count < 4:
        _count_comma = int(new_lines.count(','))
        # print(_count_comma)
        while _count_comma < 4:
            _comma_index = new_lines.find(',')
            # print("_comma")
            # print(_comma_index)
            new_lines = new_lines[:_comma_index] + \
                ',' + new_lines[_comma_index:]
            _count_comma += 1

    # print(new_lines)
    _file_data += new_lines+"\n"

# print(_file_data)
f = open("test.csv", "w")
f.write(_file_data)
f.close()

with open("test.csv", 'r') as f:
    with open("20.20.20.2.csv", 'w') as f1:
        next(f)
        next(f)   # skip header line
        for line in f:
            f1.write(line)

mydb = MySQLdb.connect(
    host='localhost', user='root', passwd='', db='test')
cursor = mydb.cursor()
_csv_line_count = 0
with open("20.20.20.2.csv") as csvfile:
    readCSV = csv.reader(csvfile, delimiter=',')
    for row in readCSV:
        if _csv_line_count == 0:
            _csv_line_count += 1
        else:
            cursor.execute(
                "INSERT INTO tbldetails (item,version,partnumber,serialnumber,description,ip,user_name) VALUES('"+row[0]+"','"+row[1]+"','"+row[2]+"','"+row[3]+"','"+row[4]+"','20.20.20.2','MCB Bank')")
            _csv_line_count += 1
mydb.commit()
cursor.close()
