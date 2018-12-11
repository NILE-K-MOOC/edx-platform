"""
EdX Branding package.

Provides a way to retrieve "branded" parts of the site.

This module provides functions to retrieve basic branded parts
such as the site visible courses, university name and logo.
"""

from django.conf import settings

from opaque_keys.edx.keys import CourseKey
from openedx.core.djangoapps.site_configuration import helpers as configuration_helpers
from datetime import datetime
from pytz import UTC
from django.db import connections

def get_visible_courses(org=None, filter_=None):
    """
    Return the set of CourseOverviews that should be visible in this branded
    instance.

    Arguments:
        org (string): Optional parameter that allows case-insensitive
            filtering by organization.
        filter_ (dict): Optional parameter that allows custom filtering by
            fields on the course.
    """
    # Import is placed here to avoid model import at project startup.
    from openedx.core.djangoapps.content.course_overviews.models import CourseOverview

    courses = []
    current_site_orgs = configuration_helpers.get_current_site_orgs()

    if org and current_site_orgs:
        print 'DEBUG ----------------1'
        # Check the current site's orgs to make sure the org's courses should be displayed
        if not current_site_orgs or org in current_site_orgs:
            courses = CourseOverview.get_all_courses(orgs=[org], filter_=filter_)
    elif current_site_orgs:
        print 'DEBUG ----------------2'
        # Only display courses that should be displayed on this site
        courses = CourseOverview.get_all_courses(orgs=current_site_orgs, filter_=filter_)
    else:
        print 'DEBUG ----------------3'
        #courses = CourseOverview.get_all_courses(filter_=filter_)
        target_org = org or current_site_orgs
        courses = CourseOverview.get_all_courses(org=target_org, filter_=filter_)
    #courses = sorted(courses, key=lambda course: course.number)
    with connections['default'].cursor() as cur:
        query = """
            SELECT a.id, ifnull(classfy, ''), ifnull(b.audit_yn, 'N')
            FROM course_overviews_courseoverview a
            LEFT JOIN course_overview_addinfo b ON a.id = b.course_id
            WHERE catalog_visibility = 'both'
        """
        cur.execute(query)
        course_tup = cur.fetchall()
        cur.close()

    # catalog_visibility:Il-Hee, Maeng
    courses = [c for c in courses if c.catalog_visibility == 'both']

    # Add Course Status
    for c in courses:
        # print c.display_name, c.id, c.start, c.end, c.enrollment_start, c.enrollment_end
        for cour in course_tup:
            if str(c.id) == cour[0]:
                c.classfy = cour[1]
                try:
                    c.audit_yn = cour[2]
                except BaseException:
                    c.audit_yn = 'N'
        if c.start is None or c.start == '' or c.end is None or c.end == '':
            c.status = 'none'
        elif datetime.now(UTC) < c.start:
            c.status = 'ready'
        elif c.start <= datetime.now(UTC) <= c.end:
            c.status = 'ing'
        elif c.end < datetime.now(UTC):
            c.status = 'end'
        else:
            c.status = 'none'

        # print 'c.status = ', c.id, c.status

    # Filtering can stop here.
    if current_site_orgs:
        return courses

    # See if we have filtered course listings in this domain
    filtered_visible_ids = None

    # this is legacy format, which also handle dev case, which should not filter
    subdomain = configuration_helpers.get_value('subdomain', 'default')
    if hasattr(settings, 'COURSE_LISTINGS') and subdomain in settings.COURSE_LISTINGS and not settings.DEBUG:
        filtered_visible_ids = frozenset(
            [CourseKey.from_string(c) for c in settings.COURSE_LISTINGS[subdomain]]
        )

    if filtered_visible_ids:
        return [course for course in courses if course.id in filtered_visible_ids]
    else:
        # Filter out any courses based on current org, to avoid leaking these.
        orgs = configuration_helpers.get_all_orgs()
        return [course for course in courses if course.location.org not in orgs]


def get_university_for_request():
    """
    Return the university name specified for the domain, or None
    if no university was specified
    """
    return configuration_helpers.get_value('university')
