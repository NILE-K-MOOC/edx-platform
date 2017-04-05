# -*- coding: utf-8 -*-
"""Views for API management."""
import logging
from django.conf import settings
from django.contrib.sites.shortcuts import get_current_site
from django.core.urlresolvers import reverse_lazy, reverse
from django.http.response import JsonResponse
from django.shortcuts import redirect
from django.views.generic import View
from django.views.generic.base import TemplateView
from django.views.generic.edit import CreateView
from oauth2_provider.generators import generate_client_secret, generate_client_id
from oauth2_provider.models import get_application_model
from oauth2_provider.views import ApplicationRegistration
from slumber.exceptions import HttpNotFoundError
from edxmako.shortcuts import render_to_response
from openedx.core.djangoapps.api_admin.decorators import require_api_access
from openedx.core.djangoapps.api_admin.forms import ApiAccessRequestForm, CatalogForm
from openedx.core.djangoapps.api_admin.models import ApiAccessRequest, Catalog
from openedx.core.djangoapps.api_admin.utils import course_discovery_api_client
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

log = logging.getLogger(__name__)

Application = get_application_model()  # pylint: disable=invalid-name

# Changelist settings
ALL_VAR = 'all'
ORDER_VAR = 'o'
ORDER_TYPE_VAR = 'ot'
PAGE_VAR = 'p'
SEARCH_VAR = 'q'
ERROR_FLAG = 'e'


def get_meta_json(self, request, mode=0, message=None):
    meta = {}
    """
    mode:
        0 - 조회
        1 - 추가
        2 - 수정
        3 - 삭제
    """

    meta['system'] = 'K-MOOC'
    meta['ip'] = request.META.get('REMOTE_ADDR')
    meta['path'] = request.path
    meta['message'] = ''

    if hasattr(self, 'result_count'):
        meta['count'] = self.result_count

    if request.method == 'GET':
        meta['query'] = request.META.get('QUERY_STRING')
    elif request.method == 'POST':
        meta['query'] = request.POST.dict()
    else:
        meta['query'] = ''

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
            content_type_id=3,
            object_id=request.user.pk,
            object_repr='auth_user_list_select',
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

    LogEntry.objects.log_action(
        user_id=request.user.pk,
        content_type_id=3,
        object_id=request.user.pk,
        object_repr='auth_user_info_select',
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


ModelAdmin.log_addition = custom_log_addition
ModelAdmin.log_change = custom_log_change
ModelAdmin.log_deletion = custom_log_deletion
ChangeList.__init__ = custom_init
UserAdmin.get_form = custom_get_form


class PrivacyLog(View):
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

    def get(self, request):
        pass

    def post(self, request):

        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0]
        else:
            ip = request.META.get('REMOTE_ADDR')

        print '--- PrivacyLog post called s ---------------'
        user = request.user
        print user.is_authenticated()
        print ip
        print user.id
        print user.username
        print user.email
        print request
        print request.body
        print request.POST['filename']
        print '--- PrivacyLog post called e ---------------'

        LogEntry.objects.log_action(
            user_id=request.user.pk,
            content_type_id=51,
            object_id=request.user.pk,
            object_repr='file download:%s' % request.POST['filename'],
            action_flag=ADDITION
        )

        return JsonResponse({'result': True})


class ApiRequestView(CreateView):
    """Form view for requesting API access."""
    form_class = ApiAccessRequestForm
    template_name = 'api_admin/api_access_request_form.html'
    success_url = reverse_lazy('api_admin:api-status')

    def get(self, request):
        print 'ApiRequestView get called'
        """
        If the requesting user has already requested API access, redirect
        them to the client creation page.
        """
        if ApiAccessRequest.api_access_status(request.user) is not None:
            return redirect(reverse('api_admin:api-status'))
        return super(ApiRequestView, self).get(request)

    def form_valid(self, form):
        form.instance.user = self.request.user
        form.instance.site = get_current_site(self.request)
        return super(ApiRequestView, self).form_valid(form)


class ApiRequestStatusView(ApplicationRegistration):
    """View for confirming our receipt of an API request."""

    success_url = reverse_lazy('api_admin:api-status')

    def get(self, request, form=None):  # pylint: disable=arguments-differ
        print 'ApiRequestStatusView get called'
        """
        If the user has not created an API request, redirect them to the
        request form. Otherwise, display the status of their API
        request. We take `form` as an optional argument so that we can
        display validation errors correctly on the page.
        """
        if form is None:
            form = self.get_form_class()()

        user = request.user
        try:
            api_request = ApiAccessRequest.objects.get(user=user)
        except ApiAccessRequest.DoesNotExist:
            return redirect(reverse('api_admin:api-request'))
        try:
            application = Application.objects.get(user=user)
        except Application.DoesNotExist:
            application = None

        # We want to fill in a few fields ourselves, so remove them
        # from the form so that the user doesn't see them.
        for field in ('client_type', 'client_secret', 'client_id', 'authorization_grant_type'):
            form.fields.pop(field)

        return render_to_response('api_admin/status.html', {
            'status': api_request.status,
            'api_support_link': settings.API_DOCUMENTATION_URL,
            'api_support_email': settings.API_ACCESS_MANAGER_EMAIL,
            'form': form,
            'application': application,
        })

    def get_form(self, form_class=None):
        form = super(ApiRequestStatusView, self).get_form(form_class)
        # Copy the data, since it's an immutable QueryDict.
        copied_data = form.data.copy()
        # Now set the fields that were removed earlier. We give them
        # confidential client credentials, and generate their client
        # ID and secret.
        copied_data.update({
            'authorization_grant_type': Application.GRANT_CLIENT_CREDENTIALS,
            'client_type': Application.CLIENT_CONFIDENTIAL,
            'client_secret': generate_client_secret(),
            'client_id': generate_client_id(),
        })
        form.data = copied_data
        return form

    def form_valid(self, form):
        # Delete any existing applications if the user has decided to regenerate their credentials
        Application.objects.filter(user=self.request.user).delete()
        return super(ApiRequestStatusView, self).form_valid(form)

    def form_invalid(self, form):
        return self.get(self.request, form)

    @require_api_access
    def post(self, request):
        return super(ApiRequestStatusView, self).post(request)


