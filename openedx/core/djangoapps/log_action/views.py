# -*- coding: utf-8 -*-
from django.http.response import JsonResponse
from django.views.generic import View
from django.contrib.admin.models import LogEntry, ADDITION, CHANGE, DELETION
from django.contrib.admin.options import get_content_type_for_model
from django.contrib.admin.options import ModelAdmin
from django.utils.encoding import force_text
from django.contrib.admin.views.main import ChangeList
from django.contrib.admin.options import (
    IS_POPUP_VAR, TO_FIELD_VAR
)
from django.contrib.admin.exceptions import DisallowedModelAdminToField
from django.utils.translation import ugettext
from django.contrib.auth.admin import UserAdmin

# Changelist settings
ALL_VAR = 'all'
ORDER_VAR = 'o'
ORDER_TYPE_VAR = 'ot'
PAGE_VAR = 'p'
SEARCH_VAR = 'q'
ERROR_FLAG = 'e'


def get_meta_json(self, request, mode=0, message=None, count=None):
    meta = {}
    """
    mode:
        0 - 조회
        1 - 추가
        2 - 수정
        3 - 삭제
    """
    if not count:
        count = 1
    meta['system'] = 'K-MOOC'
    meta['ip'] = request.META.get('REMOTE_ADDR')
    meta['path'] = request.path
    meta['method'] = request.method

    if message:
        meta['message'] = message

    if count:
        meta['count'] = count

    if request.method == 'GET':
        meta['query'] = request.META.get('QUERY_STRING')
    elif request.method == 'POST':
        param_dict = request.POST.dict()
        meta['query'] = param_dict

        if hasattr(request, 'json'):
            meta['query'] = request.json

        if 'identifiers' in param_dict:
            arr = param_dict.get('identifiers').split(',')
            count = len(arr)

    else:
        meta['query'] = ''

    if hasattr(self, 'result_count'):
        count = self.result_count

    meta['count'] = count

    print 'meta s ----------------------------------'
    print meta
    print 'meta e ----------------------------------'

    return meta


def custom_init(self, request, model, list_display, list_display_links,
                list_filter, date_hierarchy, search_fields, list_select_related,
                list_per_page, list_max_show_all, list_editable, model_admin):
    print 'CUSTOM LOG ACTION [custom_init]'
    self.model = model
    self.opts = model._meta
    self.lookup_opts = self.opts
    self.root_queryset = model_admin.get_queryset(request)
    self.list_display = list_display
    self.list_display_links = list_display_links
    self.list_filter = list_filter
    self.date_hierarchy = date_hierarchy
    self.search_fields = search_fields
    self.list_select_related = list_select_related
    self.list_per_page = list_per_page
    self.list_max_show_all = list_max_show_all
    self.model_admin = model_admin
    self.preserved_filters = model_admin.get_preserved_filters(request)

    # Get search parameters from the query string.
    try:
        self.page_num = int(request.GET.get(PAGE_VAR, 0))
    except ValueError:
        self.page_num = 0
    self.show_all = ALL_VAR in request.GET
    self.is_popup = IS_POPUP_VAR in request.GET
    to_field = request.GET.get(TO_FIELD_VAR)
    if to_field and not model_admin.to_field_allowed(request, to_field):
        raise DisallowedModelAdminToField("The field %s cannot be referenced." % to_field)
    self.to_field = to_field
    self.params = dict(request.GET.items())
    if PAGE_VAR in self.params:
        del self.params[PAGE_VAR]
    if ERROR_FLAG in self.params:
        del self.params[ERROR_FLAG]

    if self.is_popup:
        self.list_editable = ()
    else:
        self.list_editable = list_editable
    self.query = request.GET.get(SEARCH_VAR, '')
    self.queryset = self.get_queryset(request)
    self.get_results(request)
    if self.is_popup:
        title = ugettext('Select %s')
    else:
        title = ugettext('Select %s to change')
    self.title = title % force_text(self.opts.verbose_name)
    self.pk_attname = self.lookup_opts.pk.attname

    print 'request.path:', request.path

    if request.path == '/admin/auth/user/':
        LogEntry.objects.log_action(
            user_id=request.user.pk,
            content_type_id=292,
            object_id=0,
            object_repr='auth_user_list',
            action_flag=0,
            change_message=get_meta_json(self, request)
        )


