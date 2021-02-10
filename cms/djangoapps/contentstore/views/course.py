# -*- coding: utf-8 -*-
"""
Views related to operations on course objects
"""
import copy
import json
import logging
import random
import re
import string  # pylint: disable=deprecated-module
import sys

import MySQLdb as mdb
import django.utils
import six
from ccx_keys.locator import CCXLocator
from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied, ValidationError
# from django.urls import reverse
from django.core.urlresolvers import reverse
from django.http import Http404, HttpResponse, HttpResponseBadRequest, HttpResponseNotFound
from django.shortcuts import redirect
from django.utils.translation import ugettext as _
from django.views.decorators.csrf import ensure_csrf_cookie
from django.views.decorators.http import require_GET, require_http_methods
from opaque_keys import InvalidKeyError
from opaque_keys.edx.keys import CourseKey
from opaque_keys.edx.locations import Location

from contentstore import utils
from contentstore.course_group_config import (
    COHORT_SCHEME,
    ENROLLMENT_SCHEME,
    RANDOM_SCHEME,
    GroupConfiguration,
    GroupConfigurationsValidationError
)
from lms.djangoapps.courseware.courses import get_course_with_access
from opaque_keys.edx.locator import BlockUsageLocator
from openedx.core.djangoapps.content.course_overviews.models import CourseOverview
from openedx.core.djangoapps.waffle_utils import WaffleSwitchNamespace
from openedx.features.course_experience.waffle import waffle as course_experience_waffle
from openedx.features.course_experience.waffle import ENABLE_COURSE_ABOUT_SIDEBAR_HTML
from six import text_type

from contentstore.course_info_model import delete_course_update, get_course_updates, update_course_updates
from contentstore.courseware_index import CoursewareSearchIndexer, SearchIndexingError
from contentstore.push_notification import push_notification_enabled
from contentstore.tasks import rerun_course as rerun_course_task
from contentstore.tasks import rerun_course
from contentstore.utils import (
    add_instructor,
    get_lms_link_for_item,
    initialize_permissions,
    remove_all_instructors,
    reverse_course_url,
    reverse_library_url,
    reverse_url,
    reverse_usage_url
)
from contentstore.views.entrance_exam import (
    create_entrance_exam,
    delete_entrance_exam,
    update_entrance_exam,
)
from course_action_state.managers import CourseActionStateItemNotFoundError
from course_action_state.models import CourseRerunState, CourseRerunUIStateManager
from course_creators.views import add_user_with_status_unrequested, get_course_creator_status
from edxmako.shortcuts import render_to_response
from milestones import api as milestones_api
from models.settings.course_grading import CourseGradingModel
from models.settings.course_metadata import CourseMetadata
from models.settings.encoder import CourseSettingsEncoder
from openedx.core.djangoapps.content.course_structures.api.v0 import api, errors

from openedx.core.djangoapps.credit.api import get_credit_requirements, is_credit_course
from openedx.core.djangoapps.credit.tasks import update_credit_course_requirements
from openedx.core.djangoapps.models.course_details import CourseDetails
from openedx.core.djangoapps.programs.models import ProgramsApiConfig
from openedx.core.djangoapps.programs.utils import get_programs
from openedx.core.djangoapps.self_paced.models import SelfPacedConfiguration

from openedx.core.djangoapps.site_configuration import helpers as configuration_helpers
from openedx.core.djangolib.js_utils import dump_js_escaped_json
from openedx.core.lib.course_tabs import CourseTabPluginManager
from openedx.core.lib.courses import course_image_url
from student import auth
from student.auth import has_course_author_access, has_studio_read_access, has_studio_write_access
from student.roles import CourseCreatorRole, CourseInstructorRole, CourseStaffRole, GlobalStaff, UserBasedRole
from util.course import get_link_for_about_page
from util.date_utils import get_default_time_display
from util.json_request import JsonResponse, JsonResponseBadRequest, expect_json
from util.milestones_helpers import (
    is_entrance_exams_enabled,
    is_prerequisite_courses_enabled,
    is_valid_course_key,
    remove_prerequisite_course,
    set_prerequisite_courses
)
from util.organizations_helpers import add_organization_course, get_organization_by_short_name, organizations_enabled
from util.string_utils import _has_non_ascii_characters
from xblock_django.api import deprecated_xblocks
from xmodule.contentstore.content import StaticContent
from xmodule.course_module import DEFAULT_START_DATE, CourseFields
from xmodule.error_module import ErrorDescriptor
from xmodule.modulestore import EdxJSONEncoder
from xmodule.modulestore.django import modulestore
from xmodule.modulestore.exceptions import DuplicateCourseError, ItemNotFoundError
from xmodule.tabs import CourseTab, CourseTabList, InvalidTabsException

from .component import ADVANCED_COMPONENT_TYPES
from .item import create_xblock_info
from .library import LIBRARIES_ENABLED, get_library_creator_status

from django.db import connections
from pymongo import MongoClient
from bson import ObjectId

from pymongo import MongoClient
from bson import ObjectId
from datetime import datetime
from pytz import utc

log = logging.getLogger(__name__)

__all__ = ['course_info_handler', 'course_handler', 'course_listing', 'level_Verifi',
           'course_info_update_handler', 'course_search_index_handler',
           'course_rerun_handler',
           'settings_handler',
           'grading_handler',
           'advanced_settings_handler',
           'course_notifications_handler',
           'textbooks_list_handler', 'textbooks_detail_handler',
           'group_configurations_list_handler', 'group_configurations_detail_handler'
           ]

WAFFLE_NAMESPACE = 'studio_home'


class AccessListFallback(Exception):
    """
    An exception that is raised whenever we need to `fall back` to fetching *all* courses
    available to a user, rather than using a shorter method (i.e. fetching by group)
    """
    pass


def get_course_and_check_access(course_key, user, depth=0):
    """
    Internal method used to calculate and return the locator and course module
    for the view functions in this file.
    """
    if not has_studio_read_access(user, course_key):
        raise PermissionDenied()
    course_module = modulestore().get_course(course_key, depth=depth)
    return course_module


def reindex_course_and_check_access(course_key, user):
    """
    Internal method used to restart indexing on a course.
    """
    if not has_course_author_access(user, course_key):
        raise PermissionDenied()
    return CoursewareSearchIndexer.do_course_reindex(modulestore(), course_key)


@login_required
def course_notifications_handler(request, course_key_string=None, action_state_id=None):
    """
    Handle incoming requests for notifications in a RESTful way.

    course_key_string and action_state_id must both be set; else a HttpBadResponseRequest is returned.

    For each of these operations, the requesting user must have access to the course;
    else a PermissionDenied error is returned.

    GET
        json: return json representing information about the notification (action, state, etc)
    DELETE
        json: return json repressing success or failure of dismissal/deletion of the notification
    PUT
        Raises a NotImplementedError.
    POST
        Raises a NotImplementedError.
    """
    # ensure that we have a course and an action state
    if not course_key_string or not action_state_id:
        return HttpResponseBadRequest()

    response_format = request.GET.get('format') or request.POST.get('format') or 'html'

    course_key = CourseKey.from_string(course_key_string)

    if response_format == 'json' or 'application/json' in request.META.get('HTTP_ACCEPT', 'application/json'):
        if not has_studio_write_access(request.user, course_key):
            raise PermissionDenied()
        if request.method == 'GET':
            return _course_notifications_json_get(action_state_id)
        elif request.method == 'DELETE':
            # we assume any delete requests dismiss actions from the UI
            return _dismiss_notification(request, action_state_id)
        elif request.method == 'PUT':
            raise NotImplementedError()
        elif request.method == 'POST':
            raise NotImplementedError()
        else:
            return HttpResponseBadRequest()
    else:
        return HttpResponseNotFound()


def _course_notifications_json_get(course_action_state_id):
    """
    Return the action and the action state for the given id
    """
    try:
        action_state = CourseRerunState.objects.find_first(id=course_action_state_id)
    except CourseActionStateItemNotFoundError:
        return HttpResponseBadRequest()

    action_state_info = {
        'action': action_state.action,
        'state': action_state.state,
        'should_display': action_state.should_display
    }
    return JsonResponse(action_state_info)


def level_Verifi(request):
    # sys.setdefaultencoding('utf-8')
    con = mdb.connect(settings.DATABASES.get('default').get('HOST'),
                      settings.DATABASES.get('default').get('USER'),
                      settings.DATABASES.get('default').get('PASSWORD'),
                      settings.DATABASES.get('default').get('NAME'),
                      charset='utf8')
    cur = con.cursor()
    level_1 = request.GET.get('level_1')
    level_2 = request.GET.get('level_2')

    query = """
        SELECT count(*)
          FROM course_overviews_courseoverview
         WHERE org = '{0}' AND display_number_with_default = '{1}';
    """.format(level_1, level_2)
    cur.execute(query)
    check_index = cur.fetchall()
    cur.close()

    data = json.dumps(check_index[0][0])
    return HttpResponse(data, 'applications/json')


def _dismiss_notification(request, course_action_state_id):  # pylint: disable=unused-argument
    """
    Update the display of the course notification
    """
    try:
        action_state = CourseRerunState.objects.find_first(id=course_action_state_id)

    except CourseActionStateItemNotFoundError:
        # Can't dismiss a notification that doesn't exist in the first place
        return HttpResponseBadRequest()

    if action_state.state == CourseRerunUIStateManager.State.FAILED:
        # We remove all permissions for this course key at this time, since
        # no further access is required to a course that failed to be created.
        remove_all_instructors(action_state.course_key)

    # The CourseRerunState is no longer needed by the UI; delete
    action_state.delete()

    return JsonResponse({'success': True})


# pylint: disable=unused-argument
@login_required
def course_handler(request, course_key_string=None):
    """
    The restful handler for course specific requests.
    It provides the course tree with the necessary information for identifying and labeling the parts. The root
    will typically be a 'course' object but may not be especially as we support modules.

    GET
        html: return course listing page if not given a course id
        html: return html page overview for the given course if given a course id
        json: return json representing the course branch's index entry as well as dag w/ all of the children
        replaced w/ json docs where each doc has {'_id': , 'display_name': , 'children': }
    POST
        json: create a course, return resulting json
        descriptor (same as in GET course/...). Leaving off /branch/draft would imply create the course w/ default
        branches. Cannot change the structure contents ('_id', 'display_name', 'children') but can change the
        index entry.
    PUT
        json: update this course (index entry not xblock) such as repointing head, changing display name, org,
        course, run. Return same json as above.
    DELETE
        json: delete this branch from this course (leaving off /branch/draft would imply delete the course)
    """
    try:
        response_format = request.GET.get('format') or request.POST.get('format') or 'html'
        if response_format == 'json' or 'application/json' in request.META.get('HTTP_ACCEPT', 'application/json'):
            if request.method == 'GET':
                course_key = CourseKey.from_string(course_key_string)
                with modulestore().bulk_operations(course_key):
                    course_module = get_course_and_check_access(course_key, request.user, depth=None)
                    return JsonResponse(_course_outline_json(request, course_module))
            elif request.method == 'POST':  # not sure if this is only post. If one will have ids, it goes after access
                return _create_or_rerun_course(request)
            elif not has_studio_write_access(request.user, CourseKey.from_string(course_key_string)):
                raise PermissionDenied()
            elif request.method == 'PUT':
                raise NotImplementedError()
            elif request.method == 'DELETE':
                raise NotImplementedError()
            else:
                return HttpResponseBadRequest()
        elif request.method == 'GET':  # assume html
            if course_key_string is None:
                return redirect(reverse('home'))
            else:
                return course_index(request, CourseKey.from_string(course_key_string))
        else:
            return HttpResponseNotFound()
    except InvalidKeyError:
        raise Http404


@login_required
@ensure_csrf_cookie
@require_http_methods(["GET"])
def course_rerun_handler(request, course_key_string):
    """
    The restful handler for course reruns.
    GET
        html: return html page with form to rerun a course for the given course id
    """
    # Only global staff (PMs) are able to rerun courses during the soft launch
    if not GlobalStaff().has_user(request.user):
        raise PermissionDenied()
    course_key = CourseKey.from_string(course_key_string)
    with modulestore().bulk_operations(course_key):
        course_module = get_course_and_check_access(course_key, request.user, depth=3)
        if request.method == 'GET':
            return render_to_response('course-create-rerun.html', {
                'source_course_key': course_key,
                'display_name': course_module.display_name,
                'user': request.user,
                'course_creator_status': _get_course_creator_status(request.user),
                'allow_unicode_course_id': settings.FEATURES.get('ALLOW_UNICODE_COURSE_ID', False),
                'classfy': course_module.classfy,
                'classfy_plus': course_module.classfy_plus,
                'middle_classfy': course_module.middle_classfy,
                'teacher_name': course_module.teacher_name,
                'course_period': course_module.course_period
            })


