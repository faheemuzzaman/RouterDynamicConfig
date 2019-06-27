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

# from werkzeug import generate_password_hash, check_password_hash
@app.route('/new_user')
def add_user_view():
    return render_template('add.html')


@app.route('/add', methods=['POST'])
def add_user():
    try:
        _name = request.form['inputName']
        _location = request.form['inputLocation']
        # validate the received values
        if _name and _location and request.method == 'POST':
            # save edits
            sql = "INSERT INTO tbl_user(user_name, user_location) VALUES(%s, %s)"
            data = (_name, _location,)
            conn = mysql.connect()
            cursor = conn.cursor()
            cursor.execute(sql, data)
            conn.commit()
            flash('Customer added successfully!')
            return redirect('/customer')
        else:
            return 'Error while adding user'
    except Exception as e:
        print(e)
    finally:
        cursor.close()
        conn.close()


@app.route('/customer')
def users():
    try:
        conn = mysql.connect()
        cursor = conn.cursor(pymysql.cursors.DictCursor)
        cursor.execute("SELECT * FROM tbl_user")
        rows = cursor.fetchall()
        table = Results(rows)
        table.border = True
        return render_template('customer.html', table=table)
    except Exception as e:
        print(e)
    finally:
        cursor.close()
        conn.close()


@app.route('/edit/<int:id>')
def edit_view(id):
    try:
        conn = mysql.connect()
        cursor = conn.cursor(pymysql.cursors.DictCursor)
        cursor.execute("SELECT * FROM tbl_user WHERE user_id=%s", id)
        row = cursor.fetchone()
        if row:
            return render_template('edit.html', row=row)
        else:
            return 'Error loading #{id}'.format(id=id)
    except Exception as e:
        print(e)
    finally:
        cursor.close()
        conn.close()


@app.route('/update', methods=['POST'])
def update_user():
    try:
        _name = request.form['inputName']
        _location = request.form['inputLocation']
        _id = request.form['id']
        # validate the received values
        if _name and _location and _id and request.method == 'POST':

            # save edits
            sql = "UPDATE tbl_user SET user_name=%s, user_location=%s WHERE user_id=%s"
            data = (_name, _location, _id,)
            conn = mysql.connect()
            cursor = conn.cursor()
            cursor.execute(sql, data)
            conn.commit()
            flash('User updated successfully!')
            return redirect('/customer')
        else:
            return 'Error while updating user'
    except Exception as e:
        print(e)
    finally:
        cursor.close()
        conn.close()


@app.route('/delete/<int:id>')
def delete_user(id):
    try:
        conn = mysql.connect()
        cursor = conn.cursor()
        cursor.execute("DELETE FROM tbl_user WHERE user_id=%s", (id,))
        conn.commit()
        flash('User deleted successfully!')
        return redirect('/customer')
    except Exception as e:
        print(e)
    finally:
        cursor.close()
        conn.close()


@app.route('/getitem', methods=['POST'])
def process():
    _server_ip = request.form['comboxip']
    if _server_ip != "":
        print("IP: "+_server_ip)
        db = MySQLdb.connect("localhost", "root", "", "test")
        cursor = db.cursor()
        query_fetch_item = "SELECT distinct(item) from tbldetails where ip='" + \
            _server_ip+"' AND description!=''"
        print(query_fetch_item)
        cursor.execute(query_fetch_item)

        data = []
        for row in cursor:
            data.append(row)

        return jsonify({'output': data})

    return jsonify({'error': 'Missing data!'})


@app.route('/getip', methods=['POST'])
def process_getips():
    _customer_name = request.form['comboxcustomer']
    if _customer_name != "":
        print("IP: "+_customer_name)
        db = MySQLdb.connect("localhost", "root", "", "test")
        cursor = db.cursor()
        query_fetch_customer = "SELECT distinct(ip) from tbldetails where user_name='" + \
            _customer_name+"' AND description!=''"
        print(query_fetch_customer)
        cursor.execute(query_fetch_customer)

        data_customer = []
        for row in cursor:
            data_customer.append(row)

        return jsonify({'output': data_customer})

    return jsonify({'error': 'Missing data!'})


