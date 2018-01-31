from social.backends.oauth import BaseOAuth2
from django.utils.http import urlencode
import json

import requests

from django.http import (
    HttpRequest, HttpResponse
)



import logging
AUDIT_LOG = logging.getLogger("audit")
log = logging.getLogger(__name__)


class LgeOAuth2(BaseOAuth2):
    """Lge OAuth authentication backend"""
    name = 'lge'
    AUTHORIZATION_URL = 'http://oauthdev.lge.com:8080/oauth/authorize'
    ACCESS_TOKEN_URL = 'http://oauthdev.lge.com:8080/oauth/token'
    # SCOPE_SEPARATOR = ','
    
    #   STATE_PARAMETER = 'random_state_string'
    STATE_PARAMETER = False
    REDIRECT_STATE = False
    
    ACCESS_TOKEN_METHOD = 'POST'
    EXTRA_DATA = [
        #('id', 'id')
    ]

    def get_user_details(self, response):
        """Return user details from LGE account"""
        id = response['id']

        # log.info(response)
        # log.info('cookie')

        
        # log.info(user_name)
        return {'id': id}

    def user_data(self, access_token, *args, **kwargs):
        """Loads user data from service"""
        
        url = 'http://oauthdev.lge.com:8080/oauth/check_token?' + urlencode({
            'token': access_token
        })

        

        try:
            token_info = self.get_json(url)
            return {'id': token_info['user_name']}

        except ValueError:
            return None

