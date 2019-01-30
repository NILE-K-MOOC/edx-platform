#-*- coding: utf-8 -*-
import subprocess
import openpyxl
import os
import sys
import pymysql

conn = pymysql.connect(
    host='127.0.0.1', 
    user='edxapp001', 
    password='password',
    db='edxapp', 
    charset='utf8'
)

curs = conn.cursor()

wb = openpyxl.load_workbook('hello.xlsx')
ws = wb.active

store = []
error = []

lock = 0
for r in ws.rows:
    tmp = {}
    lock += 1
    if lock > 4:

        tmp['id'] = r[0].value
        tmp['pw'] = r[1].value
        tmp['email'] = r[2].value
        tmp['name'] = r[3].value
        tmp['gender'] = r[4].value
        tmp['birth'] = str(r[5].value)[:4]
        store.append(tmp)

for item in store:
    command = 'bash /edx/app/edxapp/edx-platform/add_user.sh ' + item['email'] + ' ' + item['pw'] + ' ' + item['id']
    os.system(command)

    sql = "update auth_user set first_name='" + item['name'] + "' " + "where email= '" + item['email'] + "'"
    curs.execute(sql)
    conn.commit()

    sql = "update auth_user a join auth_userprofile b on a.id = b.user_id set b.year_of_birth = '"+item['birth']+"', b.gender = '"+item['gender']+"' where a.email = '"+item['email']+"';"
    curs.execute(sql)
    conn.commit()

conn.close()

