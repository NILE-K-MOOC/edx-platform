import requests
import pymysql
from pytz import timezone
from datetime import datetime

conn = pymysql.connect(
    host='192.168.1.113',
    user='edxapp001',
    password='password',
    db='edxapp',
    charset='utf8'
)

curs = conn.cursor()

sql = '''
select id
from course_overviews_courseoverview;
'''
curs.execute(sql)
rows = curs.fetchall()

conn.close()

start = datetime.now(timezone('Asia/Seoul'))

error_list = []
for id in rows:
    course_id = id[0]
    print course_id

    URL = 'http://127.0.0.1:18010/api/' + course_id + '/search_reindex'
    response = requests.get(URL)

    print response.status_code
    print response.text
    if response.status_code == 500:
        error_list.append(course_id)

end = datetime.now(timezone('Asia/Seoul'))

print "------------------------------"
for c in error_list:
  print c
print "------------------------------"

print 'total_cnt -> ', len(rows)
print 'error_list_cnt -> ', len(error_list)
print 'start -> ', start
print 'end -> ', end
