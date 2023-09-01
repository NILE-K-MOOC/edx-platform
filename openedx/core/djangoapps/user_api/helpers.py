# -*- coding: utf-8 -*-
"""
Helper functions for the account/profile Python APIs.
This is NOT part of the public API.
"""
import json
import logging
import traceback
from collections import defaultdict
from functools import wraps
import time

from django import forms
from django.core.serializers.json import DjangoJSONEncoder
from django.http import HttpResponseBadRequest, HttpRequest
from django.utils.encoding import force_text
from django.utils.functional import Promise

from django.db import connections
from django.contrib.auth.models import User

LOGGER = logging.getLogger(__name__)
log = logging.getLogger(__name__)


def intercept_errors(api_error, ignore_errors=None):
    """
    Function decorator that intercepts exceptions
    and translates them into API-specific errors (usually an "internal" error).

    This allows callers to gracefully handle unexpected errors from the API.

    This method will also log all errors and function arguments to make
    it easier to track down unexpected errors.

    Arguments:
        api_error (Exception): The exception to raise if an unexpected error is encountered.

    Keyword Arguments:
        ignore_errors (iterable): List of errors to ignore.  By default, intercept every error.

    Returns:
        function

    """

    def _decorator(func):
        """
        Function decorator that intercepts exceptions and translates them into API-specific errors.
        """

        @wraps(func)
        def _wrapped(*args, **kwargs):
            """
            Wrapper that evaluates a function, intercepting exceptions and translating them into
            API-specific errors.
            """
            try:
                return func(*args, **kwargs)
            except Exception as ex:
                # Raise and log the original exception if it's in our list of "ignored" errors
                for ignored in ignore_errors or []:
                    if isinstance(ex, ignored):
                        msg = (
                            u"A handled error occurred when calling '{func_name}' "
                            u"with arguments '{args}' and keyword arguments '{kwargs}': "
                            u"{exception}"
                        ).format(
                            func_name=func.func_name,
                            args=args,
                            kwargs=kwargs,
                            exception=ex.developer_message if hasattr(ex, 'developer_message') else repr(ex)
                        )
                        LOGGER.warning(msg)
                        raise

                caller = traceback.format_stack(limit=2)[0]

                # Otherwise, log the error and raise the API-specific error
                msg = (
                    u"An unexpected error occurred when calling '{func_name}' "
                    u"with arguments '{args}' and keyword arguments '{kwargs}' from {caller}: "
                    u"{exception}"
                ).format(
                    func_name=func.func_name,
                    args=args,
                    kwargs=kwargs,
                    exception=ex.developer_message if hasattr(ex, 'developer_message') else repr(ex),
                    caller=caller.strip(),
                )
                LOGGER.exception(msg)
                raise api_error(msg)

        return _wrapped

    return _decorator


def require_post_params(required_params):
    """
    View decorator that ensures the required POST params are
    present.  If not, returns an HTTP response with status 400.

    Args:
        required_params (list): The required parameter keys.

    Returns:
        HttpResponse

    """

    def _decorator(func):  # pylint: disable=missing-docstring
        @wraps(func)
        def _wrapped(*args, **_kwargs):  # pylint: disable=missing-docstring
            request = args[0]
            missing_params = set(required_params) - set(request.POST.keys())
            if len(missing_params) > 0:
                msg = u"Missing POST parameters: {missing}".format(
                    missing=", ".join(missing_params)
                )
                return HttpResponseBadRequest(msg)
            else:
                return func(request)

        return _wrapped

    return _decorator


class InvalidFieldError(Exception):
    """The provided field definition is not valid. """