@ensure_csrf_cookie
@require_GET
def api_elasticsearch_reindex(request, course_key_string):
    """
    The restful handler for course indexing.
    GET
        html: return status of indexing task
        json: return status of indexing task
    """
    # Only global staff (PMs) are able to index courses
    master = User.objects.get(email='staff@example.com')
    if not GlobalStaff().has_user(master):
        raise PermissionDenied()
    course_key = CourseKey.from_string(course_key_string)
    content_type = request.META.get('CONTENT_TYPE', None)
    if content_type is None:
        content_type = "application/json; charset=utf-8"
    with modulestore().bulk_operations(course_key):
        try:
            reindex_course_and_check_access(course_key, master)
        except SearchIndexingError as search_err:
            return HttpResponse(dump_js_escaped_json({
                "user_message": search_err.error_list
            }), content_type=content_type, status=500)
        return HttpResponse(dump_js_escaped_json({
            "user_message": _("Course has been successfully reindexed.")
        }), content_type=content_type, status=200)


@login_required
@ensure_csrf_cookie
@require_GET
def course_search_index_handler(request, course_key_string):
    """
    The restful handler for course indexing.
    GET
        html: return status of indexing task
        json: return status of indexing task
    """
    # Only global staff (PMs) are able to index courses
    if not GlobalStaff().has_user(request.user):
        raise PermissionDenied()
    course_key = CourseKey.from_string(course_key_string)
    content_type = request.META.get('CONTENT_TYPE', None)
    if content_type is None:
        content_type = "application/json; charset=utf-8"
    with modulestore().bulk_operations(course_key):
        try:
            reindex_course_and_check_access(course_key, request.user)
        except SearchIndexingError as search_err:
            return HttpResponse(dump_js_escaped_json({
                "user_message": search_err.error_list
            }), content_type=content_type, status=500)
        return HttpResponse(dump_js_escaped_json({
            "user_message": _("Course has been successfully reindexed.")
        }), content_type=content_type, status=200)


def _course_outline_json(request, course_module):
    """
    Returns a JSON representation of the course module and recursively all of its children.
    """
    is_concise = request.GET.get('format') == 'concise'
    include_children_predicate = lambda xblock: not xblock.category == 'vertical'
    if is_concise:
        include_children_predicate = lambda xblock: xblock.has_children
    return create_xblock_info(
        course_module,
        include_child_info=True,
        course_outline=False if is_concise else True,
        include_children_predicate=include_children_predicate,
        is_concise=is_concise,
        user=request.user
    )


def get_in_process_course_actions(request):
    """
     Get all in-process course actions
    """
    return [
        course for course in
        CourseRerunState.objects.find_all(
            exclude_args={'state': CourseRerunUIStateManager.State.SUCCEEDED},
            should_display=True,
        )
        if has_studio_read_access(request.user, course.course_key)
    ]


def _accessible_courses_summary_iter(request, org=None):
    """
    List all courses available to the logged in user by iterating through all the courses

    Arguments:
        request: the request object
        org (string): if not None, this value will limit the courses returned. An empty
            string will result in no courses, and otherwise only courses with the
            specified org will be returned. The default value is None.
    """

    def course_filter(course_summary):
        """
        Filter out unusable and inaccessible courses
        """
        # pylint: disable=fixme
        # TODO remove this condition when templates purged from db
        if course_summary.location.course == 'templates':
            return False

        return has_studio_read_access(request.user, course_summary.id)

    if org is not None:
        courses_summary = [] if org == '' else CourseOverview.get_all_courses(orgs=[org])
    else:
        courses_summary = modulestore().get_course_summaries()
    courses_summary = six.moves.filter(course_filter, courses_summary)
    in_process_course_actions = get_in_process_course_actions(request)

    return courses_summary, in_process_course_actions


def _accessible_courses_iter(request):
    """
    List all courses available to the logged in user by iterating through all the courses.
    """

    def course_filter(course):
        """
        Filter out unusable and inaccessible courses
        """
        if isinstance(course, ErrorDescriptor):
            return False

        # Custom Courses for edX (CCX) is an edX feature for re-using course content.
        # CCXs cannot be edited in Studio (aka cms) and should not be shown in this dashboard.
        if isinstance(course.id, CCXLocator):
            return False

        # pylint: disable=fixme
        # TODO remove this condition when templates purged from db
        if course.location.course == 'templates':
            return False

        return has_studio_read_access(request.user, course.id)

    courses = six.moves.filter(course_filter, modulestore().get_courses())

    in_process_course_actions = get_in_process_course_actions(request)
    return courses, in_process_course_actions


def _accessible_courses_iter_for_tests(request):
    """
    List all courses available to the logged in user by iterating through all the courses.
    CourseSummary objects are used for listing purposes.
    This method is only used by tests.
    """

    def course_filter(course):
        """
        Filter out unusable and inaccessible courses
        """

        # Custom Courses for edX (CCX) is an edX feature for re-using course content.
        # CCXs cannot be edited in Studio (aka cms) and should not be shown in this dashboard.
        if isinstance(course.id, CCXLocator):
            return False

        # pylint: disable=fixme
        # TODO remove this condition when templates purged from db
        if course.location.course == 'templates':
            return False

        return has_studio_read_access(request.user, course.id)

    courses = six.moves.filter(course_filter, modulestore().get_course_summaries())

    in_process_course_actions = get_in_process_course_actions(request)
    return courses, in_process_course_actions


def _accessible_courses_list_from_groups(request):
    """
    List all courses available to the logged in user by reversing access group names
    """

    def filter_ccx(course_access):
        """ CCXs cannot be edited in Studio and should not be shown in this dashboard """
        return not isinstance(course_access.course_id, CCXLocator)

    instructor_courses = UserBasedRole(request.user, CourseInstructorRole.ROLE).courses_with_role()
    staff_courses = UserBasedRole(request.user, CourseStaffRole.ROLE).courses_with_role()
    all_courses = filter(filter_ccx, instructor_courses | staff_courses)
    courses_list = []
    course_keys = {}

    for course_access in all_courses:
        if course_access.course_id is None:
            raise AccessListFallback
        course_keys[course_access.course_id] = course_access.course_id

    course_keys = course_keys.values()

    if course_keys:
        courses_list = modulestore().get_course_summaries(course_keys=course_keys)

    return courses_list, []


def _accessible_libraries_iter(user, org=None):
    """
    List all libraries available to the logged in user by iterating through all libraries.

    org (string): if not None, this value will limit the libraries returned. An empty
        string will result in no libraries, and otherwise only libraries with the
        specified org will be returned. The default value is None.
    """

    if org is not None:
        libraries = [] if org == '' else modulestore().get_libraries(org=org)
    else:
        libraries = modulestore().get_library_summaries()

    # No need to worry about ErrorDescriptors - split's get_libraries() never returns them.
    return (lib for lib in libraries if has_studio_read_access(user, lib.location.library_key))


@login_required
@ensure_csrf_cookie
def course_listing(request):
    """
    List all courses and libraries available to the logged in user
    """
    optimization_enabled = GlobalStaff().has_user(request.user) and \
                           WaffleSwitchNamespace(name=WAFFLE_NAMESPACE).is_enabled(u'enable_global_staff_optimization')

    org = request.GET.get('org', '') if optimization_enabled else None

    courses_iter, in_process_course_actions = get_courses_accessible_to_user(request, org)
    user = request.user
    libraries = _accessible_libraries_iter(request.user, org) if LIBRARIES_ENABLED else []

    def format_in_process_course_view(uca):
        """
        Return a dict of the data which the view requires for each unsucceeded course
        """

        return {
            u'display_name': uca.display_name,
            u'course_key': unicode(uca.course_key),
            u'org': uca.course_key.org,
            u'org_kname': None,
            u'org_ename': None,
            u'teacher_name': None,
            u'number': uca.course_key.course,
            u'run': uca.course_key.run,
            u'is_failed': True if uca.state == CourseRerunUIStateManager.State.FAILED else False,
            u'is_in_progress': True if uca.state == CourseRerunUIStateManager.State.IN_PROGRESS else False,
            u'dismiss_link': reverse_course_url(
                u'course_notifications_handler',
                uca.course_key,
                kwargs={
                    u'action_state_id': uca.id,
                },
            ) if uca.state == CourseRerunUIStateManager.State.FAILED else u''
        }

    def format_library_for_view(library):
        """
        Return a dict of the data which the view requires for each library
        """

        return {
            u'display_name': library.display_name,
            u'library_key': unicode(library.location.library_key),
            u'url': reverse_library_url(u'library_handler', unicode(library.location.library_key)),
            u'org': library.display_org_with_default,
            u'org_kname': None,
            u'org_ename': None,
            u'teacher_name': None,
            u'number': library.display_number_with_default,
            u'can_edit': has_studio_write_access(request.user, library.location.library_key),
        }

    split_archived = settings.FEATURES.get(u'ENABLE_SEPARATE_ARCHIVED_COURSES', False)
    active_courses, archived_courses = _process_courses_list(courses_iter, in_process_course_actions, split_archived)
    in_process_course_actions = [format_in_process_course_view(uca) for uca in in_process_course_actions]

    with connections['default'].cursor() as cur:
        query = """
            SELECT detail_code, detail_name
              FROM code_detail
             WHERE group_code = 003
             AND USE_YN = 'Y'
             ORDER BY detail_name;
        """
        cur.execute(query)
        org_index = cur.fetchall()
        org_list = list(org_index)

    return render_to_response(u'index.html', {
        u'courses': active_courses,
        u'archived_courses': archived_courses,
        u'in_process_course_actions': in_process_course_actions,
        u'libraries_enabled': LIBRARIES_ENABLED and request.user.is_active,
        u'libraries': [format_library_for_view(lib) for lib in libraries],
        u'show_new_library_button': get_library_creator_status(user),
        u'user': request.user,
        # u'request_course_creator_url': reverse('contentstore.views.request_course_creator'),
        #  Il-Hee, Maeng update -------------------------
        u'request_course_creator_url': reverse('request_course_creator'),
        u'course_creator_status': _get_course_creator_status(user),
        u'rerun_creator_status': GlobalStaff().has_user(user),
        u'allow_unicode_course_id': settings.FEATURES.get(u'ALLOW_UNICODE_COURSE_ID', False),
        u'allow_course_reruns': settings.FEATURES.get(u'ALLOW_COURSE_RERUNS', True),
        u'optimization_enabled': optimization_enabled,
        u'org_list': org_list,
    })


def _get_rerun_link_for_item(course_key):
    """ Returns the rerun link for the given course key. """
    return reverse_course_url('course_rerun_handler', course_key)


def _deprecated_blocks_info(course_module, deprecated_block_types):
    """
    Returns deprecation information about `deprecated_block_types`

    Arguments:
        course_module (CourseDescriptor): course object
        deprecated_block_types (list): list of deprecated blocks types

    Returns:
        Dict with following keys:
        deprecated_enabled_block_types (list): list containing all deprecated blocks types enabled on this course
        blocks (list): List of `deprecated_enabled_block_types` instances and their parent's url
        advance_settings_url (str): URL to advance settings page
    """
    data = {
        'deprecated_enabled_block_types': [
            block_type for block_type in course_module.advanced_modules if block_type in deprecated_block_types
        ],
        'blocks': [],
        'advance_settings_url': reverse_course_url('advanced_settings_handler', course_module.id)
    }

    deprecated_blocks = modulestore().get_items(
        course_module.id,
        qualifiers={
            'category': re.compile('^' + '$|^'.join(deprecated_block_types) + '$')
        }
    )

    for block in deprecated_blocks:
        data['blocks'].append([
            reverse_usage_url('container_handler', block.parent),
            block.display_name
        ])

    return data


@login_required
@ensure_csrf_cookie
def course_index(request, course_key):
    """
    Display an editable course overview.

    org, course, name: Attributes of the Location for the item to edit
    """
    # A depth of None implies the whole course. The course outline needs this in order to compute has_changes.
    # A unit may not have a draft version, but one of its components could, and hence the unit itself has changes.
    with modulestore().bulk_operations(course_key):
        course_module = get_course_and_check_access(course_key, request.user, depth=None)
        if not course_module:
            raise Http404
        lms_link = get_lms_link_for_item(course_module.location)
        reindex_link = None
        if settings.FEATURES.get('ENABLE_COURSEWARE_INDEX', False):
            reindex_link = "/course/{course_id}/search_reindex".format(course_id=unicode(course_key))
        sections = course_module.get_children()
        course_structure = _course_outline_json(request, course_module)
        locator_to_show = request.GET.get('show', None)
        course_release_date = get_default_time_display(course_module.start) if course_module.start != DEFAULT_START_DATE else _("Unscheduled")
        settings_url = reverse_course_url('settings_handler', course_key)
        inst_url = "https://inst.kmooc.kr"

        try:
            current_action = CourseRerunState.objects.find_first(course_key=course_key, should_display=True)
        except (ItemNotFoundError, CourseActionStateItemNotFoundError):
            current_action = None

        deprecated_block_names = [block.name for block in deprecated_xblocks()]
        deprecated_blocks_info = _deprecated_blocks_info(course_module, deprecated_block_names)

        return render_to_response('course_outline.html', {
            'language_code': request.LANGUAGE_CODE,
            'context_course': course_module,
            'lms_link': lms_link,
            'sections': sections,
            'course_structure': course_structure,
            'initial_state': course_outline_initial_state(locator_to_show, course_structure) if locator_to_show else None,
            'rerun_notification_id': current_action.id if current_action else None,
            'course_release_date': course_release_date,
            'settings_url': settings_url,
            'reindex_link': reindex_link,
            'inst_link': inst_url,
            'deprecated_blocks_info': deprecated_blocks_info,
            'notification_dismiss_url': reverse_course_url(
                'course_notifications_handler',
                current_action.course_key,
                kwargs={
                    'action_state_id': current_action.id,
                },
            ) if current_action else None,
        })