@app.route('/search', methods=['GET', 'POST'])
def my_form_get_data():
    if request.method == "POST":
        phase = request.form['hidedata']
        print("check data"+phase)
        if request.form['hidedata'] == "false":

            _selected_ips = request.form['txtips'].splitlines()
            _selected_ips_list = ""
            for list_ips in _selected_ips:
                _selected_ips_list += "ip='"+list_ips+"' OR "


            _selected_items = request.form['txtitems'].splitlines()
            _selected_item_list = ""
            for list_item in _selected_items:
                _selected_item_list += "item like '%"+list_item+"' OR "

            db = MySQLdb.connect("localhost", "root", "", "test")
            query = "SELECT item,version,partnumber,serialnumber,description from tbldetails where ("+ \
                _selected_ips_list+"1 != 1) AND ("+_selected_item_list+" 1 != 1)"
            print("Query 1122:"+query)
            cursor = db.cursor()
            cursor.execute(query)
            
            fetch_rows_ip = []
            for row in cursor:
                fetch_rows_ip.append(row)

            db = MySQLdb.connect("localhost", "root", "", "test")

            cursor = db.cursor()

            cursor.execute("SELECT distinct user_name from tbldetails")
            print(cursor)
            rows = []
            for row in cursor:
                rows.append(row)

            return render_template('fetch.html', fetch_data=fetch_rows_ip, data_customer=rows)

        else:
            # _ip = request.form['comip']

            _selected_ips = request.form['txtips'].splitlines()
            _selected_ips_list = ""
            for list_ips in _selected_ips:
                _selected_ips_list += "ip='"+list_ips+"' OR "

            # _selected_items = request.form['txtitems'].splitlines()
            # _selected_item_list = ""
            # for list_item in _selected_items:
            #     _selected_item_list += "item like '%"+list_item+"' OR "

            db = MySQLdb.connect("localhost", "root", "", "test")
            query = "SELECT item,version,partnumber,serialnumber,description from tbldetails where " + \
                _selected_ips_list+" 1!=1 "
            print("Update"+query)
            cursor = db.cursor()
            cursor.execute(query)
            print("Query:"+query)
            fetch_rows_ip = []
            for row in cursor:
                fetch_rows_ip.append(row)

            db = MySQLdb.connect("localhost", "root", "", "test")

            cursor = db.cursor()

            cursor.execute("SELECT distinct ip from tbldetails")
            print(cursor)
            rows = []
            for row in cursor:
                rows.append(row)

            return render_template('fetch.html', fetch_data=fetch_rows_ip, data=rows)
    else:
        db = MySQLdb.connect("localhost", "root", "", "test")

        cursor = db.cursor()

        cursor.execute("SELECT distinct user_name from tbldetails")
        print(cursor)
        rows = []
        for row in cursor:
            rows.append(row)
    return render_template('fetch.html', data_customer=rows)


@app.route('/', methods=['GET'])
def customer_get_username():
    db = MySQLdb.connect("localhost", "root", "", "test")
    print("Work")
    cursor = db.cursor()

    cursor.execute("SELECT distinct user_name from tbl_user")
        
    rows_customers = []
    for row in cursor:
        rows_customers.append(row)
        print(row)

    return render_template('index.html', data_customer=rows_customers)