class FormDescription(object):
    """Generate a JSON representation of a form. """

    ALLOWED_TYPES = ["text", "email", "select", "textarea", "checkbox", "plaintext", "password", "hidden"]

    ALLOWED_RESTRICTIONS = {
        "text": ["min_length", "max_length"],
        "password": ["min_length", "max_length", "upper", "lower", "digits", "punctuation", "non_ascii", "words",
                     "numeric", "alphabetic"],
        "email": ["min_length", "max_length", "readonly"],
    }

    FIELD_TYPE_MAP = {
        forms.CharField: "text",
        forms.PasswordInput: "password",
        forms.ChoiceField: "select",
        forms.TypedChoiceField: "select",
        forms.Textarea: "textarea",
        forms.BooleanField: "checkbox",
        forms.EmailField: "email",
    }

    OVERRIDE_FIELD_PROPERTIES = [
        "label", "type", "defaultValue", "placeholder",
        "instructions", "required", "restrictions",
        "options", "supplementalLink", "supplementalText"
    ]

    def __init__(self, method, submit_url):
        """Configure how the form should be submitted.

        Args:
            method (unicode): The HTTP method used to submit the form.
            submit_url (unicode): The URL where the form should be submitted.

        """
        self.method = method
        self.submit_url = submit_url
        self.fields = []
        self._field_overrides = defaultdict(dict)

    def add_field(
            self, name, label=u"", field_type=u"text", default=u"",
            placeholder=u"", instructions=u"", required=True, restrictions=None,
            options=None, include_default_option=False, error_messages=None,
            supplementalLink=u"", supplementalText=u""
    ):
        """Add a field to the form description.

        Args:
            name (unicode): The name of the field, which is the key for the value
                to send back to the server.

        Keyword Arguments:
            label (unicode): The label for the field (e.g. "E-mail" or "Username")

            field_type (unicode): The type of the field.  See `ALLOWED_TYPES` for
                acceptable values.

            default (unicode): The default value for the field.

            placeholder (unicode): Placeholder text in the field
                (e.g. "user@example.com" for an email field)

            instructions (unicode): Short instructions for using the field
                (e.g. "This is the email address you used when you registered.")

            required (boolean): Whether the field is required or optional.

            restrictions (dict): Validation restrictions for the field.
                See `ALLOWED_RESTRICTIONS` for acceptable values.

            options (list): For "select" fields, a list of tuples
                (value, display_name) representing the options available to
                the user.  `value` is the value of the field to send to the server,
                and `display_name` is the name to display to the user.
                If the field type is "select", you *must* provide this kwarg.

            include_default_option (boolean): If True, include a "default" empty option
                at the beginning of the options list.

            error_messages (dict): Custom validation error messages.
                Currently, the only supported key is "required" indicating
                that the messages should be displayed if the user does
                not provide a value for a required field.

            supplementalLink (unicode): A qualified URL to provide supplemental information
                for the form field. An example may be a link to documentation for creating
                strong passwords.

            supplementalText (unicode): The visible text for the supplemental link above.

        Raises:
            InvalidFieldError

        """
        if field_type not in self.ALLOWED_TYPES:
            msg = u"Field type '{field_type}' is not a valid type.  Allowed types are: {allowed}.".format(
                field_type=field_type,
                allowed=", ".join(self.ALLOWED_TYPES)
            )
            raise InvalidFieldError(msg)

        field_dict = {
            "name": name,
            "label": label,
            "type": field_type,
            "defaultValue": default,
            "placeholder": placeholder,
            "instructions": instructions,
            "required": required,
            "restrictions": {},
            "errorMessages": {},
            "supplementalLink": supplementalLink,
            "supplementalText": supplementalText
        }

        field_override = self._field_overrides.get(name, {})

        if field_type == "select":
            if options is not None:
                field_dict["options"] = []

                # Get an existing default value from the field override
                existing_default_value = field_override.get('defaultValue')

                # Include an empty "default" option at the beginning of the list;
                # preselect it if there isn't an overriding default.
                if include_default_option:
                    field_dict["options"].append({
                        "value": "",
                        "name": "--",
                        "default": existing_default_value is None
                    })
                field_dict["options"].extend([
                    {
                        'value': option_value,
                        'name': option_name,
                        'default': option_value == existing_default_value
                    } for option_value, option_name in options
                ])
            else:
                raise InvalidFieldError("You must provide options for a select field.")

        if restrictions is not None:
            allowed_restrictions = self.ALLOWED_RESTRICTIONS.get(field_type, [])
            for key, val in restrictions.iteritems():
                if key in allowed_restrictions:
                    field_dict["restrictions"][key] = val
                else:
                    msg = "Restriction '{restriction}' is not allowed for field type '{field_type}'".format(
                        restriction=key,
                        field_type=field_type
                    )
                    raise InvalidFieldError(msg)

        if error_messages is not None:
            field_dict["errorMessages"] = error_messages

        # If there are overrides for this field, apply them now.
        # Any field property can be overwritten (for example, the default value or placeholder)
        field_dict.update(field_override)

        self.fields.append(field_dict)

    def to_json(self):
        """Create a JSON representation of the form description.

        Here's an example of the output:
        {
            "method": "post",
            "submit_url": "/submit",
            "fields": [
                {
                    "name": "cheese_or_wine",
                    "label": "Cheese or Wine?",
                    "defaultValue": "cheese",
                    "type": "select",
                    "required": True,
                    "placeholder": "",
                    "instructions": "",
                    "options": [
                        {"value": "cheese", "name": "Cheese", "default": False},
                        {"value": "wine", "name": "Wine", "default": False}
                    ]
                    "restrictions": {},
                    "errorMessages": {},
                },
                {
                    "name": "comments",
                    "label": "comments",
                    "defaultValue": "",
                    "type": "text",
                    "required": False,
                    "placeholder": "Any comments?",
                    "instructions": "Please enter additional comments here."
                    "restrictions": {
                        "max_length": 200
                    }
                    "errorMessages": {},
                },
                ...
            ]
        }

        If the field is NOT a "select" type, then the "options"
        key will be omitted.

        Returns:
            unicode
        """
        return json.dumps({
            "method": self.method,
            "submit_url": self.submit_url,
            "fields": self.fields
        }, cls=LocalizedJSONEncoder)

    def override_field_properties(self, field_name, **kwargs):
        """Override properties of a field.

        The overridden values take precedence over the values provided
        to `add_field()`.

        Field properties not in `OVERRIDE_FIELD_PROPERTIES` will be ignored.

        Arguments:
            field_name (str): The name of the field to override.

        Keyword Args:
            Same as to `add_field()`.

        """
        # Transform kwarg "field_type" to "type" (a reserved Python keyword)
        if "field_type" in kwargs:
            kwargs["type"] = kwargs["field_type"]

        # Transform kwarg "default" to "defaultValue", since "default"
        # is a reserved word in JavaScript
        if "default" in kwargs:
            kwargs["defaultValue"] = kwargs["default"]

        self._field_overrides[field_name].update({
            property_name: property_value
            for property_name, property_value in kwargs.iteritems()
            if property_name in self.OVERRIDE_FIELD_PROPERTIES
        })