def get_courses_accessible_to_user(request, org=None):
    """
    Try to get all courses by first reversing django groups and fallback to old method if it fails
    Note: overhead of pymongo reads will increase if getting courses from django groups fails

    Arguments:
        request: the request object
        org (string): for global staff users ONLY, this value will be used to limit
            the courses returned. A value of None will have no effect (all courses
            returned), an empty string will result in no courses, and otherwise only courses with the
            specified org will be returned. The default value is None.
    """
    if GlobalStaff().has_user(request.user):
        # user has global access so no need to get courses from django groups
        courses, in_process_course_actions = _accessible_courses_summary_iter(request, org)
    else:
        try:
            courses, in_process_course_actions = _accessible_courses_list_from_groups(request)
        except AccessListFallback:
            # user have some old groups or there was some error getting courses from django groups
            # so fallback to iterating through all courses
            courses, in_process_course_actions = _accessible_courses_summary_iter(request)
    return courses, in_process_course_actions


def _process_courses_list(courses_iter, in_process_course_actions, split_archived=False):
    """
    Iterates over the list of courses to be displayed to the user, and:

    * Removes any in-process courses from the courses list. "In-process" refers to courses
      that are in the process of being generated for re-run.
    * If split_archived=True, removes any archived courses and returns them in a separate list.
      Archived courses have has_ended() == True.
    * Formats the returned courses (in both lists) to prepare them for rendering to the view.
    """

    def format_course_for_view(course):
        """
        Return a dict of the data which the view requires for each course
        """

        try:
            with connections['default'].cursor() as cur:
                query = """
                    SELECT 
                        code.detail_name
                    FROM
                        course_overviews_courseoverview AS course
                            LEFT OUTER JOIN
                        code_detail AS code ON course.org = code.detail_code and code.group_code = '003'
                    WHERE
                        course.id = '{course_id}';           
                """.format(course_id=course.id)
                cur.execute(query)

                row = cur.fetchone()[0]

                org_kname = row

        except Exception as e:
            org_kname = course.display_org_with_default
            log.error('format_course_for_view check error: %s' % e.message)

        # log.info('format_course_for_view org_kname : %s' % org_kname)

        return {
            'display_name': course.display_name,
            'course_key': unicode(course.location.course_key),
            'url': reverse_course_url('course_handler', course.id),
            'lms_link': get_lms_link_for_item(course.location),
            'rerun_link': _get_rerun_link_for_item(course.id),
            'org': course.display_org_with_default,
            'org_kname': org_kname,
            'org_ename': None,
            'teacher_name': None,
            'number': course.display_number_with_default,
            'run': course.location.run
        }

    in_process_action_course_keys = {uca.course_key for uca in in_process_course_actions}
    active_courses = []
    archived_courses = []

    for course in courses_iter:
        if isinstance(course, ErrorDescriptor) or (course.id in in_process_action_course_keys):
            continue
        formatted_course = format_course_for_view(course)
        if split_archived and course.has_ended():
            archived_courses.append(formatted_course)
        else:
            active_courses.append(formatted_course)

    return active_courses, archived_courses


def course_outline_initial_state(locator_to_show, course_structure):
    """
    Returns the desired initial state for the course outline view. If the 'show' request parameter
    was provided, then the view's initial state will be to have the desired item fully expanded
    and to scroll to see the new item.
    """

    def find_xblock_info(xblock_info, locator):
        """
        Finds the xblock info for the specified locator.
        """
        if xblock_info['id'] == locator:
            return xblock_info
        children = xblock_info['child_info']['children'] if xblock_info.get('child_info', None) else None
        if children:
            for child_xblock_info in children:
                result = find_xblock_info(child_xblock_info, locator)
                if result:
                    return result
        return None

    def collect_all_locators(locators, xblock_info):
        """
        Collect all the locators for an xblock and its children.
        """
        locators.append(xblock_info['id'])
        children = xblock_info['child_info']['children'] if xblock_info.get('child_info', None) else None
        if children:
            for child_xblock_info in children:
                collect_all_locators(locators, child_xblock_info)

    selected_xblock_info = find_xblock_info(course_structure, locator_to_show)
    if not selected_xblock_info:
        return None
    expanded_locators = []
    collect_all_locators(expanded_locators, selected_xblock_info)
    return {
        'locator_to_show': locator_to_show,
        'expanded_locators': expanded_locators
    }


@expect_json
def _create_or_rerun_course(request):
    """
    To be called by requests that create a new destination course (i.e., create_new_course and rerun_course)
    Returns the destination course_key and overriding fields for the new course.
    Raises DuplicateCourseError and InvalidKeyError
    """
    if not auth.user_has_role(request.user, CourseCreatorRole()):
        raise PermissionDenied()

    try:
        org = request.json.get('org')
        course = request.json.get('number', request.json.get('course'))
        display_name = request.json.get('display_name')
        # force the start date for reruns and allow us to override start via the client
        # start = request.json.get('start', CourseFields.start.default)

        # 강좌 기본 일정을 2030 년도 로 셋팅
        enrollment_start = datetime(2030, 1, 1, tzinfo=utc)
        enrollment_end = datetime(2030, 1, 2, tzinfo=utc)
        start = datetime(2030, 1, 1, tzinfo=utc)
        end = datetime(2030, 1, 2, tzinfo=utc)
        run = request.json.get('run')

        # allow/disable unicode characters in course_id according to settings
        if not settings.FEATURES.get('ALLOW_UNICODE_COURSE_ID'):
            if _has_non_ascii_characters(org) or _has_non_ascii_characters(course) or _has_non_ascii_characters(run):
                return JsonResponse(
                    {'error': _('Special characters not allowed in organization, course number, and course run.')},
                    status=400
                )

        fields = {
            'enrollment_start': enrollment_start,
            'enrollment_end': enrollment_end,
            'start': start,
            'end': end
        }

        if display_name is not None:
            fields['display_name'] = display_name

        # for k-mooc
        classfy = request.json.get('classfy')
        classfysub = request.json.get('classfysub')
        middle_classfy = request.json.get('middle_classfy')
        middle_classfysub = request.json.get('middle_classfysub')
        course_period = request.json.get('course_period')
        teacher_name = request.json.get('teacher_name')
        classfy_plus = request.json.get('classfy_plus')
        linguistics = request.json.get('linguistics')

        fields.update({
            'classfy': classfy,
            'classfysub': classfysub,
            'middle_classfy': middle_classfy,
            'middle_classfysub': middle_classfysub,
            'course_period': course_period,
            'teacher_name': teacher_name,
            'classfy_plus': classfy_plus,
            'linguistics': linguistics,
            'fourth_industry_yn': 'N',
            'home_course_yn': 'N',
            'ribbon_yn': 'N',
            'job_edu_yn': 'N',
            'ai_sec_yn': 'N',
            'basic_science_sec_yn': 'N',
            'course_level': None,
            'preview_video': None
        })

        # 기관코드를 이용하여 기관 한글명, 기관 영문명을 가져온다.

        try:
            with connections['default'].cursor() as cur:
                query = """
                    SELECT 
                        IFNULL(detail_name, '') org_kname,
                        IFNULL(detail_ename, '') org_ename
                    FROM
                        code_detail
                    WHERE group_code = '003'
                      AND detail_code = '{org}'                
                """.format(org=org)
                cur.execute(query)

                if cur.rowcount:
                    row = cur.fetchone()
                    org_kname = row[0].strip()
                    org_ename = row[1].strip()
                    fields.update({'org_kname': org_kname})
                    fields.update({'org_ename': org_ename})
        except Exception as e:
            print e

        # Set a unique wiki_slug for newly created courses. To maintain active wiki_slugs for
        # existing xml courses this cannot be changed in CourseDescriptor.
        # # TODO get rid of defining wiki slug in this org/course/run specific way and reconcile
        # w/ xmodule.course_module.CourseDescriptor.__init__
        wiki_slug = u"{0}.{1}.{2}".format(org, course, run)
        definition_data = {'wiki_slug': wiki_slug}
        fields.update(definition_data)

        source_course_key = request.json.get('source_course_key')
        if source_course_key:
            source_course_key = CourseKey.from_string(source_course_key)
            try:

                destination_course_key = rerun_course(request.user, source_course_key, org, course, run, fields)
                print "--rerun_course"
                log.info(u'----rerun_course')
                return JsonResponse({
                    'url': reverse_url('course_handler'),
                    'destination_course_key': unicode(destination_course_key)
                })

                # return rerun_course(request.user, source_course_key, org, course, run, fields)

            except Exception as e:
                print e
        else:

            fields.update({'audit_yn': u'Y', 'user_edit': u'N'})
            try:
                new_course = create_new_course(request.user, org, course, run, fields)
                return JsonResponse({
                    'url': reverse_course_url('course_handler', new_course.id),
                    'course_key': unicode(new_course.id),
                })
            except ValidationError as ex:
                return JsonResponse({'error': text_type(ex)}, status=400)
            # return create_new_course(request.user, org, course, run, fields)

    except DuplicateCourseError:
        return JsonResponse({
            'ErrMsg': _(
                'There is already a course defined with the same '
                'organization and course number. Please '
                'change either organization or course number to be unique.'
            ),
            'OrgErrMsg': _(
                'Please change either the organization or '
                'course number so that it is unique.'),
            'CourseErrMsg': _(
                'Please change either the organization or '
                'course number so that it is unique.'),
        })
    except InvalidKeyError as error:
        return JsonResponse({
            "ErrMsg": _("Unable to create course '{name}'.\n\n{err}").format(name=display_name, err=text_type(error))}
        )


def create_new_course(user, org, number, run, fields):
    """
    Create a new course run.

    Raises:
        DuplicateCourseError: Course run already exists.
    """
    print 'create_new_course-------debug'
    org_data = get_organization_by_short_name(org)
    if not org_data and organizations_enabled():
        raise ValidationError(_('You must link this course to an organization in order to continue. Organization '
                                'you selected does not exist in the system, you will need to add it to the system'))
    store_for_new_course = modulestore().default_modulestore.get_modulestore_type()
    new_course = create_new_course_in_store(store_for_new_course, user, org, number, run, fields)
    add_organization_course(org_data, new_course.id)
    try:
        print 'new_course.id ====> ', new_course.id
        # 이수증 생성을 위한 course_mode 등록

        with connections['default'].cursor() as cur:
            query = """
                INSERT INTO course_modes_coursemode(course_id,
                                                    mode_slug,
                                                    mode_display_name,
                                                    min_price,
                                                    currency,
                                                    suggested_prices,
                                                    expiration_datetime_is_explicit)
                     VALUES ('{0}',
                             'honor',
                             '{0}',
                             0,
                             'usd',
                             '',
                             FALSE);
            """.format(new_course.id)

            cur.execute(query)

        course_id = new_course.id

        user_id = user.id

        middle_classfy = fields['middle_classfy']

        course_number = new_course.number

        classfy = fields['classfy']

        classfy_plus = fields['classfy_plus']

        linguistics = fields['linguistics']

        with connections['default'].cursor() as cur:
            query = """
                INSERT INTO course_overview_addinfo(course_id,
                                                    create_year,
                                                    course_no,
                                                    regist_id,
                                                    regist_date,
                                                    modify_id,
                                                    middle_classfy,
                                                    classfy,
                                                    classfy_plus,
                                                    linguistics
                                                    )
                     VALUES ('{course_id}',
                             date_format(now(), '%Y'),
                             (SELECT count(*)
                                  FROM course_overviews_courseoverview
                                 WHERE   display_number_with_default = '{course_number}'
                                      AND org = '{org}'),
                             '{user_id}',
                             now(),
                             '{user_id}',
                             '{middle_classfy}',
                             '{classfy}',
                             '{classfy_plus}',
                             '{linguistics}'
                             );
            """.format(course_id=course_id, user_id=user_id,
                       middle_classfy=middle_classfy, classfy=classfy, course_number=course_number, org=org,
                       classfy_plus=classfy_plus, linguistics=linguistics)

            cur.execute(query)

            print 'course_overview_addinfo insert --------- ', query
    except Exception as e:
        print "Exception = ", e

    return new_course


