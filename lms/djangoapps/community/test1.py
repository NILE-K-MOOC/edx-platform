#-*- coding: utf-8 -*-
import time
import thread
import random
import logging
import logging.handlers
from datetime import datetime
import apscheduler.scheduler
from apscheduler.scheduler import Scheduler
import MySQLdb as mdb
from django.core.mail import send_mail
# from openedx.core.djangoapps.site_configuration import helpers as configuration_helpers
from django.conf import settings

import sys

reload(sys)
sys.setdefaultencoding('utf8')

###############################################################################
logger = logging.getLogger('test_sh01')
logger.setLevel(logging.DEBUG)
LOGFILE = './foo.log'
LOGSIZE = 1024*100
LOGBACKUP_COUNT = 5
if not logger.handlers:
    loghandler = logging.handlers.RotatingFileHandler(LOGFILE,
                maxBytes=LOGSIZE, backupCount=LOGBACKUP_COUNT)
    formatter = logging.Formatter('%(asctime)s-%(name)s-%(levelname)s-%(message)s')
    loghandler.setFormatter(formatter)
    logger.addHandler(loghandler)
apscheduler.scheduler.logger = logger

###############################################################################
class ScheduleJob(object):
    def __init__(self):
        self.sched = Scheduler()
        self.sched.start()
        self.job_count = self.cron_count = 0
        self.sched.add_interval_job(self.job_function, seconds=1)
        # self.sched.add_cron_job(self.cron_function, day_of_week='mon-fri', second='*/3')
    def __del__(self):
        self.shutdown()
    def shutdown(self):
        self.sched.shutdown()
    def job_function(self):
        # self.job_count += 1
        # sleep_period = random.randint(5,15) / 10.0
        # t_ident = str(thread.get_ident())[-4:]
        # print "[%s:%s:%s] ScheduleJob.job_function: and will sleep(%s)" % (
        #     self.job_count, t_ident, datetime.now(), sleep_period)
        # time.sleep(sleep_period)
        print 'start'
        email_list = []
        con = mdb.connect(settings.DATABASES.get('default').get('HOST'),
                          settings.DATABASES.get('default').get('USER'),
                          settings.DATABASES.get('default').get('PASSWORD'),
                          settings.DATABASES.get('default').get('NAME'),
                          charset='utf8')
        cur = con.cursor()
        query = """
            SELECT email, dormant_mail_cd from auth_user
        """
        cur.execute(query)
        row = cur.fetchall()
        cur.close()
        print 'row == ', row
        for u in row:
            user = u
            if user[1] == '15' or user[1] == '30':
                email_list.append(user[0])

        from_address = configuration_helpers.get_value(
            'email_from_address',
            settings.DEFAULT_FROM_EMAIL
        )

        print 'email_list == ',email_list

        cur = con.cursor()
        for e in email_list:
            try:
                send_mail('테스트 이메일', '이메일 제대로 가나요', from_address, [e], fail_silently=False)
                query1 = "update auth_user set dormant_mail_cd = '0' where email = '"+e+"' "
                cur.execute(query1)
                cur.execute('commit')
                query1 = "insert into drmt_auth_user_process(email,success) values('"+e+"', '1')"
                cur.execute(query1)
                cur.execute('commit')
            except SMTPException:
                print 'fail sending email'
                cur = con.cursor()
                query1 = "insert into drmt_auth_user_process(email) values('"+e+"')"
                cur.execute(query1)
                cur.execute('commit')

        cur.close()
        print 'end'






    # def cron_function(self):
    #     self.cron_count += 1
    #     sleep_period = random.randint(25,35) / 10.0
    #     t_ident = str(thread.get_ident())[-4:]
    #     print ">>>[%s:%s:%s] ScheduleJob.cron_function: and will sleep(%s)" % (
    #         self.cron_count, t_ident, datetime.now(), sleep_period)
    #     time.sleep(sleep_period)

###############################################################################
class SMTPException(Exception):
    """Base class for all exceptions raised by this module."""
if __name__=='__main__':
    t_ident = str(thread.get_ident())[-4:]
    print "[%s:%s] main starting..." % (t_ident, datetime.now())
    sj = ScheduleJob()
    for _ in xrange(5): time.sleep(1)
    sj.shutdown()
    print "[%s:%s] main ended." % (t_ident, datetime.now())