class LocalizedJSONEncoder(DjangoJSONEncoder):
    """
    JSON handler that evaluates ugettext_lazy promises.
    """

    # pylint: disable=method-hidden
    def default(self, obj):
        """
        Forces evaluation of ugettext_lazy promises.
        """
        if isinstance(obj, Promise):
            return force_text(obj)
        super(LocalizedJSONEncoder, self).default(obj)


def shim_student_view(view_func, check_logged_in=False):
    """Create a "shim" view for a view function from the student Django app.

    Specifically, we need to:
    * Strip out enrollment params, since the client for the new registration/login
        page will communicate with the enrollment API to update enrollments.

    * Return responses with HTTP status codes indicating success/failure
        (instead of always using status 200, but setting "success" to False in
        the JSON-serialized content of the response)

    * Use status code 403 to indicate a login failure.

    The shim will preserve any cookies set by the view.

    Arguments:
        view_func (function): The view function from the student Django app.

    Keyword Args:
        check_logged_in (boolean): If true, check whether the user successfully
            authenticated and if not set the status to 403.

    Returns:
        function

    """

    @wraps(view_func)
    def _inner(request):  # pylint: disable=missing-docstring
        # Make a copy of the current POST request to modify.

        modified_request = request.POST.copy()
        if isinstance(request, HttpRequest):
            # Works for an HttpRequest but not a rest_framework.request.Request.
            request.POST = modified_request
        else:
            # The request must be a rest_framework.request.Request.
            request._data = modified_request


        # if 'sdata' in request.Post:
        #     import base64, json, requests, hashlib
        #     from Crypto.Cipher import AES
        #     from django.template import loader
        #     from django.template.loader import render_to_string
        #     def _unpad(s):
        #         return s[:-ord(s[len(s) - 1:])]
        #
        #     enc = request.POST.get("sdata")
        #     enc = base64.b64decode(enc)
        #     ssokey = "oingisprettyintheworld1234567890"
        #     iv = "kmooctonewkmoocg"
        #
        #     cipher = AES.new(ssokey, AES.MODE_CBC, iv)
        #     dec = cipher.decrypt(enc)
        #     postdata = _unpad(dec).decode('utf-8').replace("'", '"')
        #     postdataarray = json.loads(postdata)
        #
        #     request.POST['email'] = postdataarray["email"]
        #     request.POST['password'] = postdataarray["password"]
        #     request.POST['stype'] = postdataarray["stype"]
        #     if 'backurl' in postdataarray:
        #         request.POST['backurl'] = postdataarray["backurl"]
        #     else:
        #         request.POST['backurl'] = ""



        # The login and registration handlers in student view try to change
        # the user's enrollment status if these parameters are present.
        # Since we want the JavaScript client to communicate directly with
        # the enrollment API, we want to prevent the student views from
        # updating enrollments.
        if "enrollment_action" in modified_request:
            del modified_request["enrollment_action"]
        if "course_id" in modified_request:
            del modified_request["course_id"]

        # Include the course ID if it's specified in the analytics info
        # so it can be included in analytics events.
        if "analytics" in modified_request:
            try:
                analytics = json.loads(modified_request["analytics"])
                if "enroll_course_id" in analytics:
                    modified_request["course_id"] = analytics.get("enroll_course_id")
            except (ValueError, TypeError):
                LOGGER.error(
                    u"Could not parse analytics object sent to user API: {analytics}".format(
                        analytics=analytics
                    )
                )

        # ------------------------------------------------------------------------------ 멀티사이트 로직 시작 [s]
        insert_lock = 0  # <----------- 변수 초기화
        error_lock = 0  # <------------ 변수 초기화
        duplication_lock = 0  # <------ 변수 초기화

        edx_useremail = request.POST['email']  # <----------------------- 로직에 이메일은 무조건 날라온다 (null exception 안남)
        try:
            u1 = User.objects.get(email=edx_useremail)  # <-- 잘못된 이메일이 날라오면 여기서 오류 (null exception)
        except BaseException:
            u1 = None  # <----------------------------------- 객체가 없을 경우 (null exception 처리)

        if u1 != None:
            edx_userid = u1.id  # <------------------- 객체를 정상적으로 얻어올 경우만 사용 (null exception 안남)
            edx_useremail = u1.email  # <------------------- 객체를 정상적으로 얻어올 경우만 사용 (null exception 안남)

        log.info('multisite check: multisite_userid in request.session [%s]' % 'multisite_userid' in request.session)
        log.info('multisite check: multisite_org in request.session [%s]' % 'multisite_org' in request.session)

        # passparam logic
        if 'multisite_userid' not in request.session and 'multisite_org' in request.session:
            multisite_org = request.session['multisite_org']

            with connections['default'].cursor() as cur:
                sql = '''
                    SELECT b.email
                      FROM multisite_member AS a
                      JOIN auth_user AS b
                      ON a.user_id = b.id
                      JOIN multisite as c
                      ON a.site_id = c.site_id
                     WHERE a.user_id = '{0}' and c.site_code = '{1}';
                '''.format(edx_userid, multisite_org)
                print sql
                cur.execute(sql)
                rows = cur.fetchall()
                # ----- 멀티사이트 멤버 테이블에 이미 등록된 이메일이 있는지 확인하기 위해 이메일 구해오는 쿼리 [e]
                try:
                    cnt = rows[0][0]  # <----- 멀티사이트 테이블에 이메일이 등록이 안되있을 경우 (null exception)
                except BaseException:
                    cnt = 0  # <----- 멀티사이트 테이블에 이메일이 등록이 안되있을 경우 (null exception 처리)

            log.info("multisite check cnt ---> %s" % cnt)
            print "cnt -> ", cnt
            print "cnt -> ", cnt

            if cnt != 0:  # 멀티사이트 이메일 있을 경우
                pass
            else:  # 멀티사이트 연동 이메일 없을 경우
                error_lock = 1
                request.POST['password'] = '61f5ca6828ed92eaa1d3df776e1dcaed@'

        # prameter logic
        if 'multisite_userid' in request.session and 'multisite_org' in request.session:  # <- 멀티사이트가 아닐 경우 (null exception 처리)
            multisite_userid = request.session['multisite_userid']
            multisite_org = request.session['multisite_org']

            if 'multisite_addinfo' in request.session:
                multisite_addinfo = request.session['multisite_addinfo']
            else:
                multisite_addinfo = ''

            logging.info("-----------------------------------------------")
            logging.info('multisite_userid -> %s' % multisite_userid)
            logging.info('multisite_org -> %s' % multisite_org)
            logging.info('multisite_addinfo -> %s' % multisite_addinfo)
            logging.info("-----------------------------------------------")

            # ----- 멀티사이트 멤버 테이블에 이미 등록된 이메일이 있는지 확인하기 위해 이메일 구해오는 쿼리 [s]
            with connections['default'].cursor() as cur:
                sql = '''
                    SELECT b.email
                      FROM multisite_member AS a
                      JOIN auth_user AS b
                      ON a.user_id = b.id
                      JOIN multisite as c
                      ON a.site_id = c.site_id
                     WHERE a.org_user_id = '{0}' and c.site_code = '{1}';
                '''.format(multisite_userid, multisite_org)
                cur.execute(sql)
                rows = cur.fetchall()
                # ----- 멀티사이트 멤버 테이블에 이미 등록된 이메일이 있는지 확인하기 위해 이메일 구해오는 쿼리 [e]
                try:
                    cnt = rows[0][0]  # <----- 멀티사이트 테이블에 이메일이 등록이 안되있을 경우 (null exception)
                except BaseException as e:
                    traceback.format_exc(e)
                    cnt = 0  # <----- 멀티사이트 테이블에 이메일이 등록이 안되있을 경우 (null exception 처리)

            # ----- 멀티사이트 멤버 테이블에 이메일이 있는 경우 로직 [s]
            if cnt != 0:
                # 다른 이메일 경우 테이블에 insert 수행하지 않으며, 경고메세지를 위해 이메일을 보안함
                if rows[0][0] != edx_useremail:
                    user_email = rows[0][0]
                    user_email_dic = user_email.split('@')
                    user_email = user_email_dic[0][0] + user_email_dic[0][1] + '********@' + user_email_dic[1]

                    error_lock = 1  # 경고메세지 변경 플래그
                    insert_lock = 1  # insert 방지 플래그

                    request.POST['password'] = '61f5ca6828ed92eaa1d3df776e1dcaed@'  # 로그인 세션 등록을 방지하기 위한 코드

                # 같은 이메일이 경우 테이블에 insert만 수행하지 않게 만든다.
                elif rows[0][0] == edx_useremail:
                    insert_lock = 1  # insert 방지 플래그
            # ----- 멀티사이트 멤버 테이블에 이메일이 있는 경우 로직 [e]

            """
            로그인 성공여부를 먼저 체크한 후 연계 동의 받도록 수정요청
            연계기관 사이트에서 버튼 클릭해서 넘어왔다가, 창 닫고 다시 연계기관 사이트에서 버튼 클릭하면 로그인페이지가 아닌 연계기관사이트 메인으로 넘어간다고 합니다. 확인필요.            
            """

            # insert 방지 플래그가 설정되지 않은 경우 멀티사이트멤버 테이블에 데이터를 insert 한다.
            if insert_lock == 0:
                with connections['default'].cursor() as cur:
                    sql = '''
                        insert into multisite_member(site_id, user_id, org_user_id, regist_id, addinfo)
                        select site_id, {1}, '{2}', {1}, '{3}'
                        from multisite
                        where site_code = '{0}'
                    '''.format(multisite_org, edx_userid, multisite_userid, multisite_addinfo)
                    try:
                        print sql
                        cur.execute(sql)  # <--------------------------- 다른 사번으로 이미 등록된 이메일을 등록하려고 시도하는 경우 (에러)
                    except BaseException as e:
                        traceback.format_exc(e)
                        duplication_lock = 1  # <----------------------- 경고메세지 변경 플래그
                        request.POST['password'] = '61f5ca6828ed92eaa1d3df776e1dcaed'  # 로그인 세션 등록을 방지하기 위한 코드

        # ------------------------------------------------------------------------------ 멀티사이트 로직 종료 [e]

        response = view_func(request)  # <--------------------- 로그인 세션 올리는 부분

        # Most responses from this view are JSON-encoded
        # dictionaries with keys "success", "value", and
        # (sometimes) "redirect_url".
        #
        # We want to communicate some of this information
        # using HTTP status codes instead.
        #
        # We ignore the "redirect_url" parameter, because we don't need it:
        # 1) It's used to redirect on change enrollment, which
        # our client will handle directly
        # (that's why we strip out the enrollment params from the request)
        # 2) It's used by third party auth when a user has already successfully
        # authenticated and we're not sending login credentials.  However,
        # this case is never encountered in practice: on the old login page,
        # the login form would be submitted directly, so third party auth
        # would always be "trumped" by first party auth.  If a user has
        # successfully authenticated with us, we redirect them to the dashboard
        # regardless of how they authenticated; and if a user is completing
        # the third party auth pipeline, we redirect them from the pipeline
        # completion end-point directly.

        try:
            response_dict = json.loads(response.content)
            msg = response_dict.get("value", u"")
            success = response_dict.get("success")
        except (ValueError, TypeError):
            msg = response.content
            success = True

        # ------------------------------------------------------------------------------ 멀티사이트 로직 종료 [s]
        if 'multisite_userid' in request.session and 'multisite_org' in request.session:  # <- 멀티사이트가 아닐 경우 (null exception 처리)
            if error_lock == 1:
                msg = "이미 등록되어 있는 사용자 입니다. {0}".format(user_email)
            if duplication_lock == 1:
                msg = "다른 사번으로 이미 등록되어 있는 사용자 입니다."

        if 'multisite_userid' not in request.session and 'multisite_org' in request.session:  # <- 멀티사이트가 아닐 경우 (null exception 처리)
            if error_lock == 1:
                msg = "기관연계가 되어있지 않은 사용자 입니다."
        # ------------------------------------------------------------------------------ 멀티사이트 로직 종료 [e]

        # If the user is not authenticated when we expect them to be
        # send the appropriate status code.
        # We check whether the user attribute is set to make
        # it easier to test this without necessarily running
        # the request through authentication middleware.

        is_authenticated = (
            getattr(request, 'user', None) is not None
            and request.user.is_authenticated
        )
        if check_logged_in and not is_authenticated:
            # If we get a 403 status code from the student view
            # this means we've successfully authenticated with a
            # third party provider, but we don't have a linked
            # EdX account.  Send a helpful error code so the client
            # knows this occurred.
            if response.status_code == 403:
                response.content = "third-party-auth"

            # Otherwise, it's a general authentication failure.
            # Ensure that the status code is a 403 and pass
            # along the message from the view.
            else:
                response.status_code = 403
                response.content = msg

        # If an error condition occurs, send a status 400
        elif response.status_code != 200 or not success:
            # The student views tend to send status 200 even when an error occurs
            # If the JSON-serialized content has a value "success" set to False,
            # then we know an error occurred.
            if response.status_code == 200:
                response.status_code = 400
            response.content = msg

        # If the response is successful, then return the content
        # of the response directly rather than including it
        # in a JSON-serialized dictionary.
        else:
            response.content = msg

        # Return the response, preserving the original headers.
        # This is really important, since the student views set cookies
        # that are used elsewhere in the system (such as the marketing site).

        from django.conf import settings
        from Crypto.Cipher import AES
        from Crypto.Random import get_random_bytes
        import hashlib, time, base64, urllib
        from django.http import JsonResponse

        bs = 16
        key = settings.XINICS_KEY
        iv = settings.XINICS_IV

        print "AES SETTING bs =====> ",bs
        print "AES SETTING key =====> ",key
        print "AES SETTING iv =====> ",iv
        print "AES SETTING email =====> ",request.POST.get("email")
        print "AES SETTING password =====> ",request.POST.get("password")

        key = hashlib.sha256(key.encode("UTF-8")).digest()
        iv = iv.encode("UTF-8")

        def _pad(s):
            return s + (bs - len(s) % bs) * chr(bs - len(s) % bs)


        def encryptmake(raw):
            raw = _pad(raw)
            cipher = AES.new(key, AES.MODE_CBC, iv)
            return cipher.encrypt(raw)

        def _pad(s):
            return s + (bs - len(s) % bs) * chr(bs - len(s) % bs)
        def ssoencrypt(raw):
            raw = _pad(raw)
            ssokey = "oingisprettyintheworld1234567890"
            iv = "kmooctonewkmoocg"

            cipher = AES.new(ssokey, AES.MODE_CBC, iv)
            return cipher.encrypt(raw)

        ssocipher = ssoencrypt(json.dumps({"email": request.POST.get("email"), "password": request.POST.get("password"), "stype": "ssologin"}))
        ssocipher = base64.b64encode(ssocipher)

        enc = encryptmake(json.dumps({"timestamp": int(time.time()), "uid": request.user.id}))
        enc = base64.b64encode(enc)
        # enc = urllib.quote(enc, safe='')

        # if request.POST['backurl']:
        #     from django.shortcuts import redirect
        #     return redirect(request.POST['backurl'])
        # # elif request.POST["sdata"]:
        # #     return redirect("http://www.kmooc.kr")
        # else:
        if response.content:
            return response
        else:
            return JsonResponse({"data": enc,"ssodata": ssocipher})

    return _inner


def serializer_is_dirty(preference_serializer):
    """
    Return True if saving the supplied (Raw)UserPreferenceSerializer would change the database.
    """
    return (
            preference_serializer.instance is None or
            preference_serializer.instance.value != preference_serializer.validated_data['value']
    )