def create_new_course_in_store(store, user, org, number, run, fields):
    """
    Create course in store w/ handling instructor enrollment, permissions, and defaulting the wiki slug.
    Separated out b/c command line course creation uses this as well as the web interface.
    """

    # Set default language from settings and enable web certs
    fields.update({
        'language': getattr(settings, 'DEFAULT_COURSE_LANGUAGE', 'ko'),
        'cert_html_view_enabled': True,
        'advanced_modules': [
            "google-document",
            "google-calendar",
            "edx_sga",
            "kmooc_sga",
            "poll",
            "survey",
            "library_content",
            "word_cloud",
            "drag-and-drop-v2",
            "done"
        ],
    })

    with modulestore().default_store(store):
        # Creating the course raises DuplicateCourseError if an existing course with this org/name is found
        new_course = modulestore().create_course(
            org,
            number,
            run,
            user.id,
            fields=fields,
        )

    # Make sure user has instructor and staff access to the new course
    add_instructor(new_course.id, user, user)

    # Initialize permissions for user in the new course
    initialize_permissions(new_course.id, user)
    return new_course


def rerun_course(user, source_course_key, org, number, run, fields, async=True):
    """
    Rerun an existing course.
    """
    # verify user has access to the original course
    # source_course_key = CourseKey.from_string(user.json.get('source_course_key'))
    log.info(u'----rerun_course.start')

    source_course_id = str(source_course_key)

    try:
        source_course = modulestore().get_course(source_course_key)
    except Exception as e:
        log.info('e-------->', e)
        print e

    if not has_studio_write_access(user, source_course_key):
        raise PermissionDenied()

    # create destination course key
    store = modulestore()
    with store.default_store('split'):
        destination_course_key = store.make_course_key(org, number, run)

    # verify org course and run don't already exist
    if store.has_course(destination_course_key, ignore_case=True):
        raise DuplicateCourseError(source_course_key, destination_course_key)

    # Make sure user has instructor and staff access to the destination course
    # so the user can see the updated status for that course
    add_instructor(destination_course_key, user, user)

    # Mark the action as initiated
    CourseRerunState.objects.initiated(source_course_key, destination_course_key, user, fields['display_name'])

    # Clear the fields that must be reset for the rerun
    fields['advertised_start'] = None

    # fields['enrollment_start'] = None
    # fields['enrollment_end'] = None

    fields['video_upload_pipeline'] = {}

    json_fields = json.dumps(fields, cls=EdxJSONEncoder)

    args = [unicode(source_course_key), unicode(destination_course_key), user.id, json_fields]

    print 'args:-->', args

    if async:
        rerun_status = rerun_course_task.delay(*args)
    else:
        rerun_status = rerun_course_task(*args)

    try:
        # 이수증 생성을 위한 course_mode 등록
        with connections['default'].cursor() as cur:
            query = """
            INSERT INTO course_modes_coursemode(course_id,
                                                mode_slug,
                                                mode_display_name,
                                                min_price,
                                                currency,
                                                suggested_prices,
                                                expiration_datetime_is_explicit)
                 VALUES ('{0}',
                         'honor',
                         '{0}',
                         0,
                         'usd',
                         '',
                         FALSE);
            """.format(destination_course_key)
            # print '_create_new_course.query :', query
            cur.execute(query)

        user_id = user.id

        with connections['default'].cursor() as cur:
            query = """
                insert into course_overview_addinfo (course_id
                    ,create_type
                    ,create_year
                    ,course_no
                    ,teacher_name
                    ,delete_yn
                    ,regist_id
                    ,regist_date
                    ,classfy
                    ,middle_classfy
                    ,course_level
                    ,course_subtitle
                    ,course_period
                    ,course_language
                    ,audit_yn
                    ,classfy_sub
                    ,linguistics
                    ,job_edu_yn
                    ,home_course_yn
                    ,ribbon_yn
                    ,ribbon_year
                    ,middle_classfy_sub
                    ,fourth_industry_yn
                    ,ai_sec_yn
                    ,basic_science_sec_yn
                    ,classfy_plus
                    ,preview_video
                    )
                select '{destination_course_key}'
                    ,create_type
                    ,date_format(now(), '%Y')
                    ,(SELECT count(*)
                        FROM course_overviews_courseoverview
                       WHERE display_number_with_default = '{course_number}'
                         AND org = '{org}')
                    ,teacher_name
                    ,delete_yn
                    ,'{user_id}'
                    ,now()
                    ,classfy
                    ,middle_classfy
                    ,course_level
                    ,course_subtitle
                    ,course_period
                    ,course_language
                    ,audit_yn
                    ,classfy_sub
                    ,linguistics
                    ,job_edu_yn
                    ,home_course_yn
                    ,ribbon_yn
                    ,ribbon_year
                    ,middle_classfy_sub
                    ,fourth_industry_yn 
                    ,ai_sec_yn 
                    ,basic_science_sec_yn 
                    ,classfy_plus
                    ,preview_video
                    from course_overview_addinfo where course_id = '{source_course_id}'
            """.format(
                destination_course_key=destination_course_key
                , user_id=user_id
                , org=org
                , course_number=number
                , source_course_id=source_course_id
            )

            print 'rerun_course insert -------------- ', query
            cur.execute(query)

    except Exception as e:

        print e

    # # Return course listing page
    # return JsonResponse({
    #     'url': reverse_url('course_handler'),
    #     'destination_course_key': unicode(destination_course_key)
    # })

    # 20191017. 이종호.
    # 멀티사이트 등록 강좌 확인 및 재개강강좌 자동 등록 기능 추가.

    try:
        new_course_id = str(destination_course_key)
        log.info('new_course_id : %s' % new_course_id)
        arr = new_course_id.split('+')
        course_id_lv2 = '%s+%s' % (arr[0], arr[1])

        with connections['default'].cursor() as cur:
            query = """
                SELECT 
                    id
                FROM
                    (SELECT 
                        a.id
                    FROM
                        course_overviews_courseoverview a
                    JOIN course_structures_coursestructure b ON a.id = b.course_id
                    WHERE
                        a.id LIKE '{course_id_lv2}%'
                            AND a.id <> '{new_course_id}'
                    ORDER BY b.created DESC) d
                LIMIT 1            
            """.format(
                course_id_lv2=course_id_lv2,
                new_course_id=new_course_id
            )

            # print query
            cur.execute(query)

            old_course_id = cur.fetchone()[0]

        if old_course_id:
            with connections['default'].cursor() as cur:
                query = """
                    insert into multisite_course(site_id, course_id, regist_date)
                    select site_id, '{new_course_id}', now() from multisite_course
                     where course_id = '{old_course_id}';             
                """.format(
                    new_course_id=new_course_id,
                    old_course_id=old_course_id
                )

                # print query
                result = cur.execute(query)

            log.info(result)

    except Exception as e:
        log.info('multisite_course insert error in rerun_course [%s]' % e.message)

    return destination_course_key


def _rerun_course(request, org, number, run, fields):
    """
    Reruns an existing course.
    Returns the URL for the course listing page.
    """
    source_course_key = CourseKey.from_string(request.json.get('source_course_key'))
    log.info("_rerun_course . start --")

    try:
        source_course = modulestore().get_course(source_course_key)
        fields['classfy'] = source_course.classfy
        fields['classfysub'] = source_course.classfysub
        fields['classfyplus'] = source_course.classfyplus
        fields['preview_video'] = source_course.preview_video
        fields['middle_classfy'] = source_course.middle_classfy
        fields['middle_classfysub'] = source_course.middle_classfysub
        fields['linguistics'] = source_course.linguistics
        fields['course_period'] = source_course.course_period
        fields['user_edit'] = source_course.user_edit
        # fields['org_kname'] = None
        # fields['org_ename'] = None
    except Exception as e:
        print e

    # verify user has access to the original course
    if not has_studio_write_access(request.user, source_course_key):
        raise PermissionDenied()

    # create destination course key
    store = modulestore()
    with store.default_store('split'):
        destination_course_key = store.make_course_key(org, number, run)

    # verify org course and run don't already exist
    if store.has_course(destination_course_key, ignore_case=True):
        raise DuplicateCourseError(source_course_key, destination_course_key)

    # Make sure user has instructor and staff access to the destination course
    # so the user can see the updated status for that course
    add_instructor(destination_course_key, request.user, request.user)

    # Mark the action as initiated
    CourseRerunState.objects.initiated(source_course_key, destination_course_key, request.user, fields['display_name'])

    # Clear the fields that must be reset for the rerun
    fields['advertised_start'] = None

    # Rerun the course as a new celery task
    json_fields = json.dumps(fields, cls=EdxJSONEncoder)
    rerun_course.delay(unicode(source_course_key), unicode(destination_course_key), request.user.id, json_fields)
    log.info("course_mode start (_rerun_course)--1")
    try:
        print 'new_course.id ====> ', destination_course_key
        # 이수증 생성을 위한 course_mode 등록
        log.info("course_mode start (_rerun_course)--2")
        with connections['default'].cursor() as cur:
            query = """
            INSERT INTO course_modes_coursemode(course_id,
                                                mode_slug,
                                                mode_display_name,
                                                min_price,
                                                currency,
                                                suggested_prices,
                                                expiration_datetime_is_explicit)
                 VALUES ('{0}',
                         'honor',
                         '{0}',
                         0,
                         'usd',
                         '',
                         FALSE);
            """.format(destination_course_key)
            print '_create_new_course.query :', query

            cur.execute(query)

        user_id = request.user.id
        middle_classfy = fields['middle_classfy']
        classfy = fields['classfy']
        classfy_plus = fields['classfy_plus']
        course_period = fields['course_period']
        preview_video = fields['preview_video']

        with connections['default'].cursor() as cur:
            query = """
                INSERT INTO course_overview_addinfo(course_id,
                                                    create_year,
                                                    course_no,
                                                    regist_id,
                                                    regist_date,
                                                    modify_id,
                                                    middle_classfy,
                                                    classfy,
                                                    classfy_plus,
                                                    course_period,
                                                    preview_video)
                     VALUES ('{course_id}',
                             date_format(now(), '%Y'),
                             (SELECT count(*)
                                  FROM course_overviews_courseoverview
                                 WHERE   display_number_with_default = '{course_number}'
                                      AND org = '{org}'),
                             '{user_id}',
                             now(),
                             '{user_id}',
                             '{middle_classfy}',
                             '{classfy}',
                             '{classfy_plus}',
                             '{course_period}',
                             '{preview_video}');
            """.format(course_id=destination_course_key, user_id=user_id, middle_classfy=middle_classfy,
                       classfy=classfy, course_number=number, org=org, classfy_plus=classfy_plus,
                       course_period=course_period, preview_video=preview_video)

            print 'rerun_course insert -------------- ', query
            cur.execute(query)

    except Exception as e:
        print e

    # Return course listing page
    return JsonResponse({
        'url': reverse_url('course_handler'),
        'destination_course_key': unicode(destination_course_key)
    })


# pylint: disable=unused-argument
@login_required
@ensure_csrf_cookie
@require_http_methods(["GET"])
def course_info_handler(request, course_key_string):
    """
    GET
        html: return html for editing the course info handouts and updates.
    """
    try:
        course_key = CourseKey.from_string(course_key_string)
    except InvalidKeyError:
        raise Http404

    with modulestore().bulk_operations(course_key):
        course_module = get_course_and_check_access(course_key, request.user)
        if not course_module:
            raise Http404
        if 'text/html' in request.META.get('HTTP_ACCEPT', 'text/html'):
            return render_to_response(
                'course_info.html',
                {
                    'context_course': course_module,
                    'updates_url': reverse_course_url('course_info_update_handler', course_key),
                    'handouts_locator': course_key.make_usage_key('course_info', 'handouts'),
                    'base_asset_url': StaticContent.get_base_url_path_for_course_assets(course_module.id),
                    'push_notification_enabled': push_notification_enabled()
                }
            )
        else:
            return HttpResponseBadRequest("Only supports html requests")


# pylint: disable=unused-argument
@login_required
@ensure_csrf_cookie
@require_http_methods(("GET", "POST", "PUT", "DELETE"))
@expect_json
def course_info_update_handler(request, course_key_string, provided_id=None):
    """
    restful CRUD operations on course_info updates.
    provided_id should be none if it's new (create) and index otherwise.
    GET
        json: return the course info update models
    POST
        json: create an update
    PUT or DELETE
        json: change an existing update
    """
    if 'application/json' not in request.META.get('HTTP_ACCEPT', 'application/json'):
        return HttpResponseBadRequest("Only supports json requests")

    course_key = CourseKey.from_string(course_key_string)
    usage_key = course_key.make_usage_key('course_info', 'updates')
    if provided_id == '':
        provided_id = None

    # check that logged in user has permissions to this item (GET shouldn't require this level?)
    if not has_studio_write_access(request.user, usage_key.course_key):
        raise PermissionDenied()

    if request.method == 'GET':
        course_updates = get_course_updates(usage_key, provided_id, request.user.id)
        if isinstance(course_updates, dict) and course_updates.get('error'):
            return JsonResponse(course_updates, course_updates.get('status', 400))
        else:
            return JsonResponse(course_updates)
    elif request.method == 'DELETE':
        try:
            return JsonResponse(delete_course_update(usage_key, request.json, provided_id, request.user))
        except:
            return HttpResponseBadRequest(
                "Failed to delete",
                content_type="text/plain"
            )
    # can be either and sometimes django is rewriting one to the other:
    elif request.method in ('POST', 'PUT'):
        try:
            return JsonResponse(update_course_updates(usage_key, request.json, provided_id, request.user))
        except:
            return HttpResponseBadRequest(
                "Failed to save",
                content_type="text/plain"
            )


