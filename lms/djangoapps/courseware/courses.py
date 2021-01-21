# -*- coding: utf-8 -*-
"""
Functions for accessing and displaying courses within the
courseware.
"""
import logging, time
from collections import defaultdict
from datetime import datetime
import traceback

import branding
import pytz
from courseware.access import has_access
from courseware.access_response import StartDateError, MilestoneAccessError
from courseware.date_summary import (
    CourseEndDate,
    CourseStartDate,
    TodaysDate,
    VerificationDeadlineDate,
    VerifiedUpgradeDeadlineDate,
    CertificateAvailableDate
)
from courseware.model_data import FieldDataCache
from courseware.module_render import get_module
from courseware.models import CourseOverviewAddinfo
from django.conf import settings
from django.urls import reverse
from django.http import Http404, QueryDict
from enrollment.api import get_course_enrollment_details
from edxmako.shortcuts import render_to_string, render_to_response
from fs.errors import ResourceNotFound
from lms.djangoapps.courseware.courseware_access_exception import CoursewareAccessException
from lms.djangoapps.courseware.exceptions import CourseAccessRedirect
from opaque_keys.edx.keys import UsageKey, CourseKey
from openedx.core.djangoapps.content.course_overviews.models import CourseOverview
from openedx.core.djangoapps.site_configuration import helpers as configuration_helpers
from path import Path as path
from six import text_type
from static_replace import replace_static_urls
from student.models import CourseEnrollment
from survey.utils import is_survey_required_and_unanswered
from util.date_utils import strftime_localized
from xmodule.modulestore.django import modulestore
from xmodule.modulestore.exceptions import ItemNotFoundError
from xmodule.x_module import STUDENT_VIEW

from django.views.decorators.csrf import csrf_exempt, ensure_csrf_cookie
from util.json_request import JsonResponse
from django.db import connections
from pymongo import MongoClient
from bson import ObjectId

log = logging.getLogger(__name__)


def get_course(course_id, depth=0):
    """
    Given a course id, return the corresponding course descriptor.

    If the course does not exist, raises a ValueError.  This is appropriate
    for internal use.

    depth: The number of levels of children for the modulestore to cache.
    None means infinite depth.  Default is to fetch no children.
    """
    course = modulestore().get_course(course_id, depth=depth)
    if course is None:
        raise ValueError(u"Course not found: {0}".format(course_id))
    return course


def get_course_by_id(course_key, depth=0):
    """
    Given a course id, return the corresponding course descriptor.

    If such a course does not exist, raises a 404.

    depth: The number of levels of children for the modulestore to cache. None means infinite depth
    """
    with modulestore().bulk_operations(course_key):
        course = modulestore().get_course(course_key, depth=depth)
    if course:
        return course
    else:
        raise Http404("Course not found: {}.".format(unicode(course_key)))


def get_course_with_access(user, action, course_key, depth=0, check_if_enrolled=False, check_survey_complete=True):
    """
    Given a course_key, look up the corresponding course descriptor,
    check that the user has the access to perform the specified action
    on the course, and return the descriptor.

    Raises a 404 if the course_key is invalid, or the user doesn't have access.

    depth: The number of levels of children for the modulestore to cache. None means infinite depth

    check_if_enrolled: If true, additionally verifies that the user is either enrolled in the course
      or has staff access.
    check_survey_complete: If true, additionally verifies that the user has either completed the course survey
      or has staff access.
      Note: We do not want to continually add these optional booleans.  Ideally,
      these special cases could not only be handled inside has_access, but could
      be plugged in as additional callback checks for different actions.
    """
    course = get_course_by_id(course_key, depth)
    check_course_access(course, user, action, check_if_enrolled, check_survey_complete)
    return course


def get_course_overview_with_access(user, action, course_key, check_if_enrolled=False):
    """
    Given a course_key, look up the corresponding course overview,
    check that the user has the access to perform the specified action
    on the course, and return the course overview.

    Raises a 404 if the course_key is invalid, or the user doesn't have access.

    check_if_enrolled: If true, additionally verifies that the user is either enrolled in the course
      or has staff access.
    """
    try:
        course_overview = CourseOverview.get_from_id(course_key)
    except CourseOverview.DoesNotExist:
        raise Http404("Course not found.")
    check_course_access(course_overview, user, action, check_if_enrolled)
    return course_overview


