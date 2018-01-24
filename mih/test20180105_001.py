# -*- coding: utf-8 -*-
# test20180105_001.py
# mongodb
from pymongo import MongoClient
# mysql
import MySQLdb as mdb
from bson import ObjectId

client = MongoClient('localhost', 27017)		# connected at mongodb
db = client["edxapp"]	# database name
c_org = 'Test'
c_course = 'CC333'
c_name = 'CC313'
cursor = db.modulestore.active_versions.find_one({'org': c_org, 'course': c_course, 'run': c_name})	# find one data get row : org --> c_org, course --> c_course, run --> c_name
pb = cursor.get('versions').get('published-branch')	#
cursor = db.modulestore.structures.find_one({'_id': ObjectId(pb)})

blocks = cursor.get('blocks')
for block in blocks:
    print("Data : ", block.get('block_type'), block.get('block_id'), block.get('fields').get('catalog_visibility'))
    if block.get('block_type') and block.get('block_id'):
        if block.get('block_type') == 'course' and block.get('block_id') == 'course':
            if block.get('fields').get('catalog_visibility'):
                if block.get('fields').get('catalog_visibility') == 'none':
                    course_lock = 1
'''
다음은 몽고디비에서 데이터를 가져오는 방법에 대한 테스트 이다.
edxapp@precise64:~/edx-platform/mih$ python test20180105_001.py
('Data : ', u'about', u'title', None)
('Data : ', u'about', u'effort', None)
('Data : ', u'about', u'overview', None)
('Data : ', u'about', u'subtitle', None)
('Data : ', u'about', u'entrance_exam_enabled', None)
('Data : ', u'about', u'catalog_visibility', None)
('Data : ', u'about', u'entrance_exam_minimum_score_pct', None)
('Data : ', u'about', u'entrance_exam_id', None)
('Data : ', u'about', u'short_description', None)
('Data : ', u'about', u'description', None)
('Data : ', u'about', u'duration', None)
('Data : ', u'course', u'course', u'both')  <-- 여기에 데이터가 존재한다.
여러개 데이터 중에 특정 항목에서 데이터를 가져오기 위한 방법으로이다.
'''