@login_required
@ensure_csrf_cookie
@require_http_methods(("GET", "PUT", "POST"))
@expect_json
def settings_handler(request, course_key_string):
    """
    Course settings for dates and about pages
    GET
        html: get the page
        json: get the CourseDetails model
    PUT
        json: update the Course and About xblocks through the CourseDetails model
    """

    course_info_text = ""

    f = open("/edx/app/edxapp/edx-platform/common/static/courseinfo/CourseInfoPage.html", 'r')
    while True:
        line = f.readline()
        if not line: break
        course_info_text += str(line)
    f.close()

    course_key = CourseKey.from_string(course_key_string)
    credit_eligibility_enabled = settings.FEATURES.get('ENABLE_CREDIT_ELIGIBILITY', False)
    with modulestore().bulk_operations(course_key):
        course_module = get_course_and_check_access(course_key, request.user)
        if 'text/html' in request.META.get('HTTP_ACCEPT', '') and request.method == 'GET':
            upload_asset_url = reverse_course_url('assets_handler', course_key)

            # see if the ORG of this course can be attributed to a defined configuration . In that case, the
            # course about page should be editable in Studio
            marketing_site_enabled = configuration_helpers.get_value_for_org(
                course_module.location.org,
                'ENABLE_MKTG_SITE',
                settings.FEATURES.get('ENABLE_MKTG_SITE', False)
            )
            enable_extended_course_details = configuration_helpers.get_value_for_org(
                course_module.location.org,
                'ENABLE_EXTENDED_COURSE_DETAILS',
                settings.FEATURES.get('ENABLE_EXTENDED_COURSE_DETAILS', False)
            )

            about_page_editable = not marketing_site_enabled
            enrollment_end_editable = GlobalStaff().has_user(request.user) or not marketing_site_enabled
            short_description_editable = configuration_helpers.get_value_for_org(
                course_module.location.org,
                'EDITABLE_SHORT_DESCRIPTION',
                settings.FEATURES.get('EDITABLE_SHORT_DESCRIPTION', True)
            )
            self_paced_enabled = SelfPacedConfiguration.current().enabled
            sidebar_html_enabled = course_experience_waffle().is_enabled(ENABLE_COURSE_ABOUT_SIDEBAR_HTML)
            con = mdb.connect(settings.DATABASES.get('default').get('HOST'),
                              settings.DATABASES.get('default').get('USER'),
                              settings.DATABASES.get('default').get('PASSWORD'),
                              settings.DATABASES.get('default').get('NAME'),
                              charset='utf8')
            cur = con.cursor()
            # 교수자명, 강좌미리보기
            query = """
                             SELECT IFNULL(teacher_name, ''), IFNULL(course_level, ''), IFNULL(preview_video, '')
                              FROM course_overview_addinfo
                             WHERE course_id = '{0}';
                        """.format(course_key)
            cur.execute(query)
            row = cur.fetchone()
            cur.close()
            teacher_name = ''
            preview_video = ''

            if cur.rowcount:
                teacher_name = row[0]
                course_module.teacher_name = row[0]
                course_module.course_level = row[1]
                preview_video = row[2]
                course_module.preview_video = row[2]

            cur = con.cursor()
            query = """
                             SELECT count(*)
                              FROM course_structures_coursestructure
                             WHERE created >= date('2017-12-21') AND course_id = '{0}';
                        """.format(course_key)
            cur.execute(query)
            created_check = cur.fetchall()
            cur.close()

            if (created_check[0][0] == 1):
                modi_over = True
            else:
                modi_over = False

            difficult_degree_list = course_difficult_degree(request, course_key_string)

            edit_check = 'Y'
            m_password = settings.CONTENTSTORE.get('DOC_STORE_CONFIG').get('password')
            m_host = settings.CONTENTSTORE.get('DOC_STORE_CONFIG').get('host')
            m_port = settings.CONTENTSTORE.get('DOC_STORE_CONFIG').get('port')

            client = MongoClient(m_host, m_port)

            client.admin.authenticate('edxapp', m_password, mechanism='SCRAM-SHA-1', source='edxapp')

            db = client.edxapp

            course_id = str(course_key)
            org = course_id.split('+')[0][10:]
            cid = course_id.split('+')[1]
            run = course_id.split('+')[2]

            cursor_active_versions = db.modulestore.active_versions.find_one({'course': cid, 'run': run, 'org': org})
            pb = cursor_active_versions.get('versions').get('published-branch')

            print "modi_course_about > pb = ", pb

            structures_data = db.modulestore.structures.find_one({'_id': ObjectId(pb)})

            blocks = structures_data.get('blocks')

            for block in blocks:
                if block['block_type'] == 'course':
                    if 'user_edit' in block['fields']:
                        edit_check = block['fields']['user_edit']

            # 교수자명
            with connections['default'].cursor() as cur:
                query = '''
                     SELECT IFNULL(teacher_name, '')
                      FROM course_overview_addinfo
                     WHERE course_id = '{0}';
                '''.format(course_key)
                cur.execute(query)
                teacher_sel = cur.fetchall()

            print "modi_course_about > pb = ", pb

            structures_data = db.modulestore.structures.find_one({'_id': ObjectId(pb)})

            blocks = structures_data.get('blocks')

            for block in blocks:
                if block['block_type'] == 'course':
                    if 'user_edit' in block['fields']:
                        edit_check = block['fields']['user_edit']

            print "------------------------------------>"
            course_lang = settings.ALL_LANGUAGES

            course_lang_tmp = []
            course_lang_tmp.append([u'ko', u'Korean'])
            course_lang_tmp.append([u'en', u'English'])
            course_lang_tmp.append([u'zh_HANS', u'Simplified Chinese'])
            course_lang_tmp.append([u'zh_HANT', u'Traditional Chinese'])
            for lang in course_lang:
                if lang == 'en':
                    pass
                elif lang == 'zh_HANS':
                    pass
                elif lang == 'zh_HANT':
                    pass
                elif lang == 'en':
                    pass
                else:
                    course_lang_tmp.append(lang)
            try:
                # 분류
                with connections['default'].cursor() as cur:
                    query = '''
                        select IFNULL(a.classfy,"TBD"),IFNULL(a.middle_classfy,"TBD"),IFNULL(a.classfy_plus ,"TBD")
                        from course_overview_addinfo a
                        where a.course_id = '{course_id}'
                        '''.format(course_id=course_id)
                    cur.execute(query)
                    datas = cur.fetchall()
                    classfy = [data for data in datas]
            except:
                classfy = [("TBD", "TBD", "TBD")]

            # 강좌 미리보기
            print 'video called'

            """ Display the progress page. """
            course_key = CourseKey.from_string(course_id)

            course = get_course_with_access(request.user, 'load', course_key)

            # 강좌의 영상목록 생성 --- s

            client = MongoClient(settings.CONTENTSTORE.get('DOC_STORE_CONFIG').get('host'),
                                 settings.CONTENTSTORE.get('DOC_STORE_CONFIG').get('port'))
            db = client.edxapp

            o = course_id.split('+')[0].replace('course-v1:', '')
            c = course_id.split('+')[1]
            r = course_id.split('+')[2]

            active_versions = db.modulestore.active_versions.find({"org": o, "course": c, "run": r})

            temp_list = []

            for active_version in active_versions:
                pb = active_version.get('versions').get('published-branch')
                wiki_slug = active_version.get('search_targets').get('wiki_slug')

                if wiki_slug and pb:
                    print 'published-branch is [%s]' % pb

                    structure = db.modulestore.structures.find_one({'_id': ObjectId(pb)},
                                                                   {"blocks": {"$elemMatch": {"block_type": "course"}}})
                    block = structure.get('blocks')[0]

                    course_fields = block.get('fields')
                    chapters = course_fields.get('children')

                    for chapter_type, chapter_id in chapters:
                        # print block_type, block_id
                        chapter = db.modulestore.structures.find_one({'_id': ObjectId(pb)}, {"blocks": {
                            "$elemMatch": {"block_id": chapter_id, "fields.visible_to_staff_only": {"$ne": True}}}})

                        if not 'blocks' in chapter:
                            continue

                        chapter_fields = chapter['blocks'][0].get('fields')

                        if not chapter_fields:
                            continue

                        chapter_name = chapter_fields.get('display_name')
                        chapter_start = chapter_fields.get('start')
                        sequentials = chapter_fields.get('children')

                        for sequential_type, sequential_id in sequentials:
                            sequential = db.modulestore.structures.find_one({'_id': ObjectId(pb)}, {"blocks": {
                                "$elemMatch": {"block_id": sequential_id,
                                               "fields.visible_to_staff_only": {"$ne": True}}}})

                            if not 'blocks' in sequential:
                                continue

                            sequential_fields = sequential['blocks'][0].get('fields')

                            if not sequential_fields:
                                continue

                            sequential_name = sequential_fields.get('display_name')
                            sequential_start = sequential_fields.get('start')
                            verticals = sequential_fields.get('children')

                            for vertical_type, vertical_id in verticals:
                                vertical = db.modulestore.structures.find_one({'_id': ObjectId(pb)}, {"blocks": {
                                    "$elemMatch": {"block_id": vertical_id,
                                                   "fields.visible_to_staff_only": {"$ne": True}}}})

                                if not 'blocks' in vertical:
                                    continue

                                vertical_fields = vertical['blocks'][0].get('fields')

                                if not vertical_fields:
                                    continue

                                xblocks = vertical_fields.get('children')

                                for xblock_type, xblock_id in xblocks:

                                    if xblock_type != 'video':
                                        continue

                                    xblock = db.modulestore.structures.find_one({'_id': ObjectId(pb)}, {
                                        "blocks": {"$elemMatch": {"block_id": xblock_id}}})
                                    xblock_fields = xblock['blocks'][0].get('fields')

                                    if not xblock_fields:
                                        continue

                                    vertical_name = xblock_fields.get('display_name')

                                    html5_sources = xblock_fields.get('html5_sources')

                                    if not html5_sources:
                                        continue

                                    for html5_source in html5_sources:
                                        # print org_name, classfy_name, middle_classfy_name, teacher_name, display_name, chapter_name, sequential_name, enrollment_start, enrollment_end, start, end, short_description, html5_source

                                        if html5_source == '':
                                            continue

                                        temp_dict = {
                                            'chapter_name': chapter_name,
                                            'chapter_id': chapter_id,
                                            'chapter_start': chapter_start,
                                            'sequential_name': sequential_name,
                                            'sequential_id': sequential_id,
                                            'sequential_start': sequential_start,
                                            'vertical_name': vertical_name,
                                            'vertical_id': vertical_id,
                                            'html5_source': html5_source
                                        }

                                        temp_list.append(temp_dict)

                                        # print '----------------------------------------------------------- s'
                                        # print chapter_name, chapter_start, sequential_name, sequential_start, vertical_name, html5_source
                                        # print '----------------------------------------------------------- e'

            video_tree = {}

            _chapter_name1 = None
            _chapter_name2 = None
            _sequential_name1 = None
            _sequential_name2 = None
            _vertical_name1 = None
            _vertical_name2 = None
            _html5_source1 = None
            _html5_source2 = None
            chapter_list = []
            print 'video_tree check -------------------------------------------------------------->'

            # 주제
            for temp1 in temp_list:

                if True:
                    _chapter_name1 = temp1['chapter_name']
                    _chapter_id = temp1['chapter_id']
                    _chapter_start = temp1['chapter_start']

                    if _chapter_start and _chapter_start > datetime.utcnow():
                        continue

                    if not _chapter_name2:
                        _chapter_name2 = temp1['chapter_name']
                    elif _chapter_name1 and _chapter_name2 and _chapter_name1 == _chapter_name2:
                        continue
                    else:
                        _chapter_name2 = temp1['chapter_name']

                    # print _chapter_name2

                    _sequential_name1 = None
                    _sequential_name2 = None
                    _sequential_start = None

                    sequential_list = list()
                    for temp2 in temp_list:
                        if _chapter_name1 == temp2['chapter_name']:

                            _sequential_name1 = temp2['sequential_name']
                            _sequential_id = temp2['sequential_id']
                            _sequential_start = temp2['sequential_start']

                            if _sequential_start and _sequential_start > datetime.utcnow():
                                continue

                            if not _sequential_name2:
                                _sequential_name2 = temp2['sequential_name']
                            elif _sequential_name1 and _sequential_name2 and _sequential_name1 == _sequential_name2:
                                continue
                            else:
                                _sequential_name2 = temp2['sequential_name']

                            # print '\t', _sequential_name1

                            _html5_source1 = None
                            _html5_source2 = None

                            vertical_list = list()
                            for temp3 in temp_list:
                                if _chapter_name1 == temp3['chapter_name'] and _sequential_name1 == temp3[
                                    'sequential_name']:

                                    _html5_source1 = temp3['html5_source']

                                    if not _html5_source2:
                                        _html5_source2 = temp3['html5_source']
                                    elif _html5_source1 and _html5_source2 and _html5_source1 == _html5_source2:
                                        continue
                                    else:
                                        _html5_source2 = temp3['html5_source']

                                    _vertical_name1 = temp3['vertical_name']
                                    _vertical_id = temp3['vertical_id']

                                    jump_url = 'http://{domain}/courses/{course_id}/jump_to/block-v1:{course}+type@vertical+block@{vertical_id}'.format(
                                        domain=request.META.get('HTTP_HOST'),
                                        course_id=course_id,
                                        course=course_id.replace('course-v1:', ''),
                                        vertical_id=_vertical_id
                                    )

                                    # print '\t\t', _vertical_name1, _html5_source2, jump_url

                                    vertical_list.append({
                                        'vertical_id': _vertical_id,
                                        'vertical_name': _vertical_name1,
                                        'video_url': _html5_source2,
                                        'jump_url': jump_url
                                    })

                            sequential_list.append({
                                'sequential_id': _sequential_id,
                                'sequential_name': _sequential_name1,
                                'vertical_list': vertical_list
                            })

                    chapter_list.append({
                        'chapter_id': _chapter_id,
                        'chapter_name': _chapter_name1,
                        'sequential_list': sequential_list
                    })

            # 강좌의 영상목록 생성 --- e

            settings_context = {
                'course': course,
                'chapter_list': chapter_list,
                'context_course': course_module,
                'user_edit': edit_check,
                'course_locator': course_key,
                'lms_link_for_about_page': utils.get_lms_link_for_about_page(course_key),
                'course_image_url': course_image_url(course_module, 'course_image'),
                'banner_image_url': course_image_url(course_module, 'banner_image'),
                'video_thumbnail_image_url': course_image_url(course_module, 'video_thumbnail_image'),
                'details_url': reverse_course_url('settings_handler', course_key),
                'about_page_editable': about_page_editable,
                'short_description_editable': short_description_editable,
                'upload_asset_url': upload_asset_url,
                'course_handler_url': reverse_course_url('course_handler', course_key),
                # 'language_options': settings.ALL_LANGUAGES,
                'language_options': course_lang_tmp,
                'credit_eligibility_enabled': credit_eligibility_enabled,
                'is_credit_course': False,
                'show_min_grade_warning': False,
                'enrollment_end_editable': enrollment_end_editable,
                'is_prerequisite_courses_enabled': is_prerequisite_courses_enabled(),
                'is_entrance_exams_enabled': is_entrance_exams_enabled(),
                'enable_extended_course_details': enable_extended_course_details,
                'difficult_degree_list': difficult_degree_list,
                'teacher_name': teacher_name,
                'preview_video': preview_video,
                'user_edit': edit_check,
                'classfy': classfy
            }

            if is_prerequisite_courses_enabled():
                courses, in_process_course_actions = get_courses_accessible_to_user(request)
                # exclude current course from the list of available courses
                courses = (course for course in courses if course.id != course_key)
                if courses:
                    courses, __ = _process_courses_list(courses, in_process_course_actions)
                settings_context.update({'possible_pre_requisite_courses': list(courses)})

            if credit_eligibility_enabled:
                if is_credit_course(course_key):
                    # get and all credit eligibility requirements
                    credit_requirements = get_credit_requirements(course_key)
                    # pair together requirements with same 'namespace' values
                    paired_requirements = {}
                    for requirement in credit_requirements:
                        namespace = requirement.pop("namespace")
                        paired_requirements.setdefault(namespace, []).append(requirement)

                    # if 'minimum_grade_credit' of a course is not set or 0 then
                    # show warning message to course author.
                    show_min_grade_warning = False if course_module.minimum_grade_credit > 0 else True
                    settings_context.update(
                        {
                            'is_credit_course': True,
                            'credit_requirements': paired_requirements,
                            'show_min_grade_warning': show_min_grade_warning,
                        }
                    )

            return render_to_response('settings.html', settings_context)
        elif 'application/json' in request.META.get('HTTP_ACCEPT', ''):
            if request.method == 'GET':
                # 강좌 상세 내용 조회시 강좌 생성일 및 이수증 생성일을 조회하여 같이 전달
                course_details = CourseDetails.fetch(course_key)
                course_details.need_lock = course_need_lock(request, course_key)
                with connections['default'].cursor() as cur:
                    query = '''
                        select ifnull(course_level, '') from course_overview_addinfo
                        where course_id = '{course_id}'
                    '''.format(course_id=course_key_string)
                    cur.execute(query)
                    course_level = cur.fetchone()[0]
                course_details.course_level = course_level
                return JsonResponse(
                    course_details,
                    # encoder serializes dates, old locations, and instances
                    encoder=CourseSettingsEncoder
                )
            # For every other possible method type submitted by the caller...
            else:
                # if pre-requisite course feature is enabled set pre-requisite course
                if is_prerequisite_courses_enabled():
                    prerequisite_course_keys = request.json.get('pre_requisite_courses', [])
                    if prerequisite_course_keys:
                        if not all(is_valid_course_key(course_key) for course_key in prerequisite_course_keys):
                            return JsonResponseBadRequest({"error": _("Invalid prerequisite course key")})
                        set_prerequisite_courses(course_key, prerequisite_course_keys)
                    else:
                        # None is chosen, so remove the course prerequisites
                        course_milestones = milestones_api.get_course_milestones(course_key=course_key, relationship="requires")
                        for milestone in course_milestones:
                            remove_prerequisite_course(course_key, milestone)

                # If the entrance exams feature has been enabled, we'll need to check for some
                # feature-specific settings and handle them accordingly
                # We have to be careful that we're only executing the following logic if we actually
                # need to create or delete an entrance exam from the specified course
                if is_entrance_exams_enabled():
                    course_entrance_exam_present = course_module.entrance_exam_enabled
                    entrance_exam_enabled = request.json.get('entrance_exam_enabled', '') == 'true'
                    ee_min_score_pct = request.json.get('entrance_exam_minimum_score_pct', None)
                    # If the entrance exam box on the settings screen has been checked...
                    if entrance_exam_enabled:
                        # Load the default minimum score threshold from settings, then try to override it
                        entrance_exam_minimum_score_pct = float(settings.ENTRANCE_EXAM_MIN_SCORE_PCT)
                        if ee_min_score_pct:
                            entrance_exam_minimum_score_pct = float(ee_min_score_pct)
                        if entrance_exam_minimum_score_pct.is_integer():
                            entrance_exam_minimum_score_pct = entrance_exam_minimum_score_pct / 100
                        # If there's already an entrance exam defined, we'll update the existing one
                        if course_entrance_exam_present:
                            exam_data = {
                                'entrance_exam_minimum_score_pct': entrance_exam_minimum_score_pct
                            }
                            update_entrance_exam(request, course_key, exam_data)
                        # If there's no entrance exam defined, we'll create a new one
                        else:
                            create_entrance_exam(request, course_key, entrance_exam_minimum_score_pct)

                    # If the entrance exam box on the settings screen has been unchecked,
                    # and the course has an entrance exam attached...
                    elif not entrance_exam_enabled and course_entrance_exam_present:
                        delete_entrance_exam(request, course_key)

                # Perform the normal update workflow for the CourseDetails model
                return JsonResponse(
                    CourseDetails.update_from_json(course_key, request.json, request.user),
                    encoder=CourseSettingsEncoder
                )


