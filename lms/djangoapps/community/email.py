from django.conf import settings
import MySQLdb as mdb
from django.core.mail import send_mail
from openedx.core.djangoapps.site_configuration import helpers as configuration_helpers
import sys

reload(sys)
sys.setdefaultencoding('utf8')

class SMTPException(Exception):
    """Base class for all exceptions raised by this module."""

def test(request):
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

    for u in row:
        user = u
        if user[1] == '15' or user[1] == '30':
            email_list.append(user[0])
    # 이메일 전송
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
    print 'done'