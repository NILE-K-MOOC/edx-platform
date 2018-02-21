import json

from social.backends.oauth import BaseOAuth2


class OAuth2(BaseOAuth2):
    # callback name
    name = 'nhi'
    AUTHORIZATION_URL = 'http://e-learning.nhi.go.kr/external/kmooc.do'
    ACCESS_TOKEN_URL = 'https://policy.nhi.go.kr/oauth2/token.do'
    USER_INFO_URL = 'https://policy.nhi.go.kr/oauth2/token.do'
    SCOPE_SEPARATOR = ','
    ACCESS_TOKEN_METHOD = 'POST'
    EXTRA_DATA = [
        ('id', 'id'),
        ('expires', 'expires'),
        ('login', 'login')
    ]

    def get_user_details(self, response):
        """Return user details from Github account"""
        jsonString = dict()
        jsonString['login'] = response.get('user_no')
        jsonString['email'] = response.get('email')
        jsonString['name'] = response.get('user_nm')
        jsonString['id'] = response.get('user_no')

        return json.loads(json.dumps(jsonString))

    def user_data(self, access_token, *args, **kwargs):
        data = self.auth_complete_params()
        str = self.get_json(self.USER_INFO_URL, method='POST',
                            params={'access_token': access_token, 'grant_type': 'access_token_identify2', 'scope': 'http://sso.nhi.go.kr', 'client_id': data['client_id'], 'client_secret': data['client_secret'], 'client_ip': ''})
        str['id'] = str['user_no']

        try:
            return str
        except ValueError:
            return None

    def auth_complete(self, *args, **kwargs):
        data = self.auth_complete_params()
        data['scope'] = 'http://sso.nhi.go.kr'

        response = self.request_access_token(
            self.ACCESS_TOKEN_URL,
            data=data,
            headers=self.auth_headers(),
            method=self.ACCESS_TOKEN_METHOD
        )

        return self.do_auth(response['access_token'], response=response,
                            *args, **kwargs)
