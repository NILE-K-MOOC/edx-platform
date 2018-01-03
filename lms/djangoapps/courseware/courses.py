# -*- coding: utf-8 -*-
"""
Functions for accessing and displaying courses within the
courseware.
"""
from datetime import datetime
from collections import defaultdict
from fs.errors import ResourceNotFoundError
import logging
from path import Path as path
import pytz
from django.http import Http404
from django.conf import settings
from edxmako.shortcuts import render_to_string
from xmodule.modulestore.django import modulestore
from xmodule.modulestore.exceptions import ItemNotFoundError
from static_replace import replace_static_urls
from xmodule.modulestore import ModuleStoreEnum
from xmodule.x_module import STUDENT_VIEW
<<<<<<< HEAD
=======

>>>>>>> origin
from courseware.access import has_access
from courseware.date_summary import (
    CourseEndDate,
    CourseStartDate,
    TodaysDate,
    VerificationDeadlineDate,
    VerifiedUpgradeDeadlineDate,
)
from courseware.model_data import FieldDataCache
from courseware.module_render import get_module
from lms.djangoapps.courseware.courseware_access_exception import CoursewareAccessException
from student.models import CourseEnrollment
import branding
from opaque_keys.edx.keys import UsageKey
from openedx.core.djangoapps.content.course_overviews.models import CourseOverview
from openedx.core.djangoapps.site_configuration import helpers as configuration_helpers
<<<<<<< HEAD
from django.utils.timezone import UTC
=======

>>>>>>> origin

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
        raise Http404("Course not found.")


class UserNotEnrolled(Http404):
    def __init__(self, course_key):
        super(UserNotEnrolled, self).__init__()
        self.course_key = course_key


def get_course_with_access(user, action, course_key, depth=0, check_if_enrolled=False):
    """
    Given a course_key, look up the corresponding course descriptor,
    check that the user has the access to perform the specified action
    on the course, and return the descriptor.

    Raises a 404 if the course_key is invalid, or the user doesn't have access.

    depth: The number of levels of children for the modulestore to cache. None means infinite depth

    check_if_enrolled: If true, additionally verifies that the user is either enrolled in the course
      or has staff access.
    """
    course = get_course_by_id(course_key, depth)
    check_course_access(course, user, action, check_if_enrolled)
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


def check_course_access(course, user, action, check_if_enrolled=False):
    """
    Check that the user has the access to perform the specified action
    on the course (CourseDescriptor|CourseOverview).

    check_if_enrolled: If true, additionally verifies that the user is either
    enrolled in the course or has staff access.
    """
    access_response = has_access(user, action, course, course.id)

    if not access_response:
        # Deliberately return a non-specific error message to avoid
        # leaking info about access control settings
        raise CoursewareAccessException(access_response)

    if check_if_enrolled:
        # Verify that the user is either enrolled in the course or a staff
        # member.  If user is not enrolled, raise UserNotEnrolled exception
        # that will be caught by middleware.
        if not ((user.id and CourseEnrollment.is_enrolled(user, course.id)) or has_access(user, 'staff', course)):
            raise UserNotEnrolled(course.id)


def find_file(filesystem, dirs, filename):
    """
    Looks for a filename in a list of dirs on a filesystem, in the specified order.

    filesystem: an OSFS filesystem
    dirs: a list of path objects
    filename: a string

    Returns d / filename if found in dir d, else raises ResourceNotFoundError.
    """
    for directory in dirs:
        filepath = path(directory) / filename
        if filesystem.exists(filepath):
            return filepath
    raise ResourceNotFoundError(u"Could not find {0}".format(filename))