@csrf_exempt
def course_search_list(request):
    if request.is_ajax():
        # print "search_list -- courseware.py"
        with connections['default'].cursor() as cur:
            query = '''
                SELECT DISTINCT display_name
                  FROM course_overviews_courseoverview
                  WHERE catalog_visibility = 'both'
                   AND enrollment_start IS NOT NULL
                   AND start < '2030-01-01'
                 ORDER BY display_name;
            '''
            cur.execute(query)
            course_tup = cur.fetchall()
            course_list = list()
            for course in course_tup:
                course_list.append(course[0])
            # print "-----courseware------",course_list
            # print 'course_listcourse_listcourse_list',course_list
            return JsonResponse({'course_search_list': course_list})
    pass


def check_course_access(course, user, action, check_if_enrolled=False, check_survey_complete=True):
    """
    Check that the user has the access to perform the specified action
    on the course (CourseDescriptor|CourseOverview).

    check_if_enrolled: If true, additionally verifies that the user is enrolled.
    check_survey_complete: If true, additionally verifies that the user has completed the survey.
    """
    # Allow staff full access to the course even if not enrolled
    if has_access(user, 'staff', course.id):
        return

    access_response = has_access(user, action, course, course.id)
    if not access_response:
        # Redirect if StartDateError
        if isinstance(access_response, StartDateError):
            start_date = strftime_localized(course.start, 'SHORT_DATE')
            params = QueryDict(mutable=True)
            params['notlive'] = start_date
            raise CourseAccessRedirect('{dashboard_url}?{params}'.format(
                dashboard_url=reverse('dashboard'),
                params=params.urlencode()
            ), access_response)

        # Redirect if the user must answer a survey before entering the course.
        if isinstance(access_response, MilestoneAccessError):
            raise CourseAccessRedirect('{dashboard_url}'.format(
                dashboard_url=reverse('dashboard'),
            ), access_response)

        # Deliberately return a non-specific error message to avoid
        # leaking info about access control settings
        raise CoursewareAccessException(access_response)

    if check_if_enrolled:
        # If the user is not enrolled, redirect them to the about page
        if not CourseEnrollment.is_enrolled(user, course.id):
            raise CourseAccessRedirect(reverse('about_course', args=[unicode(course.id)]))

    # Redirect if the user must answer a survey before entering the course.
    if check_survey_complete and action == 'load':
        if is_survey_required_and_unanswered(user, course):
            raise CourseAccessRedirect(reverse('course_survey', args=[unicode(course.id)]))


def age_specific_course(request):
    from student.views.management import index_courses
    age_group = {}

    with connections['default'].cursor() as cur:
        query2 = 'select course_id, course_division from tb_main_course where course_division like "%0s";'

        cur.execute(query2)
        new_course = cur.fetchall()

        for i in range(1, 6):
            courses = [CourseKey.from_string(course[0]) for course in new_course if course[1] == str(i) + '0s']

            age_group[str(i) + '0'] = index_courses(user=request.user, filter_={'id__in': courses})

    return render_to_response('courseware/age_specific_course.html', {'courses': age_group})


def can_self_enroll_in_course(course_key):
    """
    Returns True if the user can enroll themselves in a course.

    Note: an example of a course that a user cannot enroll in directly
    is a CCX course. For such courses, a user can only be enrolled by
    a CCX coach.
    """
    if hasattr(course_key, 'ccx'):
        return False
    return True


def course_open_for_self_enrollment(course_key):
    """
    For a given course_key, determine if the course is available for enrollment
    """
    # Check to see if learners can enroll themselves.
    if not can_self_enroll_in_course(course_key):
        return False

    # Check the enrollment start and end dates.
    course_details = get_course_enrollment_details(unicode(course_key))
    now = datetime.now().replace(tzinfo=pytz.UTC)
    start = course_details['enrollment_start']
    end = course_details['enrollment_end']

    start = start if start is not None else now
    end = end if end is not None else now

    # If we are not within the start and end date for enrollment.
    if now < start or end < now:
        return False

    return True


def find_file(filesystem, dirs, filename):
    """
    Looks for a filename in a list of dirs on a filesystem, in the specified order.

    filesystem: an OSFS filesystem
    dirs: a list of path objects
    filename: a string

    Returns d / filename if found in dir d, else raises ResourceNotFound.
    """
    for directory in dirs:
        filepath = path(directory) / filename
        if filesystem.exists(filepath):
            return filepath
    raise ResourceNotFound(u"Could not find {0}".format(filename))


