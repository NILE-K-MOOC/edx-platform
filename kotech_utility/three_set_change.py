# -*- coding: utf-8 -*-
import os, uuid
import json
import datetime
import requests
import pymysql
import urllib
from pymemcache.client import base
from bson.objectid import ObjectId
from pymongo import MongoClient

# global variable
WEB1_HOST = '127.0.0.1'
database_id = '127.0.0.1'

def update_coursestructure(course_id, fourth_industry='N', ribbon_yn='N', job_edu_yn='N', linguistics='N'):
    """
    step1. mongo update
    step2. memcached 에서 branch 값으로 cache 된 내용을 확인후 삭제
    step3. elasticsearch update
    """
    # step1
    org = course_id.split('+')[0][10:]
    cid = course_id.split('+')[1]
    run = course_id.split('+')[2]

    client = MongoClient(database_id, 27017)
    db = client.edxapp
    active_versions = db.modulestore.active_versions.find_one({'org': org, 'course': cid, 'run': run})

    if active_versions:
        publish_branch = active_versions.get('versions').get('published-branch')
        draft_branch = active_versions.get('versions').get('draft-branch')
    else:
        raise Exception("active_versions is not exists")

    if publish_branch and draft_branch:
        result = db.modulestore.structures.update(
            {'_id': {'$in': [ObjectId(publish_branch), ObjectId(draft_branch)]}, 'blocks.block_type': 'course'},
            {
                '$set': {
                    'blocks.$.fields.fourth_industry': fourth_industry,
                    'blocks.$.fields.ribbon_yn': ribbon_yn,
                    'blocks.$.fields.job_edu_yn': job_edu_yn,
                    'blocks.$.fields.linguistics': linguistics
                }
            },
            multi=True
        )

        print "result -> ", result

    # step2
    #client = base.Client((WEB1_HOST, 11211))
    #a = client.delete('course_structure:1:%s' % draft_branch)
    #b = client.delete('course_structure:1:%s' % publish_branch)

    #print 'memcached:', a, b

    # step3
    #uri = 'http://{es_url}:9200/courseware_index/course_info/{course_id}?pretty'.format(
    #    es_url=WEB1_HOST,
    #    course_id=urllib.quote_plus(course_id)
    #)

    #query = json.dumps({
    #    "fourth_industry": fourth_industry,
    #    "ribbon_yn": ribbon_yn,
    #    "job_edu_yn": job_edu_yn,
    #    "linguistics": linguistics,
    #})

    #response = requests.post(uri, data=query)
    #print "status_code -> ", response.status_code
    #print "response.text -> ", response.text

print "hello world"

conn = pymysql.connect(
host=database_id, 
user='edxapp001', 
password='password',
db='edxapp', 
charset='utf8')
 
curs = conn.cursor()
 
sql = "select id from course_overviews_courseoverview limit 5"
curs.execute(sql)

course_list = [] 
rows = curs.fetchall()
for row in rows:
  course_list.append(row[0])

course_list = ['course-v1:KoreaUnivK+ku_phy_002+2019_A05']
print course_list

f = open("user_list.txt", 'r')
lines = f.readlines()
for line in lines:
    tmp = line.strip().split(', ')
    course = tmp[1]
    print tmp[0]
    print tmp[1]

    if tmp[0] == 'linguistics':
      sql = '''
        update course_overview_addinfo
        set linguistics = 'Y'
        , job_edu_yn = 'N'
        , ribbon_yn = 'N'
        , fourth_industry_yn = 'N'
        where course_id = '{course}'
      '''.format(course=tmp[1])
      curs.execute(sql)
      update_coursestructure(course, 'N', 'N', 'N', 'Y')
    elif tmp[0] == 'fourth_industry':
      sql = '''
        update course_overview_addinfo
        set linguistics = 'N'
        , job_edu_yn = 'N'
        , ribbon_yn = 'N'
        , fourth_industry_yn = 'Y'
        where course_id = '{course}'
      '''.format(course=tmp[1])
      curs.execute(sql)
      update_coursestructure(course, 'Y', 'N', 'N', 'N')
    elif tmp[0] == 'job_edu_yn':
      sql = '''
        update course_overview_addinfo
        set linguistics = 'N'
        , job_edu_yn = 'Y'
        , ribbon_yn = 'N'
        , fourth_industry_yn = 'N'
        where course_id = '{course}'
      '''.format(course=tmp[1])
      curs.execute(sql)
    conn.commit()
    update_coursestructure(course, 'N', 'N', 'Y', 'N')
    print sql
    print "-------------------------------"

conn.close()
f.close()

print "bye world"
