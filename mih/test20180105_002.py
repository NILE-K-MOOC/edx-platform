# -*- coding: utf-8 -*-
# python test20180105_002.py

import MySQLdb as mdb

# MySQL Connection 연결
# con = mdb.connect(settings.DATABASES.get('default').get('HOST'),
#                  settings.DATABASES.get('default').get('USER'),
#                  settings.DATABASES.get('default').get('PASSWORD'),
#                  settings.DATABASES.get('default').get('NAME'),
#                  charset='utf8')

con = mdb.connect(host='localhost', user='root', passwd='', db='edxapp', charset='utf8')

# Connection 으로부터 Cursor 생성

curs = con.cursor()

# SQL문 실행
sql = "select id, display_name, catalog_visibility, org from course_overviews_courseoverview"
curs.execute(sql)

# 데이타 Fetch
rows = curs.fetchall()
for row in rows:
    print(row)  # 전체 rows

# print(rows[0])  # 첫번째 row: (1, '김정수', 1, '서울')
# print(rows[1])  # 두번째 row: (2, '강수정', 2, '서울')

# Connection 닫기
con.close()

'''
다음은 위 프로그램을 수행한 후 결과를 보여준다.
edxapp@precise64:~/edx-platform/mih$ python test20180105_002.py
(u'course-v1:edX+DemoX+Demo_Course', u'edX Demonstration Course', u'none', u'edX')
(u'course-v1:Pusan+KMOOC_02+2017_T1_1', u'\ucef4\ud4e8\ud130 \uacf5\ud559 \uac1c\ub8602', u'both', u'Pusan')
(u'course-v1:PusanX+CS106+2017_T10', u'\ucef4\ud4e8 \uacf5\ud559 \uc785\ubb38', u'both', u'PusanX')
(u'course-v1:Test+CC333+CC313', u'Test', u'both', u'Test')
(u'course-v1:Test+CC334+2017_T0_1', u'Test II (\ud14c\uc2a4\ud2b8 II \uac15\uc88c)', u'both', u'Test')
(u'course-v1:Test+CS204+2017_T2_1', u'Test1', u'both', u'Test')
(u'course-v1:Test01+CS202+2017_T22', u'\uc608\uc220\uacfc \uc778\uc0dd', u'both', u'Test01')
(u'course-v1:Test01+CS203+2017_T23', u'\uc608\uc220 \uc5b8\uc5b4\ud559', u'about', u'Test01')
(u'course-v1:TestX1+CS201+2017_T11', u'\uc608\uc220\uacfc \uacbd\uc601\uc758 \ub9cc\ub0a8', u'both', u'TestX1')
(u'course-v1:TestX1+CS202+2017_T11', u'\ub300\uc911\ubb38\ud654\ub85c \uc778\ubb38\ud559\ud558\uae30', u'both', u'TestX1')
(u'course-v1:TestX1+CS203+2017_T22', u'\uc608\uc220\uc758 \uc774\ud574', u'both', u'TestX1')
'''