@login_required
@ensure_csrf_cookie
@require_http_methods(("GET", "POST", "PUT", "DELETE"))
@expect_json
def grading_handler(request, course_key_string, grader_index=None):
    """
    Course Grading policy configuration
    GET
        html: get the page
        json no grader_index: get the CourseGrading model (graceperiod, cutoffs, and graders)
        json w/ grader_index: get the specific grader
    PUT
        json no grader_index: update the Course through the CourseGrading model
        json w/ grader_index: create or update the specific grader (create if index out of range)
    """
    course_key = CourseKey.from_string(course_key_string)
    with modulestore().bulk_operations(course_key):
        course_module = get_course_and_check_access(course_key, request.user)

        if 'text/html' in request.META.get('HTTP_ACCEPT', '') and request.method == 'GET':
            course_details = CourseGradingModel.fetch(course_key)

            return render_to_response('settings_graders.html', {
                'context_course': course_module,
                'course_locator': course_key,
                'course_details': course_details,
                'grading_url': reverse_course_url('grading_handler', course_key),
                'is_credit_course': is_credit_course(course_key),
            })
        elif 'application/json' in request.META.get('HTTP_ACCEPT', ''):
            if request.method == 'GET':
                if grader_index is None:
                    return JsonResponse(
                        CourseGradingModel.fetch(course_key),
                        # encoder serializes dates, old locations, and instances
                        encoder=CourseSettingsEncoder
                    )
                else:
                    return JsonResponse(CourseGradingModel.fetch_grader(course_key, grader_index))
            elif request.method in ('POST', 'PUT'):  # post or put, doesn't matter.
                # update credit course requirements if 'minimum_grade_credit'
                # field value is changed
                if 'minimum_grade_credit' in request.json:
                    update_credit_course_requirements.delay(unicode(course_key))

                # None implies update the whole model (cutoffs, graceperiod, and graders) not a specific grader
                if grader_index is None:
                    return JsonResponse(
                        CourseGradingModel.update_from_json(course_key, request.json, request.user),
                        encoder=CourseSettingsEncoder
                    )
                else:
                    return JsonResponse(
                        CourseGradingModel.update_grader_from_json(course_key, request.json, request.user)
                    )
            elif request.method == "DELETE" and grader_index is not None:
                CourseGradingModel.delete_grader(course_key, grader_index, request.user)
                return JsonResponse()


def _refresh_course_tabs(request, course_module):
    """
    Automatically adds/removes tabs if changes to the course require them.

    Raises:
        InvalidTabsException: raised if there's a problem with the new version of the tabs.
    """

    def update_tab(tabs, tab_type, tab_enabled):
        """
        Adds or removes a course tab based upon whether it is enabled.
        """
        tab_panel = {
            "type": tab_type.type,
        }
        has_tab = tab_panel in tabs
        if tab_enabled and not has_tab:
            tabs.append(CourseTab.from_json(tab_panel))
        elif not tab_enabled and has_tab:
            tabs.remove(tab_panel)

    course_tabs = copy.copy(course_module.tabs)

    # Additionally update any tabs that are provided by non-dynamic course views
    for tab_type in CourseTabPluginManager.get_tab_types():
        if not tab_type.is_dynamic and tab_type.is_default:
            tab_enabled = tab_type.is_enabled(course_module, user=request.user)
            update_tab(course_tabs, tab_type, tab_enabled)

    CourseTabList.validate_tabs(course_tabs)

    # Save the tabs into the course if they have been changed
    if course_tabs != course_module.tabs:
        course_module.tabs = course_tabs

    course_id = course_module.id
    classfy = course_module.classfy
    middle_classfy = course_module.middle_classfy
    user_id = request.user.id
    old_classfy = u''
    old_middle_classfy = u''
    classfy_plus = course_module.classfy_plus
    course_period = course_module.course_period

    with connections['default'].cursor() as cur:
        query = """
                SELECT classfy, middle_classfy, classfy_plus, course_period, preview_video
                  FROM course_overview_addinfo
                 WHERE course_id = '{course_id}';
            """.format(course_id=course_id)

        cur.execute(query)
        print "--------------------------------> course.py s"
        print query
        print "--------------------------------> course.py e"
        old_classfy_data = cur.fetchall()

        if len(old_classfy_data) != 0:
            old_classfy = old_classfy_data[0][0]
            old_middle_classfy = old_classfy_data[0][1]
            old_classfy_plus = old_classfy_data[0][2]
            old_course_period = old_classfy_data[0][3]
            print type(old_classfy), type(old_middle_classfy), type(classfy), type(middle_classfy)

    with connections['default'].cursor() as cur:
        if classfy != old_classfy or middle_classfy != old_middle_classfy or classfy_plus != old_classfy_plus or course_period != old_course_period:
            query2 = """
                    UPDATE course_overview_addinfo
                       SET middle_classfy = '{middle_classfy}',
                           classfy = '{classfy}',
                           modify_id = '{user_id}',
                           classfy_plus = '{classfy_plus}',
                           course_period = '{course_period}',
                           modify_date = now()
                     WHERE course_id = '{course_id}';
                """.format(middle_classfy=middle_classfy, classfy=classfy, user_id=user_id, course_id=course_id,
                           classfy_plus=classfy_plus, course_period=course_period)

            print 'advanced addinfo update --------- ', query2
            cur.execute(query2)