def get_course_about_section(request, course, section_key):
    """
    This returns the snippet of html to be rendered on the course about page,
    given the key for the section.

    Valid keys:
    - overview
    - about_sidebar_html
    - short_description
    - description
    - key_dates (includes start, end, exams, etc)
    - video
    - course_staff_short
    - course_staff_extended
    - requirements
    - syllabus
    - textbook
    - faq
    - effort
    - more_info
    - ocw_links
    """

    # Many of these are stored as html files instead of some semantic
    # markup. This can change without effecting this interface when we find a
    # good format for defining so many snippets of text/html.
    course_week = False
    course_video = False
    if section_key == 'course_week':
        course_week = True
        section_key = 'effort'
    if section_key == 'course_video':
        course_video = True
        section_key = 'effort'

    html_sections = {
        'short_description',
        'teacher_name',
        'description',
        'key_dates',
        'video',
        'course_staff_short',
        'course_staff_extended',
        'requirements',
        'syllabus',
        'textbook',
        'faq',
        'more_info',
        'overview',
        'effort',
        'end_date',
        'prerequisites',
        'about_sidebar_html',
        'ocw_links',
        'preview_video'
    }

    if section_key in html_sections:
        try:
            loc = course.location.replace(category='about', name=section_key)

            # Use an empty cache
            field_data_cache = FieldDataCache([], course.id, request.user)

            about_module = get_module(
                request.user,
                request,
                loc,
                field_data_cache,
                log_if_not_found=False,
                wrap_xmodule_display=False,
                static_asset_path=course.static_asset_path,
                course=course
            )

            html = ''

            if about_module is not None:
                try:
                    html = about_module.render(STUDENT_VIEW).content
                    html = html.replace('<label for="toggle"></label>', '<a href="javascript:click_syllabus_label();"><label for="toggle"></label></a>')

                except Exception:  # pylint: disable=broad-except
                    html = render_to_string('courseware/error-message.html', None)
                    log.exception(
                        u"Error rendering course=%s, section_key=%s",
                        course, section_key
                    )

            if section_key == "effort":
                if html.__len__() > 5:
                    if course_week:
                        if html.strip().find('#') != -1:
                            html = html.strip().split('#')[0]
                        else:
                            html = html.strip()[6:] + '주'
                    elif course_video:
                        if html.strip().find('#') != -1:
                            html = html.strip().split('#')[1].split('$')[0].split(':')[0] + '시간 ' + \
                                   html.strip().split('#')[1].split('$')[0].split(':')[1] + '분'
                        else:
                            html = ''
                    else:
                        html = html.strip()[:5]

                        if ':' in html:
                            html = html.split(':')[0] + '시간 ' + html.split(':')[1] + '분'
                        else:
                            html += '시간'
                else:
                    html = ''

            if section_key == "preview_video":

                try:

                    course_id = str(course.id)

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

                    cnt = 0
                    url1 = ''
                    url2 = ''

                    for active_version in active_versions:
                        pb = active_version.get('versions').get('published-branch')
                        wiki_slug = active_version.get('search_targets').get('wiki_slug')

                        if wiki_slug and pb:
                            print 'published-branch is [%s]' % pb

                            structure = db.modulestore.structures.find_one({'_id': ObjectId(pb)},
                                                                           {"blocks": {
                                                                               "$elemMatch": {"block_type": "course"}}})
                            block = structure.get('blocks')[0]

                            course_fields = block.get('fields')
                            chapters = course_fields.get('children')

                            for chapter_type, chapter_id in chapters:
                                # print block_type, block_id
                                chapter = db.modulestore.structures.find_one({'_id': ObjectId(pb)}, {"blocks": {
                                    "$elemMatch": {"block_id": chapter_id,
                                                   "fields.visible_to_staff_only": {"$ne": True}}}})

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
                                        vertical = db.modulestore.structures.find_one({'_id': ObjectId(pb)},
                                                                                      {"blocks": {
                                                                                          "$elemMatch": {
                                                                                              "block_id": vertical_id,
                                                                                              "fields.visible_to_staff_only": {
                                                                                                  "$ne": True}}}})

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

                                                if cnt == 0:
                                                    url1 = html5_source

                                                cnt += 1

                                                #print '----------------------------------------------------------- s'
                                                #print chapter_name, chapter_start, sequential_name, sequential_start, vertical_name, html5_source
                                                #print '----------------------------------------------------------- e'

                    try:
                        video_url = CourseOverviewAddinfo.objects.get(course_id=course.id).preview_video

                        if not video_url:
                            video_url = url1
                    except:
                        if url1:
                            video_url = url1
                        else:
                            video_url = ''
                    print video_url
                    print url1

                    html = '<video class="preview_video_id" title="Preview Video" width="560" height="315" src="'+video_url+'#t=0:01:01, 0:02:02" controls></video>'
                except Exception as e:
                    print traceback.print_exc(e)
                    html = ''

            return html

        except ItemNotFoundError:
            log.warning(
                u"Missing about section %s in course %s",
                section_key, course.location.to_deprecated_string()
            )
            return None

    raise KeyError("Invalid about key " + str(section_key))