def custom_get_form(self, request, obj=None, **kwargs):
    print 'CUSTOM LOG ACTION [custom_get_form]'
    """
    Use special form during user creation
    """
    defaults = {}
    if obj is None:
        defaults['form'] = self.add_form
    defaults.update(kwargs)

    path = request.path
    path_list = path.split('/')
    target_id = ''
    for val in path_list:
        if val:
            print 'val:', val
            target_id = val

    from django.contrib.auth.models import User
    user = User.objects.get(id=target_id)

    if request.method == 'GET':
        LogEntry.objects.log_action(
            user_id=request.user.pk,
            content_type_id=291,
            object_id=0,
            object_repr='auth_user_info[student:%s]' % user.username,
            action_flag=0,
            change_message=get_meta_json(self, request)
        )

    return super(UserAdmin, self).get_form(request, obj, **defaults)


def custom_log_addition(self, request, object):
    print 'CUSTOM LOG ACTION [custom_log_addition]'
    """
    Log that an object has been successfully added.

    The default implementation creates an admin LogEntry object.
    """
    LogEntry.objects.log_action(
        user_id=request.user.pk,
        content_type_id=get_content_type_for_model(object).pk,
        object_id=object.pk,
        object_repr=force_text(object),
        action_flag=ADDITION,
        change_message=get_meta_json(self, request, mode=ADDITION)
    )


def custom_log_change(self, request, object, message):
    print 'CUSTOM LOG ACTION [custom_log_change]'
    """
    Log that an object has been successfully changed.

    The default implementation creates an admin LogEntry object.
    """
    LogEntry.objects.log_action(
        user_id=request.user.pk,
        content_type_id=get_content_type_for_model(object).pk,
        object_id=object.pk,
        object_repr=force_text(object),
        action_flag=CHANGE,
        change_message=get_meta_json(self, request, mode=CHANGE, message=message)
    )


def custom_log_deletion(self, request, object, object_repr):
    print 'CUSTOM LOG ACTION [custom_log_deletion]'
    """
    Log that an object will be deleted. Note that this method must be
    called before the deletion.

    The default implementation creates an admin LogEntry object.
    """
    LogEntry.objects.log_action(
        user_id=request.user.pk,
        content_type_id=get_content_type_for_model(object).pk,
        object_id=object.pk,
        object_repr=object_repr,
        action_flag=DELETION,
        change_message=get_meta_json(self, request, mode=DELETION)
    )


class LogAction(View):
    """
    --> student_courseaccessrole
    -- staff : 운영팀
    -- instructor : 교수자
    -- beta_testers : 베타테스터

    --> django_comment_client_role_users, django_comment_client_role
    -- Administrator : 게시판 관리자
    -- Moderator : 토의진행
    -- Community TA : 게시판 커뮤니티 조교
    """

    def __init__(self):
        print 'LogAction __init__ called'
        ModelAdmin.log_addition = custom_log_addition
        ModelAdmin.log_change = custom_log_change
        ModelAdmin.log_deletion = custom_log_deletion
        ChangeList.__init__ = custom_init
        UserAdmin.get_form = custom_get_form

    def get(self, request):
        pass

    def post(self, request):
        LogEntry.objects.log_action(
            user_id=request.user.pk,
            content_type_id=297,
            object_id=0,
            object_repr='file download[filename:%s]' % request.POST['filename'],
            action_flag=ADDITION,
            change_message=get_meta_json(self, request, mode=ADDITION)
        )
        return JsonResponse({'result': True})