class ApiTosView(TemplateView):
    """View to show the API Terms of Service."""

    template_name = 'api_admin/terms_of_service.html'


class CatalogSearchView(View):
    """View to search for catalogs belonging to a user."""

    def get(self, request):
        print 'CatalogSearchView get called'
        """Display a form to search for catalogs belonging to a user."""
        return render_to_response('api_admin/catalogs/search.html')

    def post(self, request):
        """Redirect to the list view for the given user."""
        username = request.POST.get('username')
        # If no username is provided, bounce back to this page.
        if not username:
            return redirect(reverse('api_admin:catalog-search'))
        return redirect(reverse('api_admin:catalog-list', kwargs={'username': username}))


class CatalogListView(View):
    """View to list existing catalogs and create new ones."""

    template = 'api_admin/catalogs/list.html'

    def _get_catalogs(self, client, username):
        """Retrieve catalogs for a user. Returns the empty list if none are found."""
        try:
            response = client.catalogs.get(username=username)
            return [Catalog(attributes=catalog) for catalog in response['results']]
        except HttpNotFoundError:
            return []

    def get_context_data(self, client, username, form):
        """ Retrieve context data for the template. """

        return {
            'username': username,
            'catalogs': self._get_catalogs(client, username),
            'form': form,
            'preview_url': reverse('api_admin:catalog-preview'),
            'catalog_api_catalog_endpoint': client.catalogs.url().rstrip('/'),
            'catalog_api_url': client.courses.url(),
        }

    def get(self, request, username):
        print 'CatalogListView get called'
        """Display a list of a user's catalogs."""
        client = course_discovery_api_client(request.user)
        form = CatalogForm(initial={'viewers': [username]})
        return render_to_response(self.template, self.get_context_data(client, username, form))

    def post(self, request, username):
        """Create a new catalog for a user."""
        form = CatalogForm(request.POST)
        client = course_discovery_api_client(request.user)
        if not form.is_valid():
            return render_to_response(self.template, self.get_context_data(client, username, form), status=400)

        attrs = form.instance.attributes
        catalog = client.catalogs.post(attrs)
        return redirect(reverse('api_admin:catalog-edit', kwargs={'catalog_id': catalog['id']}))


class CatalogEditView(View):
    """View to edit an individual catalog."""

    template_name = 'api_admin/catalogs/edit.html'

    def get_context_data(self, catalog, form, client):
        """ Retrieve context data for the template. """

        return {
            'catalog': catalog,
            'form': form,
            'preview_url': reverse('api_admin:catalog-preview'),
            'catalog_api_url': client.courses.url(),
            'catalog_api_catalog_endpoint': client.catalogs.url().rstrip('/'),
        }

    def get(self, request, catalog_id):
        print 'CatalogEditView get called'
        """Display a form to edit this catalog."""
        client = course_discovery_api_client(request.user)
        response = client.catalogs(catalog_id).get()
        catalog = Catalog(attributes=response)
        form = CatalogForm(instance=catalog)
        return render_to_response(self.template_name, self.get_context_data(catalog, form, client))

    def post(self, request, catalog_id):
        """Update or delete this catalog."""
        client = course_discovery_api_client(request.user)
        if request.POST.get('delete-catalog') == 'on':
            client.catalogs(catalog_id).delete()
            return redirect(reverse('api_admin:catalog-search'))
        form = CatalogForm(request.POST)
        if not form.is_valid():
            response = client.catalogs(catalog_id).get()
            catalog = Catalog(attributes=response)
            return render_to_response(self.template_name, self.get_context_data(catalog, form, client), status=400)
        catalog = client.catalogs(catalog_id).patch(form.instance.attributes)
        return redirect(reverse('api_admin:catalog-edit', kwargs={'catalog_id': catalog['id']}))


class CatalogPreviewView(View):
    """Endpoint to preview courses for a query."""

    def get(self, request):
        print 'CatalogPreviewView get called'
        """
        Return the results of a query against the course catalog API. If no
        query parameter is given, returns an empty result set.
        """
        client = course_discovery_api_client(request.user)
        # Just pass along the request params including limit/offset pagination
        if 'q' in request.GET:
            results = client.courses.get(**request.GET)
        # Ensure that we don't just return all the courses if no query is given
        else:
            results = {'count': 0, 'results': [], 'next': None, 'prev': None}
        return JsonResponse(results)