def get_course_info_usage_key(course, section_key):
    """
    Returns the usage key for the specified section's course info module.
    """
    return course.id.make_usage_key('course_info', section_key)


def get_course_info_section_module(request, user, course, section_key):
    """
    This returns the course info module for a given section_key.

    Valid keys:
    - handouts
    - guest_handouts
    - updates
    - guest_updates
    """
    usage_key = get_course_info_usage_key(course, section_key)

    # Use an empty cache
    field_data_cache = FieldDataCache([], course.id, user)

    return get_module(
        user,
        request,
        usage_key,
        field_data_cache,
        log_if_not_found=False,
        wrap_xmodule_display=False,
        static_asset_path=course.static_asset_path,
        course=course
    )


def get_course_info_section(request, user, course, section_key):
    """
    This returns the snippet of html to be rendered on the course info page,
    given the key for the section.

    Valid keys:
    - handouts
    - guest_handouts
    - updates
    - guest_updates
    """
    info_module = get_course_info_section_module(request, user, course, section_key)

    html = ''
    if info_module is not None:
        try:
            html = info_module.render(STUDENT_VIEW).content.strip()
        except Exception:  # pylint: disable=broad-except
            html = render_to_string('courseware/error-message.html', None)
            log.exception(
                u"Error rendering course_id=%s, section_key=%s",
                unicode(course.id), section_key
            )

    return html


def get_course_date_blocks(course, user):
    """
    Return the list of blocks to display on the course info page,
    sorted by date.
    """
    block_classes = (
        CertificateAvailableDate,
        CourseEndDate,
        CourseStartDate,
        TodaysDate,
        VerificationDeadlineDate,
        VerifiedUpgradeDeadlineDate,
    )

    blocks = (cls(course, user) for cls in block_classes)

    def block_key_fn(block):
        """
        If the block's date is None, return the maximum datetime in order
        to force it to the end of the list of displayed blocks.
        """
        if block.date is None:
            return datetime.max.replace(tzinfo=pytz.UTC)
        return block.date
    return sorted((b for b in blocks if b.is_enabled), key=block_key_fn)


# TODO: Fix this such that these are pulled in as extra course-specific tabs.
#       arjun will address this by the end of October if no one does so prior to
#       then.
def get_course_syllabus_section(course, section_key):
    """
    This returns the snippet of html to be rendered on the syllabus page,
    given the key for the section.

    Valid keys:
    - syllabus
    - guest_syllabus
    """

    # Many of these are stored as html files instead of some semantic
    # markup. This can change without effecting this interface when we find a
    # good format for defining so many snippets of text/html.

    if section_key in ['syllabus', 'guest_syllabus']:
        try:
            filesys = course.system.resources_fs
            # first look for a run-specific version
            dirs = [path("syllabus") / course.url_name, path("syllabus")]
            filepath = find_file(filesys, dirs, section_key + ".html")
            with filesys.open(filepath) as html_file:
                return replace_static_urls(
                    html_file.read().decode('utf-8'),
                    getattr(course, 'data_dir', None),
                    course_id=course.id,
                    static_asset_path=course.static_asset_path,
                )
        except ResourceNotFound:
            log.exception(
                u"Missing syllabus section %s in course %s",
                section_key, text_type(course.location)
            )
            return "! Syllabus missing !"

    raise KeyError("Invalid about key " + str(section_key))


def get_courses(user, org=None, filter_=None):
    """
    Returns a list of courses available, sorted by course.number and optionally
    filtered by org code (case-insensitive).
    """
    start_time = time.time()
    is_api = False

    if filter_:
        is_api = filter_.get('is_api', False)

    log.debug('get_courses time check1 [%s]' % (time.time() - start_time))
    courses = branding.get_visible_courses(org=org, filter_=filter_)

    log.debug('get_courses time check2 [%s]' % (time.time() - start_time))

    permission_name = configuration_helpers.get_value(
        'COURSE_CATALOG_VISIBILITY_PERMISSION',
        settings.COURSE_CATALOG_VISIBILITY_PERMISSION
    )

    if is_api:
        log.debug('get_courses time check2-1 [%s]' % (time.time() - start_time))
        pass
    else:
        log.debug('get_courses time check2-2 [%s]' % (time.time() - start_time))
        courses = [c for c in courses if has_access(user, permission_name, c)]

    log.debug('get_courses time check3 [%s]' % (time.time() - start_time))

    return courses


