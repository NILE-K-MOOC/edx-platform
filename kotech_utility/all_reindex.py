import requests
import pymysql
from pytz import timezone
from datetime import datetime

conn = pymysql.connect(
    host='127.0.0.1',
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

for id in rows:
    course_id = id[0]
    print course_id

    URL = 'http://127.0.0.1:18010/api/' + course_id + '/search_reindex'
    response = requests.get(URL)

    print response.status_code
    print response.text

end = datetime.now(timezone('Asia/Seoul'))

print 'start -> ', start
print 'end -> ', end