def course_difficult_degree(request, course_key_string):
    with connections['default'].cursor() as cur:
        query = '''
          SELECT
                detail_code, detail_name, detail_ename
            FROM code_detail
           WHERE group_code = '007'
           AND   use_yn = 'Y'
           AND   delete_yn = 'N'
           ORDER BY detail_code asc
        '''
        cur.execute(query)
        rows = cur.fetchall()
        difficult_degree = {
            'degree_list': rows
        }
        cur.close()
    return difficult_degree


from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.models import User


# 아래의 함수는 외부로 노출되면 인증없이 강좌 수정하는 취약점이 발생합니다
# 절대로 외부에 노출되게 사용하지 마세요 ^_^
# 외부로 노출되어 취약점이 발생할 경우 책임은 본인에게 있습니다
@csrf_exempt
def api_advanced_settings_handler(request, course_key_string):
    master = User.objects.filter(is_staff=1).first()

    course_key = CourseKey.from_string(course_key_string)
    with modulestore().bulk_operations(course_key):
        course_module = get_course_and_check_access(course_key, master)
        try:
            params = {

                "audit_yn": {
                    u'deprecated': False,
                    u'display_name': u'\uccad\uac15\ud5c8\uc6a9 \uc5ec\ubd80',
                    u'help': u'Y\ub610\ub294 N\uc744 \uc785\ub825\ud569\ub2c8\ub2e4. Y\ub97c \uc785\ub825\ud560 \uacbd\uc6b0, \uac15\uc88c\uac00 \uc885\ub8cc\ub41c \uc774\ud6c4\uc5d0\ub3c4 \uccad\uac15\uc2e0\uccad\uc744 \ud558\uc2e4 \uc218 \uc788\uc2b5\ub2c8\ub2e4.',
                    u'value': u'N'
                },
                "catalog_visibility": {
                    u'deprecated': False,
                    u'display_name': u'\uac15\uc88c \ubaa9\ub85d\uc5d0\uc11c \uac15\uc88c \ubcf4\uc774\uac8c \ud558\uae30',
                    u'help': u"\uac15\uc88c \ubaa9\ub85d\uc5d0\uc11c \uac15\uc88c\ub97c \ubcf4\uc774\uac8c \ud560 \uc218 \uc788\ub294 \uad8c\ud55c\uc744 \uc124\uc815\ud569\ub2c8\ub2e4. \ub2e4\uc74c \uc138 \uac00\uc9c0 \uc911 \ud558\ub098\ub97c \uc120\ud0dd\ud560 \uc218 \uc788\uc2b5\ub2c8\ub2e4. 'both'(\ubaa9\ub85d\uc5d0\uc11c \ubcf4\uc774\uba70 \uac15\uc88c \uc0c1\uc138 \uc815\ubcf4\uc5d0\ub3c4 \uc811\uadfc \uac00\ub2a5 ), 'about'(\uac15\uc88c \uc0c1\uc138 \uc815\ubcf4\ub85c\ub9cc \uc811\uadfc \uac00\ub2a5), 'none'(\ubaa9\ub85d \ubc0f \uac15\uc88c \uc0c1\uc138 \uc815\ubcf4 \ubaa8\ub450 \uc811\uadfc \ubd88\uac00).",
                    u'value': u'about'
                }
            }

            is_valid, errors, updated_data = CourseMetadata.validate_and_update_from_json(
                course_module,
                params,
                user=master,
            )

            if 'audit_yn' in params:
                try:
                    audit_yn = params['audit_yn']['value']
                    audit_yn = 'N' if not audit_yn or audit_yn not in ['Y', 'y'] else 'Y'
                    with connections['default'].cursor() as cur:
                        query = """
                            UPDATE course_overview_addinfo
                               SET audit_yn = '{audit_yn}'
                             WHERE course_id = '{course_id}';
                        """.format(audit_yn=audit_yn, course_id=course_key_string)
                        cur.execute(query)
                except Exception as e:
                    is_valid = False
                    errors.append({'message': 'audit_yn value is not collect', 'model': None})
                    print e

            if is_valid:
                try:
                    # update the course tabs if required by any setting changes
                    _refresh_course_tabs(request, course_module)
                except InvalidTabsException as err:
                    log.exception(err.message)
                    response_message = [
                        {
                            'message': _('An error occurred while trying to save your tabs'),
                            'model': {'display_name': _('Tabs Exception')}
                        }
                    ]
                    return JsonResponseBadRequest(response_message)

                # now update mongo
                modulestore().update_item(course_module, master.id)

                return JsonResponse(updated_data)
            else:
                return JsonResponseBadRequest(errors)

        # Handle all errors that validation doesn't catch
        except (TypeError, ValueError, InvalidTabsException) as err:
            return HttpResponseBadRequest(
                django.utils.html.escape(err.message),
                content_type="text/plain"
            )


@login_required
@ensure_csrf_cookie
@require_http_methods(("GET", "POST", "PUT"))
@expect_json
def advanced_settings_handler(request, course_key_string):
    # 안녕하세요 advanced_settings_handler 함수를 수정하려는 용사님!
    # 용사님에게 수정하실 때 주의할 사항이 있습니다.
    # 그것은 바로...

    # 이거 수정하실 때 위에 있는 api_advanced_settings_handler 함수도 같이 수정해주세요
    # 이거 수정하실 때 위에 있는 api_advanced_settings_handler 함수도 같이 수정해주세요
    # 이거 수정하실 때 위에 있는 api_advanced_settings_handler 함수도 같이 수정해주세요

    """
    Course settings configuration
    GET
        html: get the page
        json: get the model
    PUT, POST
        json: update the Course's settings. The payload is a json rep of the
            metadata dicts.
    """
    print course_key_string
    course_key = CourseKey.from_string(course_key_string)
    with modulestore().bulk_operations(course_key):
        course_module = get_course_and_check_access(course_key, request.user)
        if 'text/html' in request.META.get('HTTP_ACCEPT', '') and request.method == 'GET':

            need_lock = course_need_lock(request, course_key_string)
            difficult_degree_list = course_difficult_degree(request, course_key_string)
            advanced_dict = CourseMetadata.fetch(course_module)

            # difficult_degree setting
            with connections['default'].cursor() as cur:
                query = """
                                SELECT audit_yn
                                  FROM course_overview_addinfo
                                 WHERE course_id = '{course_id}';
                            """.format(course_id=course_key_string)
                cur.execute(query)

                audit_yn = cur.fetchone()[0] if cur.rowcount else 'N'

            with connections['default'].cursor() as cur:
                query = """
                                SELECT ifnull(preview_video, '')
                                  FROM course_overview_addinfo
                                 WHERE course_id = '{course_id}';
                            """.format(course_id=course_key_string)
                cur.execute(query)

                preview_video = cur.fetchone()[0]

            need_lock_dict = {
                'hidden': True,
                'display_name': _("is_course_lock"),
                'help': '',
                'value': need_lock
            }

            audit_yn_dict = {
                'deprecated': False,
                'display_name': _("audit_yn"),
                'help': u'Y또는 N을 입력합니다. Y를 입력할 경우, 강좌가 종료된 이후에도 청강신청을 하실 수 있습니다.',
                'value': audit_yn
            }

            advanced_dict['audit_yn'] = audit_yn_dict
            advanced_dict['need_lock'] = need_lock_dict

            return render_to_response('settings_advanced.html', {
                'context_course': course_module,
                'advanced_dict': advanced_dict,
                'difficult_degree_list': difficult_degree_list,
                'advanced_settings_url': reverse_course_url('advanced_settings_handler', course_key),
                'is_staff': {"is_staff": 'true'} if request.user.is_staff is True else {"is_staff": 'false'}
            })

        elif 'application/json' in request.META.get('HTTP_ACCEPT', ''):
            if request.method == 'GET':
                return JsonResponse(CourseMetadata.fetch(course_module))
            else:
                try:
                    # validate data formats and update the course module.
                    # Note: don't update mongo yet, but wait until after any tabs are changed
                    params = request.json

                    is_valid, errors, updated_data = CourseMetadata.validate_and_update_from_json(
                        course_module,
                        params,
                        user=request.user,
                    )
                    audit_yn = 'Y'
                    teacher_name = ''

                    from xblock.core import XBlock

                    if 'user_edit' in params:
                        is_use = params['user_edit']['value']

                        # 에디터 이용하기 선택시 기본 overview html 으로 셋팅되도록 함
                        if is_use == 'N':
                            about_descriptor = XBlock.load_class('about')
                            overview_template = about_descriptor.get_template('overview.yaml')

                            if overview_template:
                                updated_data.update(overview_template=overview_template['data'])

                    if 'audit_yn' in params:
                        audit_yn = params['audit_yn']['value']
                        audit_yn = 'N' if not audit_yn or audit_yn not in ['Y', 'y'] else 'Y'
                    if 'teacher_name' in params:
                        teacher_name = params['teacher_name']['value']

                    try:
                        with connections['default'].cursor() as cur:
                            if 'audit_yn' in params:
                                query = """
                                    UPDATE course_overview_addinfo
                                       SET audit_yn = '{audit_yn}'
                                     WHERE course_id = '{course_id}';
                                """.format(audit_yn=audit_yn, course_id=course_key_string)
                                cur.execute(query)
                            if 'teacher_name' in params:
                                query2 = """
                                    UPDATE course_overview_addinfo
                                       SET teacher_name = '{teacher_name}'
                                     WHERE course_id = '{course_id}';
                                """.format(course_id=course_key_string,
                                           teacher_name=teacher_name)
                                cur.execute(query2)
                    except Exception as e:
                        is_valid = False
                        errors.append({'message': 'audit_yn or teacher_name value is not collect', 'model': None})
                        print e

                    if is_valid:
                        try:
                            # update the course tabs if required by any setting changes
                            _refresh_course_tabs(request, course_module)
                        except InvalidTabsException as err:
                            log.exception(err.message)
                            response_message = [
                                {
                                    'message': _('An error occurred while trying to save your tabs'),
                                    'model': {'display_name': _('Tabs Exception')}
                                }
                            ]
                            return JsonResponseBadRequest(response_message)

                        # now update mongo
                        modulestore().update_item(course_module, request.user.id)

                        return JsonResponse(updated_data)
                    else:
                        return JsonResponseBadRequest(errors)

                # Handle all errors that validation doesn't catch
                except (TypeError, ValueError, InvalidTabsException) as err:
                    return HttpResponseBadRequest(
                        django.utils.html.escape(err.message),
                        content_type="text/plain"
                    )


class TextbookValidationError(Exception):
    "An error thrown when a textbook input is invalid"
    pass


def course_need_lock(request, course_key_string):
    if not request.user.is_staff and str(course_key_string).startswith('course'):
        from django.db import connections
        with connections['default'].cursor() as cursor:
            query = '''
                SELECT 
                    a.course_id,
                    IF(DATE_FORMAT(c.start, '%Y-%m-%d %H:%i') <> '2030-01-01 00:00'
                    AND (NOW() > MIN(b.created_date)
                            OR NOW() > ADDDATE(c.end, INTERVAL 30 DAY)),
                        1,
                        0) need_lock
                FROM
                    course_structures_coursestructure a
                        JOIN
                    course_overviews_courseoverview c ON a.course_id = c.id
                        LEFT JOIN
                    certificates_generatedcertificate b ON a.course_id = b.course_id
                WHERE
                    a.course_id = '{course_id}'
                GROUP BY a.course_id , a.created;                           
            '''.format(course_id=course_key_string)
            cursor.execute(query)
            desc = cursor.description
            result = [dict(zip([col[0] for col in desc], row)) for row in cursor.fetchall()][0]
        need_lock = result['need_lock']
    else:
        need_lock = 0
    return need_lock


def course_difficult_degree(request, course_key_string):
    with connections['default'].cursor() as cur:
        query = '''
          SELECT
                detail_code, detail_name, detail_ename
            FROM code_detail
           WHERE group_code = '007'
           AND   use_yn = 'Y'
           AND   delete_yn = 'N'
           ORDER BY detail_code asc
        '''
        cur.execute(query)
        rows = cur.fetchall()
        difficult_degree = {
            'degree_list': rows
        }
        cur.close()
    return difficult_degree


def validate_textbooks_json(text):
    """
    Validate the given text as representing a single PDF textbook
    """
    try:
        textbooks = json.loads(text)
    except ValueError:
        raise TextbookValidationError("invalid JSON")
    if not isinstance(textbooks, (list, tuple)):
        raise TextbookValidationError("must be JSON list")
    for textbook in textbooks:
        validate_textbook_json(textbook)
    # check specified IDs for uniqueness
    all_ids = [textbook["id"] for textbook in textbooks if "id" in textbook]
    unique_ids = set(all_ids)
    if len(all_ids) > len(unique_ids):
        raise TextbookValidationError("IDs must be unique")
    return textbooks