def get_permission_for_course_about():
    """
    Returns the CourseOverview object for the course after checking for access.
    """
    return configuration_helpers.get_value(
        'COURSE_ABOUT_VISIBILITY_PERMISSION',
        settings.COURSE_ABOUT_VISIBILITY_PERMISSION
    )


def sort_by_announcement(courses):
    """
    Sorts a list of courses by their announcement date. If the date is
    not available, sort them by their start date.
    """

    # Sort courses by how far are they from they start day
    key = lambda course: course.sorting_score
    courses = sorted(courses, key=key)

    return courses


def sort_by_start_date(courses):
    """
    Returns a list of courses sorted by their start date, latest first.
    """
    courses = sorted(
        courses,
        key=lambda course: (course.has_ended(), course.start is None, course.start),
        reverse=False
    )

    return courses


def get_cms_course_link(course, page='course'):
    """
    Returns a link to course_index for editing the course in cms,
    assuming that the course is actually cms-backed.
    """
    # This is fragile, but unfortunately the problem is that within the LMS we
    # can't use the reverse calls from the CMS
    return u"//{}/{}/{}".format(settings.CMS_BASE, page, unicode(course.id))


def get_cms_block_link(block, page):
    """
    Returns a link to block_index for editing the course in cms,
    assuming that the block is actually cms-backed.
    """
    # This is fragile, but unfortunately the problem is that within the LMS we
    # can't use the reverse calls from the CMS
    return u"//{}/{}/{}".format(settings.CMS_BASE, page, block.location)


def get_studio_url(course, page):
    """
    Get the Studio URL of the page that is passed in.

    Args:
        course (CourseDescriptor)
    """
    studio_link = None
    if course.course_edit_method == "Studio":
        studio_link = get_cms_course_link(course, page)
    return studio_link


def get_problems_in_section(section):
    """
    This returns a dict having problems in a section.
    Returning dict has problem location as keys and problem
    descriptor as values.
    """

    problem_descriptors = defaultdict()
    if not isinstance(section, UsageKey):
        section_key = UsageKey.from_string(section)
    else:
        section_key = section
    # it will be a Mongo performance boost, if you pass in a depth=3 argument here
    # as it will optimize round trips to the database to fetch all children for the current node
    section_descriptor = modulestore().get_item(section_key, depth=3)

    # iterate over section, sub-section, vertical
    for subsection in section_descriptor.get_children():
        for vertical in subsection.get_children():
            for component in vertical.get_children():
                if component.location.block_type == 'problem' and getattr(component, 'has_score', False):
                    problem_descriptors[unicode(component.location)] = component

    return problem_descriptors


def get_current_child(xmodule, min_depth=None, requested_child=None):
    """
    Get the xmodule.position's display item of an xmodule that has a position and
    children.  If xmodule has no position or is out of bounds, return the first
    child with children of min_depth.

    For example, if chapter_one has no position set, with two child sections,
    section-A having no children and section-B having a discussion unit,
    `get_current_child(chapter, min_depth=1)`  will return section-B.

    Returns None only if there are no children at all.
    """
    # TODO: convert this method to use the Course Blocks API
    def _get_child(children):
        """
        Returns either the first or last child based on the value of
        the requested_child parameter.  If requested_child is None,
        returns the first child.
        """
        if requested_child == 'first':
            return children[0]
        elif requested_child == 'last':
            return children[-1]
        else:
            return children[0]

    def _get_default_child_module(child_modules):
        """Returns the first child of xmodule, subject to min_depth."""
        if min_depth <= 0:
            return _get_child(child_modules)
        else:
            content_children = [
                child for child in child_modules
                if child.has_children_at_depth(min_depth - 1) and child.get_display_items()
            ]
            return _get_child(content_children) if content_children else None

    child = None
    if hasattr(xmodule, 'position'):
        children = xmodule.get_display_items()
        if len(children) > 0:
            if xmodule.position is not None and not requested_child:
                pos = xmodule.position - 1  # position is 1-indexed
                if 0 <= pos < len(children):
                    child = children[pos]
                    if min_depth > 0 and not child.has_children_at_depth(min_depth - 1):
                        child = None
            if child is None:
                child = _get_default_child_module(children)

    return child


def get_course_chapter_ids(course_key):
    """
    Extracts the chapter block keys from a course structure.

    Arguments:
        course_key (CourseLocator): The course key
    Returns:
        list (string): The list of string representations of the chapter block keys in the course.
    """
    try:
        chapter_keys = modulestore().get_course(course_key).children
    except Exception:  # pylint: disable=broad-except
        log.exception('Failed to retrieve course from modulestore.')
        return []
    return [unicode(chapter_key) for chapter_key in chapter_keys if chapter_key.block_type == 'chapter']
