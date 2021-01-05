# -*- coding: utf-8 -*-
import os
import json
from Crypto.Cipher import AES
from base64 import b64decode
from base64 import b64encode
from path import Path as path
from django.conf import settings
import commands
from django.views.decorators.csrf import csrf_exempt
from openedx.core.djangoapps.site_configuration import helpers as configuration_helpers
from django.views.generic import View
from django.http import HttpRequest, HttpResponse, HttpResponseBadRequest, HttpResponseForbidden
from django.http import JsonResponse
import logging

log = logging.getLogger(__name__)


class Utils(View):

    def __init__(self):
        with open("/edx/app/edxapp/lms.auth.json") as auth_file:
            AUTH_TOKENS = json.load(auth_file)

        self.NICE_SECRET_KEY = AUTH_TOKENS.get('NICE_SECRET_KEY')
        self.NICE_SITECODE = AUTH_TOKENS.get('NICE_SITECODE')
        self.NICE_SITEPASSWD = AUTH_TOKENS.get('NICE_SITEPASSWD')
        self.NICE_CB_ENCODE_PATH = AUTH_TOKENS.get('NICE_CB_ENCODE_PATH')

    @csrf_exempt
    def post(self, request):
        lms_base = settings.ENV_TOKENS.get('LMS_BASE')
        return_url = request.POST.get('return_url')
        error_url = request.POST.get('error_url', 'nicecheckplus_error')

        nice_return_url = "{scheme}://{lms_base}/{return_url}".format(
            scheme=request.scheme,
            lms_base=lms_base,
            return_url=return_url
        )

        nice_error_url = '{scheme}://{lms_base}/{error_url}'.format(
            scheme=request.scheme,
            lms_base=lms_base,
            error_url=error_url
        )

        enc_data = self.nice_enc_data(nice_returnurl=nice_return_url, nice_errorurl=nice_error_url)
        return JsonResponse({'enc_data': enc_data})

    def nice_enc_data(self, nice_returnurl, nice_errorurl):
        nice_secret_key = self.NICE_SECRET_KEY
        nice_sitecode = self.NICE_SITECODE
        nice_sitepasswd = self.NICE_SITEPASSWD
        nice_cb_encode_path = self.NICE_CB_ENCODE_PATH
        nice_reqseq = 'REQ0000000001'
        nice_authtype = ''  # 없으면 기본 선택화면, X: 공인인증서, M: 핸드폰, C: 카드
        nice_popgubun = 'N'  # Y : 취소버튼 있음 / N : 취소버튼 없음
        nice_customize = ''  # 없으면 기본 웹페이지 / Mobile : 모바일페이지
        nice_gender = ''  # 없으면 기본 선택화면, 0: 여자, 1: 남자

        plaindata = '7:REQ_SEQ{0}:{1}8:SITECODE{2}:{3}9:AUTH_TYPE{4}:{5}7:RTN_URL{6}:{7}7:ERR_URL{8}:{9}11:POPUP_GUBUN{10}:{11}9:CUSTOMIZE{12}:{13}6:GENDER{14}:{15}' \
            .format(len(nice_reqseq), nice_reqseq,
                    len(nice_sitecode), nice_sitecode,
                    len(nice_authtype), nice_authtype,
                    len(nice_returnurl), nice_returnurl,
                    len(nice_errorurl), nice_errorurl,
                    len(nice_popgubun), nice_popgubun,
                    len(nice_customize), nice_customize,
                    len(nice_gender), nice_gender)

        nice_command = '{0} ENC {1} {2} {3}'.format(nice_cb_encode_path, nice_sitecode, nice_sitepasswd, plaindata)
        enc_data = commands.getoutput(nice_command)
        return enc_data

    def nice_des_data(self, enc_data):
        nice_sitecode = self.NICE_SITECODE
        nice_sitepasswd = self.NICE_SITEPASSWD
        nice_cb_encode_path = self.NICE_CB_ENCODE_PATH

        nice_command = '{0} DEC {1} {2} {3}'.format(nice_cb_encode_path, nice_sitecode, nice_sitepasswd, enc_data)
        plain_data = commands.getoutput(nice_command)

        d = {}
        pos1 = 0
        ci = None

        log.info('plain_data check ----------------------------------------- s')
        log.info(plain_data)
        log.info('plain_data check ----------------------------------------- m')
        log.info(plain_data.find(':'))
        log.info('plain_data check ----------------------------------------- e')

        while pos1 <= len(plain_data):
            pos1 = plain_data.find(':')
            key_size = int(plain_data[:pos1])
            plain_data = plain_data[pos1 + 1:]
            key = plain_data[:key_size]
            plain_data = plain_data[key_size:]
            pos2 = plain_data.find(':')
            val_size = int(plain_data[:pos2])
            val = plain_data[pos2 + 1: pos2 + val_size + 1]
            d[key] = val
            plain_data = plain_data[pos2 + val_size + 1:]

        return d

    def encrypt(self, key, iv, raw):

        if not key:
            key = self.NICE_SECRET_KEY

        if not iv:
            iv = key

        BLOCK_SIZE = 16  # Bytes
        pad = lambda s: s + (BLOCK_SIZE - len(s) % BLOCK_SIZE) * chr(BLOCK_SIZE - len(s) % BLOCK_SIZE)
        unpad = lambda s: s[:-ord(s[len(s) - 1:])]
        cipher = AES.new(key, AES.MODE_CBC, iv)
        p_raw = pad(raw.encode('utf8'))
        enc_data = cipher.encrypt(p_raw)
        b64_enc_data = b64encode(enc_data)
        return b64_enc_data

    def decrypt(self, key, iv, enc):
        if not key:
            key = self.NICE_SECRET_KEY

        if not iv:
            iv = key
        BLOCK_SIZE = 16  # Bytes
        pad = lambda s: s + (BLOCK_SIZE - len(s) % BLOCK_SIZE) * chr(BLOCK_SIZE - len(s) % BLOCK_SIZE)
        unpad = lambda s: s[:-ord(s[len(s) - 1:])]
        enc = b64decode(enc)
        cipher = AES.new(key, AES.MODE_CBC, iv)
        return unpad(cipher.decrypt(enc)).decode('utf8')