def validate_textbook_json(textbook):
    """
    Validate the given text as representing a list of PDF textbooks
    """
    if isinstance(textbook, basestring):
        try:
            textbook = json.loads(textbook)
        except ValueError:
            raise TextbookValidationError("invalid JSON")
    if not isinstance(textbook, dict):
        raise TextbookValidationError("must be JSON object")
    if not textbook.get("tab_title"):
        raise TextbookValidationError("must have tab_title")
    tid = unicode(textbook.get("id", ""))
    if tid and not tid[0].isdigit():
        raise TextbookValidationError("textbook ID must start with a digit")
    return textbook


def assign_textbook_id(textbook, used_ids=()):
    """
    Return an ID that can be assigned to a textbook
    and doesn't match the used_ids
    """
    tid = BlockUsageLocator.clean(textbook["tab_title"])
    if not tid[0].isdigit():
        # stick a random digit in front
        tid = random.choice(string.digits) + tid
    while tid in used_ids:
        # add a random ASCII character to the end
        tid = tid + random.choice(string.ascii_lowercase)
    return tid


@require_http_methods(("GET", "POST", "PUT"))
@login_required
@ensure_csrf_cookie
def textbooks_list_handler(request, course_key_string):
    """
    A RESTful handler for textbook collections.

    GET
        html: return textbook list page (Backbone application)
        json: return JSON representation of all textbooks in this course
    POST
        json: create a new textbook for this course
    PUT
        json: overwrite all textbooks in the course with the given list
    """
    course_key = CourseKey.from_string(course_key_string)
    store = modulestore()
    with store.bulk_operations(course_key):
        course = get_course_and_check_access(course_key, request.user)

        if "application/json" not in request.META.get('HTTP_ACCEPT', 'text/html'):
            # return HTML page
            upload_asset_url = reverse_course_url('assets_handler', course_key)
            textbook_url = reverse_course_url('textbooks_list_handler', course_key)
            return render_to_response('textbooks.html', {
                'context_course': course,
                'textbooks': course.pdf_textbooks,
                'upload_asset_url': upload_asset_url,
                'textbook_url': textbook_url,
            })

        # from here on down, we know the client has requested JSON
        if request.method == 'GET':
            return JsonResponse(course.pdf_textbooks)
        elif request.method == 'PUT':
            try:
                textbooks = validate_textbooks_json(request.body)
            except TextbookValidationError as err:
                return JsonResponse({"error": text_type(err)}, status=400)

            tids = set(t["id"] for t in textbooks if "id" in t)
            for textbook in textbooks:
                if "id" not in textbook:
                    tid = assign_textbook_id(textbook, tids)
                    textbook["id"] = tid
                    tids.add(tid)

            if not any(tab['type'] == 'pdf_textbooks' for tab in course.tabs):
                course.tabs.append(CourseTab.load('pdf_textbooks'))
            course.pdf_textbooks = textbooks
            store.update_item(course, request.user.id)
            return JsonResponse(course.pdf_textbooks)
        elif request.method == 'POST':
            # create a new textbook for the course
            try:
                textbook = validate_textbook_json(request.body)
            except TextbookValidationError as err:
                return JsonResponse({"error": text_type(err)}, status=400)
            if not textbook.get("id"):
                tids = set(t["id"] for t in course.pdf_textbooks if "id" in t)
                textbook["id"] = assign_textbook_id(textbook, tids)
            existing = course.pdf_textbooks
            existing.append(textbook)
            course.pdf_textbooks = existing
            if not any(tab['type'] == 'pdf_textbooks' for tab in course.tabs):
                course.tabs.append(CourseTab.load('pdf_textbooks'))
            store.update_item(course, request.user.id)
            resp = JsonResponse(textbook, status=201)
            resp["Location"] = reverse_course_url(
                'textbooks_detail_handler',
                course.id,
                kwargs={'textbook_id': textbook["id"]}
            )
            return resp


@login_required
@ensure_csrf_cookie
@require_http_methods(("GET", "POST", "PUT", "DELETE"))
def textbooks_detail_handler(request, course_key_string, textbook_id):
    """
    JSON API endpoint for manipulating a textbook via its internal ID.
    Used by the Backbone application.

    GET
        json: return JSON representation of textbook
    POST or PUT
        json: update textbook based on provided information
    DELETE
        json: remove textbook
    """
    course_key = CourseKey.from_string(course_key_string)
    store = modulestore()
    with store.bulk_operations(course_key):
        course_module = get_course_and_check_access(course_key, request.user)
        matching_id = [tb for tb in course_module.pdf_textbooks
                       if unicode(tb.get("id")) == unicode(textbook_id)]
        if matching_id:
            textbook = matching_id[0]
        else:
            textbook = None

        if request.method == 'GET':
            if not textbook:
                return JsonResponse(status=404)
            return JsonResponse(textbook)
        elif request.method in ('POST', 'PUT'):  # can be either and sometimes
            # django is rewriting one to the other
            try:
                new_textbook = validate_textbook_json(request.body)
            except TextbookValidationError as err:
                return JsonResponse({"error": text_type(err)}, status=400)
            new_textbook["id"] = textbook_id
            if textbook:
                i = course_module.pdf_textbooks.index(textbook)
                new_textbooks = course_module.pdf_textbooks[0:i]
                new_textbooks.append(new_textbook)
                new_textbooks.extend(course_module.pdf_textbooks[i + 1:])
                course_module.pdf_textbooks = new_textbooks
            else:
                course_module.pdf_textbooks.append(new_textbook)
            store.update_item(course_module, request.user.id)
            return JsonResponse(new_textbook, status=201)
        elif request.method == 'DELETE':
            if not textbook:
                return JsonResponse(status=404)
            i = course_module.pdf_textbooks.index(textbook)
            remaining_textbooks = course_module.pdf_textbooks[0:i]
            remaining_textbooks.extend(course_module.pdf_textbooks[i + 1:])
            course_module.pdf_textbooks = remaining_textbooks
            store.update_item(course_module, request.user.id)
            return JsonResponse()


def remove_content_or_experiment_group(request, store, course, configuration, group_configuration_id, group_id=None):
    """
    Remove content group or experiment group configuration only if it's not in use.
    """
    configuration_index = course.user_partitions.index(configuration)
    if configuration.scheme.name == RANDOM_SCHEME:
        usages = GroupConfiguration.get_content_experiment_usage_info(store, course)
        used = int(group_configuration_id) in usages

        if used:
            return JsonResponse(
                {"error": _("This group configuration is in use and cannot be deleted.")},
                status=400
            )
        course.user_partitions.pop(configuration_index)
    elif configuration.scheme.name == COHORT_SCHEME:
        if not group_id:
            return JsonResponse(status=404)

        group_id = int(group_id)
        usages = GroupConfiguration.get_partitions_usage_info(store, course)
        used = group_id in usages

        if used:
            return JsonResponse(
                {"error": _("This content group is in use and cannot be deleted.")},
                status=400
            )

        matching_groups = [group for group in configuration.groups if group.id == group_id]
        if matching_groups:
            group_index = configuration.groups.index(matching_groups[0])
            configuration.groups.pop(group_index)
        else:
            return JsonResponse(status=404)

        course.user_partitions[configuration_index] = configuration

    store.update_item(course, request.user.id)
    return JsonResponse(status=204)


@require_http_methods(("GET", "POST"))
@login_required
@ensure_csrf_cookie
def group_configurations_list_handler(request, course_key_string):
    """
    A RESTful handler for Group Configurations

    GET
        html: return Group Configurations list page (Backbone application)
    POST
        json: create new group configuration
    """
    course_key = CourseKey.from_string(course_key_string)
    store = modulestore()
    with store.bulk_operations(course_key):
        course = get_course_and_check_access(course_key, request.user)

        if 'text/html' in request.META.get('HTTP_ACCEPT', 'text/html'):
            group_configuration_url = reverse_course_url('group_configurations_list_handler', course_key)
            course_outline_url = reverse_course_url('course_handler', course_key)
            should_show_experiment_groups = are_content_experiments_enabled(course)
            if should_show_experiment_groups:
                experiment_group_configurations = GroupConfiguration.get_split_test_partitions_with_usage(store, course)
            else:
                experiment_group_configurations = None

            all_partitions = GroupConfiguration.get_all_user_partition_details(store, course)
            should_show_enrollment_track = False
            has_content_groups = False
            displayable_partitions = []
            for partition in all_partitions:
                if partition['scheme'] == COHORT_SCHEME:
                    has_content_groups = True
                    displayable_partitions.append(partition)
                elif partition['scheme'] == ENROLLMENT_SCHEME:
                    should_show_enrollment_track = len(partition['groups']) > 1

                    # Add it to the front of the list if it should be shown.
                    if should_show_enrollment_track:
                        displayable_partitions.insert(0, partition)
                elif partition['scheme'] != RANDOM_SCHEME:
                    # Experiment group configurations are handled explicitly above. We don't
                    # want to display their groups twice.
                    displayable_partitions.append(partition)

            # Add empty content group if there is no COHORT User Partition in the list.
            # This will add ability to add new groups in the view.
            if not has_content_groups:
                displayable_partitions.append(GroupConfiguration.get_or_create_content_group(store, course))

            return render_to_response('group_configurations.html', {
                'context_course': course,
                'group_configuration_url': group_configuration_url,
                'course_outline_url': course_outline_url,
                'experiment_group_configurations': experiment_group_configurations,
                'should_show_experiment_groups': should_show_experiment_groups,
                'all_group_configurations': displayable_partitions,
                'should_show_enrollment_track': should_show_enrollment_track
            })
        elif "application/json" in request.META.get('HTTP_ACCEPT'):
            if request.method == 'POST':
                # create a new group configuration for the course
                try:
                    new_configuration = GroupConfiguration(request.body, course).get_user_partition()
                except GroupConfigurationsValidationError as err:
                    return JsonResponse({"error": text_type(err)}, status=400)

                course.user_partitions.append(new_configuration)
                response = JsonResponse(new_configuration.to_json(), status=201)

                response["Location"] = reverse_course_url(
                    'group_configurations_detail_handler',
                    course.id,
                    kwargs={'group_configuration_id': new_configuration.id}
                )
                store.update_item(course, request.user.id)
                return response
        else:
            return HttpResponse(status=406)


@login_required
@ensure_csrf_cookie
@require_http_methods(("POST", "PUT", "DELETE"))
def group_configurations_detail_handler(request, course_key_string, group_configuration_id, group_id=None):
    """
    JSON API endpoint for manipulating a group configuration via its internal ID.
    Used by the Backbone application.

    POST or PUT
        json: update group configuration based on provided information
    """
    course_key = CourseKey.from_string(course_key_string)
    store = modulestore()
    with store.bulk_operations(course_key):
        course = get_course_and_check_access(course_key, request.user)
        matching_id = [p for p in course.user_partitions
                       if unicode(p.id) == unicode(group_configuration_id)]
        if matching_id:
            configuration = matching_id[0]
        else:
            configuration = None

        if request.method in ('POST', 'PUT'):  # can be either and sometimes
            # django is rewriting one to the other
            try:
                new_configuration = GroupConfiguration(request.body, course, group_configuration_id).get_user_partition()
            except GroupConfigurationsValidationError as err:
                return JsonResponse({"error": text_type(err)}, status=400)

            if configuration:
                index = course.user_partitions.index(configuration)
                course.user_partitions[index] = new_configuration
            else:
                course.user_partitions.append(new_configuration)
            store.update_item(course, request.user.id)
            configuration = GroupConfiguration.update_usage_info(store, course, new_configuration)
            return JsonResponse(configuration, status=201)

        elif request.method == "DELETE":
            if not configuration:
                return JsonResponse(status=404)

            return remove_content_or_experiment_group(
                request=request,
                store=store,
                course=course,
                configuration=configuration,
                group_configuration_id=group_configuration_id,
                group_id=group_id
            )


def are_content_experiments_enabled(course):
    """
    Returns True if content experiments have been enabled for the course.
    """
    return (
            'split_test' in ADVANCED_COMPONENT_TYPES and
            'split_test' in course.advanced_modules
    )


def _get_course_creator_status(user):
    """
    Helper method for returning the course creator status for a particular user,
    taking into account the values of DISABLE_COURSE_CREATION and ENABLE_CREATOR_GROUP.

    If the user passed in has not previously visited the index page, it will be
    added with status 'unrequested' if the course creator group is in use.
    """

    if user.is_staff:
        course_creator_status = 'granted'
    elif settings.FEATURES.get('DISABLE_COURSE_CREATION', False):
        course_creator_status = 'disallowed_for_this_site'
    elif settings.FEATURES.get('ENABLE_CREATOR_GROUP', False):
        course_creator_status = get_course_creator_status(user)
        if course_creator_status is None:
            # User not grandfathered in as an existing user, has not previously visited the dashboard page.
            # Add the user to the course creator admin table with status 'unrequested'.
            add_user_with_status_unrequested(user)
            course_creator_status = get_course_creator_status(user)
    else:
        course_creator_status = 'granted'

    return course_creator_status