def get_course_about_section(request, course, section_key):
    """
    This returns the snippet of html to be rendered on the course about page,
    given the key for the section.

    Valid keys:
    - overview
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
        'ocw_links'
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
                except Exception:  # pylint: disable=broad-except
                    html = render_to_string('courseware/error-message.html', None)
                    log.exception(
                        u"Error rendering course=%s, section_key=%s",
                        course, section_key
                    )

            if section_key == "effort":
                if course_week:
                    if html.strip().find('#'):
                        html = html.strip().split('#')[0]
                    else:
                        html = html.strip()[6:] + '주'
                elif course_video:
                    if html.strip().find('#'):
                        html = html.strip().split('#')[1].split(':')[0] + '시간 ' + html.strip().split('#')[1].split(':')[1] + '분'
                    else:
                        html = ''

                else:
                    html = html.strip()[:5]

                    if ':' in html:
                        html = html.split(':')[0] + '시간 ' + html.split(':')[1] + '분'
                    else:
                        html += '시간'

            return html

        except ItemNotFoundError:
            log.warning(
                u"Missing about section %s in course %s",
                section_key, course.location.to_deprecated_string()
            )
            return None

    raise KeyError("Invalid about key " + str(section_key))


def get_course_info_section_module(request, user, course, section_key):
    """
    This returns the course info module for a given section_key.

    Valid keys:
    - handouts
    - guest_handouts
    - updates
    - guest_updates
    """
    usage_key = course.id.make_usage_key('course_info', section_key)

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
            html = info_module.render(STUDENT_VIEW).content
        except Exception:  # pylint: disable=broad-except
            html = render_to_string('courseware/error-message.html', None)
            log.exception(
                u"Error rendering course_id=%s, section_key=%s",
                unicode(course.id), section_key
            )

    return html


def get_course_date_summary(course, user):
    """
    Return the snippet of HTML to be included on the course info page
    in the 'Date Summary' section.
    """
    blocks = _get_course_date_summary_blocks(course, user)
    return '\n'.join(
        b.render() for b in blocks
    )


def _get_course_date_summary_blocks(course, user):
    """
    Return the list of blocks to display on the course info page,
    sorted by date.
    """
    block_classes = (
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
        except ResourceNotFoundError:
            log.exception(
                u"Missing syllabus section %s in course %s",
                section_key, course.location.to_deprecated_string()
            )
            return "! Syllabus missing !"

    raise KeyError("Invalid about key " + str(section_key))


# def add_course_status(courses):
#
#     print 'add_course_status start'
#     print 'len(courses):', len(courses)
#
#     for c in courses:
#         print c.id, c.name, c.start, c.end, c.enrollment_start, c.enrollment_end
#
#     print 'add_course_status end'


def get_courses(user, org=None, filter_=None):
    """
    Returns a list of courses available, sorted by course.number and optionally
    filtered by org code (case-insensitive).
    """
    courses = branding.get_visible_courses(org=org, filter_=filter_)

    permission_name = configuration_helpers.get_value(
        'COURSE_CATALOG_VISIBILITY_PERMISSION',
        settings.COURSE_CATALOG_VISIBILITY_PERMISSION
    )

    courses = [c for c in courses if has_access(user, permission_name, c)]

    return courses


def get_courses_by_org(user, org=None, filter_=None):
    '''
    Returns a list of courses available, sorted by course.number
    '''

    print user, org, filter

    courses = branding.get_visible_courses(org=org, filter_=filter_)

    # print 'len ::::::::::', len(courses)

    courses1 = list()
    courses2 = list()

    for c in courses:
        # print 'course.keys1:', c.__dict__.keys()
        # print 'c.has_ended()', c.has_ended()
        # print 'c.number', c.number
        # print 'c.start', c.start
        # print 'c.id', c.id


        if c.start is not None and c.end is not None and c.start > c.end:
            continue

        if str(c.id).find('2015') > 0:
            continue

        # if c.enrollment_end is not None and c.has_ended() and c.enrollment_end < datetime.now(UTC()):
        #     continue

        if not c.has_ended():
            courses1.append(c)
        else:
            courses2.append(c)

    # courses1 = sorted(courses1, key=lambda course: course.number)
    # courses2 = sorted(courses2, key=lambda course: course.number)
    courses1 = sorted(courses1, key=lambda course: course.start, reverse=True)
    courses2 = sorted(courses2, key=lambda course: course.start, reverse=True)

    courses = courses1 + courses2

    permission_name = configuration_helpers.get_value(
        'COURSE_CATALOG_VISIBILITY_PERMISSION',
        settings.COURSE_CATALOG_VISIBILITY_PERMISSION
    )

    courses = [c for c in courses if has_access(user, permission_name, c)]

    # courses = sorted(courses, key=lambda course: course.number)

    return courses


def get_courses_by_org2(user, org=None, filter_=None):
    '''
    Returns a list of courses available, sorted by course.number
    '''

    print user, org, filter

    courses_temp = branding.get_visible_courses(org=org, filter_=filter_)

    courses = list()
    courses1 = list()
    courses2 = list()

    for c in courses_temp:
        cid = str(c.id)

        print 'get_courses_by_org2.step1: ', cid

        if c.start is not None and c.end is not None and c.start > c.end:
            continue

        if cid.find('2015') > 0:
            continue

        if org == 'KOCWk' and (c.enrollment_start is not None and datetime.now(UTC()) >= c.enrollment_start and c.id is not None and 'KOCW' in cid):
            courses.append(c)
        elif org == 'ACEk' and ('ACE' in cid or 'FA.HGU01' in cid):
            courses.append(c)
        elif org == 'CKk' and 'CK' in cid:
            courses.append(c)
        elif org == 'COREk' and ('SKKU_COS2021.01K' in cid or 'SKKU_COS2022.01K' in cid or 'SKKU_NTST100.01K' in cid or 'HYUKMOOC2016-4k' in cid or 'HYUKMOOC2016-5k' in cid):
            courses.append(c)

    for c in courses:
        print 'get_courses_by_org2.step2: ', c.id

        if not c.has_ended():
            courses1.append(c)
        else:
            courses2.append(c)

    courses1 = sorted(courses1, key=lambda course: course.start, reverse=True)
    courses2 = sorted(courses2, key=lambda course: course.start, reverse=True)

    courses = courses1 + courses2

    permission_name = configuration_helpers.get_value(
        'COURSE_CATALOG_VISIBILITY_PERMISSION',
        settings.COURSE_CATALOG_VISIBILITY_PERMISSION
    )

    courses = [c for c in courses if has_access(user, permission_name, c)]

    return courses


def get_courses_by_kocw(user, domain=None):
    '''
    Returns a list of courses available, sorted by course.number
    '''
    courses_temp = branding.get_visible_courses()
    courses = list()
    courses1 = list()
    courses2 = list()
    # for c in courses_temp:
    #     print 'wiki_slug ##############################', c.wiki_slug
    #     if c.enrollment_start is not None and datetime.now(UTC()) >= c.enrollment_start and c.wiki_slug is not None and 'KOCW' in c.wiki_slug:
    #         courses.append(c)

    for c in courses_temp:
        # print 'id ##############################', c.id, type(c.id)

        if c.start is not None and c.end is not None and c.start > c.end:
            continue

        if str(c.id).find('2015') > 0:
            continue

        # if c.enrollment_end is not None and c.has_ended() and c.enrollment_end < datetime.now(UTC()):
        #     continue

        if c.enrollment_start is not None and datetime.now(UTC()) >= c.enrollment_start and c.id is not None and 'KOCW' in str(c.id):
            courses.append(c)

    for c in courses:
        # print 'course.keys1:', c.__dict__.keys()
        # print 'c.has_ended()', c.has_ended()
        # print 'c.number', c.number
        # print 'c.start', c.start

        if not c.has_ended():
            courses1.append(c)
        else:
            courses2.append(c)

    # courses1 = sorted(courses1, key=lambda course: course.number)
    # courses2 = sorted(courses2, key=lambda course: course.number)

    courses1 = sorted(courses1, key=lambda course: course.start, reverse=True)
    courses2 = sorted(courses2, key=lambda course: course.start, reverse=True)

    courses = courses1 + courses2

    permission_name = configuration_helpers.get_value(
        'COURSE_CATALOG_VISIBILITY_PERMISSION',
        settings.COURSE_CATALOG_VISIBILITY_PERMISSION
    )

    courses = [c for c in courses if has_access(user, permission_name, c)]

    # courses = sorted(courses, key=lambda course: course.number)

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
                if component.location.category == 'problem' and getattr(component, 'has_score', False):
                    problem_descriptors[unicode(component.location)] = component

    return problem_descriptors
