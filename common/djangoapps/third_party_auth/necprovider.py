from social.backends.oauth import BaseOAuth2
import json


class OAuth2(BaseOAuth2):
    """civicedu OAuth authentication backend"""

    # callback name
    name = 'nec'
    AUTHORIZATION_URL = 'http://www.civicedu.go.kr/web/oauth/server/authorize.jsp'
    ACCESS_TOKEN_URL = 'http://www.civicedu.go.kr/web/oauth/server/token2.jsp'
    SCOPE_SEPARATOR = ','
    ACCESS_TOKEN_METHOD = 'POST'
    EXTRA_DATA = [
        ('id', 'id'),
        ('expires', 'expires'),
        ('login', 'login')
    ]

    def get_user_details(self, response):

        # print 'response ---------------- s'
        # print response
        # print 'response ---------------- e'

        """Return user details from Github account"""
        jsonString = dict()
        jsonString['login'] = response.get('user_id')
        jsonString['email'] = response.get('email')
        jsonString['name'] = response.get('name')
        jsonString['id'] = response.get('id')

        print '***********************'
        print jsonString
        print '***********************'

        return json.loads(json.dumps(jsonString))

    def user_data(self, access_token, *args, **kwargs):
        """Loads user data from service"""
        print 'user_data called!!'

        str = self.get_json('http://www.civicedu.go.kr/web/oauth/server/resource2.jsp', params={'access_token': access_token})

        try:
            return str
        except ValueError:
            return None

    def auth_complete(self, *args, **kwargs):

        print 'auth_complete called1'
        print self.ACCESS_TOKEN_URL
        print self.auth_complete_params()
        print self.auth_headers()
        print self.ACCESS_TOKEN_METHOD
        print 'auth_complete called2'

        response = self.request_access_token(
            self.ACCESS_TOKEN_URL,
            data=self.auth_complete_params(),
            headers=self.auth_headers(),
            method=self.ACCESS_TOKEN_METHOD
        )
        self.process_error(response)
        return self.do_auth(response['access_token'], response=response,
                            *args, **kwargs)