@app.route('/', methods=['POST','GET'])
def my_form_post():

    _fromated_data = ""
    _ip = request.form['txtip']
    _ip_lists = ""
    if request.method == "POST":
        db = MySQLdb.connect("localhost", "root", "", "test")

        cursor = db.cursor()

        cursor.execute("SELECT distinct user_name from tbl_user")
        print(cursor)
        rows_customers = []
        for row in cursor:
            rows_customers.append(row)

        if _ip.find(" ") != -1:
            print("Many IPS")
            _ip_lists = _ip.split()
            for iplist in _ip_lists:
                print(iplist)
                _fromated_data = ""
                _ip_date = ""
                _username = request.form['txtusername']
                _password = request.form['txtpassword']
                _customer = request.form['comcustomer']

                _device = ConnectHandler(
                    device_type='cisco_ios', ip=iplist, username=_username, password=_password)
                _output = _device.send_command("show chassis hardware")
                _device.disconnect()

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

                _ip_date = iplist+" "+dt_string
                print(_ip_date)
                with open("test.csv", 'r') as f:
                    with open(_ip_date+".csv", 'w') as f1:
                        next(f)
                        next(f)   # skip header line
                        for line in f:
                            f1.write(line)

                os.remove('test.csv')

                mydb = MySQLdb.connect(
                    host='localhost', user='root', passwd='', db='test')
                cursor = mydb.cursor()
                _csv_line_count = 0
                # cursor.execute('INSERT INTO tbldetails (item,version,partnumber,serial,description) VALUES("","","","","")')
                with open(_ip_date+".csv") as csvfile:
                    readCSV = csv.reader(csvfile, delimiter=',')
                    for row in readCSV:
                        if _csv_line_count == 0:
                            _csv_line_count += 1
                        else:
                            cursor.execute(
                                "INSERT INTO tbldetails (item,version,partnumber,serialnumber,description,ip,user_name) VALUES('"+row[0]+"','"+row[1]+"','"+row[2]+"','"+row[3]+"','"+row[4]+"','"+_ip_date+"','"+_customer+"')")
                            _csv_line_count += 1
                mydb.commit()
                cursor.close()

            return render_template('index.html', message="ALL Data Submited", data_customer=rows_customers)

        else:
            _ip = request.form['txtip']
            _username = request.form['txtusername']
            _password = request.form['txtpassword']
            _customer = request.form['comcustomer']

            _device = ConnectHandler(
                device_type='cisco_ios', ip=_ip, username=_username, password=_password)
            _output = _device.send_command("show chassis hardware")
            _device.disconnect()

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

            _ip_date = _ip+" "+dt_string
            with open("test.csv", 'r') as f:
                with open(_ip_date+".csv", 'w') as f1:
                    next(f)
                    next(f)   # skip header line
                    for line in f:
                        f1.write(line)

            # os.remove('test.csv')

            mydb = MySQLdb.connect(
                host='localhost', user='root', passwd='', db='test')
            cursor = mydb.cursor()
            _csv_line_count = 0
            # cursor.execute('INSERT INTO tbldetails (item,version,partnumber,serial,description) VALUES("","","","","")')
            with open(_ip_date+".csv") as csvfile:
                readCSV = csv.reader(csvfile, delimiter=',')
                for row in readCSV:
                    if _csv_line_count == 0:
                        _csv_line_count += 1
                    else:
                        cursor.execute(
                            "INSERT INTO tbldetails (item,version,partnumber,serialnumber,description,ip,user_name) VALUES('"+row[0]+"','"+row[1]+"','"+row[2]+"','"+row[3]+"','"+row[4]+"','"+_ip_date+"','"+_customer+"')")
                        _csv_line_count += 1
            mydb.commit()
            cursor.close()

            return render_template('index.html', message="Data Submit in Database", data_customer=rows_customers)
    else:
        db = MySQLdb.connect("localhost", "root", "", "test")

        cursor = db.cursor()

        cursor.execute("SELECT distinct user_name from tbl_user")
        
        rows_customers = []
        for row in cursor:
            rows_customers.append(row)
            print(row)

    return render_template('index.html', data_customer=rows_customers)


if __name__ == "__main__":
    app.run()

# s = "Hardware inventory: Item Version Part number Serial number Description Chassis 1ed4cedf63a0 FIREFLY-PERIMETER Midplane System IO Routing Engine FIREFLY-PERIMETER RE FPC 0 Virtual FPC PIC 0 Virtual GE Power Supply 0"
