from social.backends.oauth import BaseOAuth2
from django.utils.http import urlencode
import json

class HelloworldOAuth2(BaseOAuth2):
    print "---------------------------> class called"

    name = 'helloworld'
    AUTHORIZATION_URL = 'http://all.kmooc.kr/o/authorize'
    ACCESS_TOKEN_URL = 'http://all.kmooc.kr/o/token/'
    # AUTHORIZATION_URL = 'http://myserver:8002/o/authorize'
    # ACCESS_TOKEN_URL = 'http://myserver:8002/o/token/'
    SCOPE_SEPARATOR = ','
    ACCESS_TOKEN_METHOD = 'POST'
    EXTRA_DATA = [
        ('id', 'id'),
        ('expires', 'expires'),
        ('login', 'login')
    ]

    def get_user_details(self, response):
        print "---------------------------> get_user_details"
        jsonString = "{"
        jsonString += '"login":"'+response.get('login')+'"'
        jsonString += ',"email":"'+response.get('email')+'"'
        jsonString += ',"name":"'+response.get('name')+'"'
        jsonString += ',"id":"'+response.get('id')+'"'
        jsonString += '}'

        print '***********************'
        print jsonString
        print '***********************'

        return json.loads(jsonString)


    def user_data(self, access_token, *args, **kwargs):
        print "---------------------------> user_data"
        """Loads user data from service"""
        url = 'http://all.kmooc.kr/api/hello?' + urlencode({
            'access_token': access_token
        })

        str = self.get_json(url)

        try:
            return str
        except ValueError:
            return None
