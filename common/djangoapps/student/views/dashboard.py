# -*- coding: utf-8 -*-
"""
Dashboard view and supporting methods
"""

import datetime
import logging
from collections import defaultdict

from completion.exceptions import UnavailableCompletionData
from completion.utilities import get_key_to_last_completed_course_block
from django.conf import settings
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.urls import reverse
from django.shortcuts import redirect
from django.utils.translation import ugettext as _
from django.views.decorators.csrf import ensure_csrf_cookie

from opaque_keys.edx.keys import CourseKey
from pytz import UTC
from six import text_type, iteritems

from django.db import connections
import track.views
from bulk_email.models import BulkEmailFlag, Optout  # pylint: disable=import-error
from course_modes.models import CourseMode
from courseware.access import has_access
from edxmako.shortcuts import render_to_response, render_to_string
from entitlements.models import CourseEntitlement
from lms.djangoapps.commerce.utils import EcommerceService  # pylint: disable=import-error
from lms.djangoapps.verify_student.services import IDVerificationService
from openedx.core.djangoapps import monitoring_utils
from openedx.core.djangoapps.catalog.utils import (
    get_programs,
    get_pseudo_session_for_entitlement,
    get_visible_sessions_for_entitlement
)
from openedx.core.djangoapps.credit.email_utils import get_credit_provider_display_names, make_providers_strings
from openedx.core.djangoapps.programs.models import ProgramsApiConfig
from openedx.core.djangoapps.programs.utils import ProgramDataExtender, ProgramProgressMeter
from openedx.core.djangoapps.site_configuration import helpers as configuration_helpers
from openedx.core.djangoapps.util.maintenance_banner import add_maintenance_banner
from openedx.core.djangoapps.waffle_utils import WaffleFlag, WaffleFlagNamespace
from openedx.core.djangolib.markup import HTML, Text
from openedx.features.enterprise_support.api import get_dashboard_consent_notification
from shoppingcart.api import order_history
from shoppingcart.models import CourseRegistrationCode, DonationConfiguration
from student.cookies import set_user_info_cookie
from student.helpers import cert_info, check_verify_status_by_course
from student.models import (
    CourseEnrollment,
    CourseEnrollmentAttribute,
    DashboardConfiguration,
    UserProfile
)
from util.milestones_helpers import get_pre_requisite_courses_not_completed
from xmodule.modulestore.django import modulestore

import json
import sys
import MySQLdb as mdb
from django.db import connections
from django.views.decorators.csrf import csrf_exempt
from django.http import HttpResponse
from django.http import JsonResponse

from pymongo import MongoClient
from bson import ObjectId

reload(sys)
sys.setdefaultencoding('utf-8')
log = logging.getLogger("edx.student")


def get_org_black_and_whitelist_for_site():
    """
    Returns the org blacklist and whitelist for the current site.

    Returns:
        (org_whitelist, org_blacklist): A tuple of lists of orgs that serve as
            either a blacklist or a whitelist of orgs for the current site. The
            whitelist takes precedence, and the blacklist is used if the
            whitelist is None.
    """
    # Default blacklist is empty.
    org_blacklist = None
    # Whitelist the orgs configured for the current site.  Each site outside
    # of edx.org has a list of orgs associated with its configuration.
    org_whitelist = configuration_helpers.get_current_site_orgs()

    if not org_whitelist:
        # If there is no whitelist, the blacklist will include all orgs that
        # have been configured for any other sites. This applies to edx.org,
        # where it is easier to blacklist all other orgs.
        org_blacklist = configuration_helpers.get_all_orgs()

    return org_whitelist, org_blacklist


def _get_recently_enrolled_courses(course_enrollments):
    """
    Given a list of enrollments, filter out all but recent enrollments.

    Args:
        course_enrollments (list[CourseEnrollment]): A list of course enrollments.

    Returns:
        list[CourseEnrollment]: A list of recent course enrollments.
    """
    seconds = DashboardConfiguration.current().recent_enrollment_time_delta
    time_delta = (datetime.datetime.now(UTC) - datetime.timedelta(seconds=seconds))
    return [
        enrollment for enrollment in course_enrollments
        # If the enrollment has no created date, we are explicitly excluding the course
        # from the list of recent enrollments.
        if enrollment.is_active and enrollment.created > time_delta
    ]


def _allow_donation(course_modes, course_id, enrollment):
    """
    Determines if the dashboard will request donations for the given course.

    Check if donations are configured for the platform, and if the current course is accepting donations.

    Args:
        course_modes (dict): Mapping of course ID's to course mode dictionaries.
        course_id (str): The unique identifier for the course.
        enrollment(CourseEnrollment): The enrollment object in which the user is enrolled

    Returns:
        True if the course is allowing donations.

    """
    if course_id not in course_modes:
        flat_unexpired_modes = {
            text_type(course_id): [mode for mode in modes]
            for course_id, modes in iteritems(course_modes)
        }
        flat_all_modes = {
            text_type(course_id): [mode.slug for mode in modes]
            for course_id, modes in iteritems(CourseMode.all_modes_for_courses([course_id]))
        }
        log.error(
            u'Can not find `%s` in course modes.`%s`. All modes: `%s`',
            course_id,
            flat_unexpired_modes,
            flat_all_modes
        )
    donations_enabled = configuration_helpers.get_value(
        'ENABLE_DONATIONS',
        DonationConfiguration.current().enabled
    )
    return (
            donations_enabled and
            enrollment.mode in course_modes[course_id] and
            course_modes[course_id][enrollment.mode].min_price == 0
    )


def _create_recent_enrollment_message(course_enrollments, course_modes):  # pylint: disable=invalid-name
    """
    Builds a recent course enrollment message.

    Constructs a new message template based on any recent course enrollments
    for the student.

    Args:
        course_enrollments (list[CourseEnrollment]): a list of course enrollments.
        course_modes (dict): Mapping of course ID's to course mode dictionaries.

    Returns:
        A string representing the HTML message output from the message template.
        None if there are no recently enrolled courses.

    """
    recently_enrolled_courses = _get_recently_enrolled_courses(course_enrollments)

    if recently_enrolled_courses:
        enrollments_count = len(recently_enrolled_courses)
        course_name_separator = ', '
        # If length of enrolled course 2, join names with 'and'
        if enrollments_count == 2:
            course_name_separator = _(' and ')

        course_names = course_name_separator.join(
            [enrollment.course_overview.display_name for enrollment in recently_enrolled_courses]
        )

        allow_donations = any(
            _allow_donation(course_modes, enrollment.course_overview.id, enrollment)
            for enrollment in recently_enrolled_courses
        )

        platform_name = configuration_helpers.get_value('platform_name', settings.PLATFORM_NAME)

        return render_to_string(
            'enrollment/course_enrollment_message.html',
            {
                'course_names': course_names,
                'enrollments_count': enrollments_count,
                'allow_donations': allow_donations,
                'platform_name': platform_name,
                'course_id': recently_enrolled_courses[0].course_overview.id if enrollments_count == 1 else None
            }
        )


def get_course_enrollments(user, org_to_include, orgs_to_exclude, status=None, multisiteStatus=None):
    """
    Given a user, return a filtered set of his or her course enrollments.

    Arguments:
        user (User): the user in question.
        org_to_include (str): If not None, ONLY courses of this org will be returned.
        orgs_to_exclude (list[str]): If org_to_include is not None, this
            argument is ignored. Else, courses of this org will be excluded.

    Returns:
        generator[CourseEnrollment]: a sequence of enrollments to be displayed
        on the user's dashboard.
    """
    if not status:
        if multisiteStatus == True:
            enrollments = CourseEnrollment.enrollments_for_user_multi(user)
        else:
            enrollments = CourseEnrollment.enrollments_for_user_ing(user)


    elif status == 'end':
        enrollments = CourseEnrollment.enrollments_for_user_end(user)
    elif status == 'audit':
        enrollments = CourseEnrollment.enrollments_for_user_audit(user)
    elif status == 'interest':
        enrollments = CourseEnrollment.enrollments_for_user_interest(user)
    elif status == 'propose':
        enrollments = CourseEnrollment.enrollments_for_user_propose(user)
    else:
        enrollments = CourseEnrollment.enrollments_for_user_ing(user)

    if status == 'propose':
        for enrollment in enrollments:
            yield enrollment
    else:
        for enrollment in enrollments:
            enrollment.is_enrolled = CourseEnrollment.is_enrolled(user, enrollment.course_id)
            # If the course is missing or broken, log an error and skip it.
            course_overview = enrollment.course_overview
            if not course_overview:
                log.error(
                    "User %s enrolled in broken or non-existent course %s",
                    user.username,
                    enrollment.course_id
                )
                continue
            else:
                pass

            # Filter out anything that is not attributed to the current ORG.
            if org_to_include and course_overview.location.org != org_to_include:
                continue

            # Conversely, filter out any enrollments with courses attributed to current ORG.
            elif course_overview.location.org in orgs_to_exclude:
                continue

            # Else, include the enrollment.
            else:
                yield enrollment


def get_filtered_course_entitlements(user, org_whitelist, org_blacklist):
    """
    Given a user, return a filtered set of his or her course entitlements.

    Arguments:
        user (User): the user in question.
        org_whitelist (list[str]): If not None, ONLY entitlements of these orgs will be returned.
        org_blacklist (list[str]): CourseEntitlements of these orgs will be excluded.

    Returns:
        generator[CourseEntitlement]: a sequence of entitlements to be displayed
        on the user's dashboard.
    """
    course_entitlement_available_sessions = {}
    unfulfilled_entitlement_pseudo_sessions = {}
    course_entitlements = list(CourseEntitlement.get_active_entitlements_for_user(user))
    filtered_entitlements = []
    pseudo_session = None
    course_run_key = None

    for course_entitlement in course_entitlements:
        course_entitlement.update_expired_at()
        available_runs = get_visible_sessions_for_entitlement(course_entitlement)

        if not course_entitlement.enrollment_course_run:
            # Unfulfilled entitlements need a mock session for metadata
            pseudo_session = get_pseudo_session_for_entitlement(course_entitlement)
            unfulfilled_entitlement_pseudo_sessions[str(course_entitlement.uuid)] = pseudo_session

        # Check the org of the Course and filter out entitlements that are not available.
        if course_entitlement.enrollment_course_run:
            course_run_key = course_entitlement.enrollment_course_run.course_id
        elif available_runs:
            course_run_key = CourseKey.from_string(available_runs[0]['key'])
        elif pseudo_session:
            course_run_key = CourseKey.from_string(pseudo_session['key'])

        if course_run_key:
            # If there is no course_run_key at this point we will be unable to determine if it should be shown.
            # Therefore it should be excluded by default.
            if org_whitelist and course_run_key.org not in org_whitelist:
                continue
            elif org_blacklist and course_run_key.org in org_blacklist:
                continue

            course_entitlement_available_sessions[str(course_entitlement.uuid)] = available_runs
            filtered_entitlements.append(course_entitlement)

    return filtered_entitlements, course_entitlement_available_sessions, unfulfilled_entitlement_pseudo_sessions


def complete_course_mode_info(course_id, enrollment, modes=None):
    """
    We would like to compute some more information from the given course modes
    and the user's current enrollment

    Returns the given information:
        - whether to show the course upsell information
        - numbers of days until they can't upsell anymore
    """
    if modes is None:
        modes = CourseMode.modes_for_course_dict(course_id)

    mode_info = {'show_upsell': False, 'days_for_upsell': None}
    # we want to know if the user is already enrolled as verified or credit and
    # if verified is an option.
    if CourseMode.VERIFIED in modes and enrollment.mode in CourseMode.UPSELL_TO_VERIFIED_MODES:
        mode_info['show_upsell'] = True
        mode_info['verified_sku'] = modes['verified'].sku
        mode_info['verified_bulk_sku'] = modes['verified'].bulk_sku
        # if there is an expiration date, find out how long from now it is
        if modes['verified'].expiration_datetime:
            today = datetime.datetime.now(UTC).date()
            mode_info['days_for_upsell'] = (modes['verified'].expiration_datetime.date() - today).days

    return mode_info


def is_course_blocked(request, redeemed_registration_codes, course_key):
    """
    Checking if registration is blocked or not.
    """
    blocked = False
    for redeemed_registration in redeemed_registration_codes:
        # registration codes may be generated via Bulk Purchase Scenario
        # we have to check only for the invoice generated registration codes
        # that their invoice is valid or not
        if redeemed_registration.invoice_item:
            if not redeemed_registration.invoice_item.invoice.is_valid:
                blocked = True
                # disabling email notifications for unpaid registration courses
                Optout.objects.get_or_create(user=request.user, course_id=course_key)
                log.info(
                    u"User %s (%s) opted out of receiving emails from course %s",
                    request.user.username,
                    request.user.email,
                    course_key,
                )
                track.views.server_track(
                    request,
                    "change-email1-settings",
                    {"receive_emails": "no", "course": text_type(course_key)},
                    page='dashboard',
                )
                break

    return blocked


def get_verification_error_reasons_for_display(verification_error_codes):
    """
    Returns the display text for the given verification error codes.
    """
    verification_errors = []
    verification_error_map = {
        'photos_mismatched': _('Photos are mismatched'),
        'id_image_missing_name': _('Name missing from ID photo'),
        'id_image_missing': _('ID photo not provided'),
        'id_invalid': _('ID is invalid'),
        'user_image_not_clear': _('Learner photo is blurry'),
        'name_mismatch': _('Name on ID does not match name on account'),
        'user_image_missing': _('Learner photo not provided'),
        'id_image_not_clear': _('ID photo is blurry'),
    }

    for error in verification_error_codes:
        error_text = verification_error_map.get(error)
        if error_text:
            verification_errors.append(error_text)

    return verification_errors


def reverification_info(statuses):
    """
    Returns reverification-related information for *all* of user's enrollments whose
    reverification status is in statuses.

    Args:
        statuses (list): a list of reverification statuses we want information for
            example: ["must_reverify", "denied"]

    Returns:
        dictionary of lists: dictionary with one key per status, e.g.
            dict["must_reverify"] = []
            dict["must_reverify"] = [some information]
    """
    reverifications = defaultdict(list)

    # Sort the data by the reverification_end_date
    for status in statuses:
        if reverifications[status]:
            reverifications[status].sort(key=lambda x: x.date)
    return reverifications


def _credit_statuses(user, course_enrollments):
    """
    Retrieve the status for credit courses.

    A credit course is a course for which a user can purchased
    college credit.  The current flow is:

    1. User becomes eligible for credit (submits verifications, passes the course, etc.)
    2. User purchases credit from a particular credit provider.
    3. User requests credit from the provider, usually creating an account on the provider's site.
    4. The credit provider notifies us whether the user's request for credit has been accepted or rejected.

    The dashboard is responsible for communicating the user's state in this flow.

    Arguments:
        user (User): The currently logged-in user.
        course_enrollments (list[CourseEnrollment]): List of enrollments for the
            user.

    Returns: dict

    The returned dictionary has keys that are `CourseKey`s and values that
    are dictionaries with:

        * eligible (bool): True if the user is eligible for credit in this course.
        * deadline (datetime): The deadline for purchasing and requesting credit for this course.
        * purchased (bool): Whether the user has purchased credit for this course.
        * provider_name (string): The display name of the credit provider.
        * provider_status_url (string): A URL the user can visit to check on their credit request status.
        * request_status (string): Either "pending", "approved", or "rejected"
        * error (bool): If true, an unexpected error occurred when retrieving the credit status,
            so the user should contact the support team.

    Example:
    >>> _credit_statuses(user, course_enrollments)
    {
        CourseKey.from_string("edX/DemoX/Demo_Course"): {
            "course_key": "edX/DemoX/Demo_Course",
            "eligible": True,
            "deadline": 2015-11-23 00:00:00 UTC,
            "purchased": True,
            "provider_name": "Hogwarts",
            "provider_status_url": "http://example.com/status",
            "request_status": "pending",
            "error": False
        }
    }

    """
    from openedx.core.djangoapps.credit import api as credit_api

    # Feature flag off
    if not settings.FEATURES.get("ENABLE_CREDIT_ELIGIBILITY"):
        return {}

    request_status_by_course = {
        request["course_key"]: request["status"]
        for request in credit_api.get_credit_requests_for_user(user.username)
    }

    credit_enrollments = {
        enrollment.course_id: enrollment
        for enrollment in course_enrollments
        if enrollment.mode == "credit"
    }

    # When a user purchases credit in a course, the user's enrollment
    # mode is set to "credit" and an enrollment attribute is set
    # with the ID of the credit provider.  We retrieve *all* such attributes
    # here to minimize the number of database queries.
    purchased_credit_providers = {
        attribute.enrollment.course_id: attribute.value
        for attribute in CourseEnrollmentAttribute.objects.filter(
        namespace="credit",
        name="provider_id",
        enrollment__in=credit_enrollments.values()
    ).select_related("enrollment")
    }

    provider_info_by_id = {
        provider["id"]: provider
        for provider in credit_api.get_credit_providers()
    }

    statuses = {}
    for eligibility in credit_api.get_eligibilities_for_user(user.username):
        course_key = CourseKey.from_string(text_type(eligibility["course_key"]))
        providers_names = get_credit_provider_display_names(course_key)
        status = {
            "course_key": text_type(course_key),
            "eligible": True,
            "deadline": eligibility["deadline"],
            "purchased": course_key in credit_enrollments,
            "provider_name": make_providers_strings(providers_names),
            "provider_status_url": None,
            "provider_id": None,
            "request_status": request_status_by_course.get(course_key),
            "error": False,
        }

        # If the user has purchased credit, then include information about the credit
        # provider from which the user purchased credit.
        # We retrieve the provider's ID from the an "enrollment attribute" set on the user's
        # enrollment when the user's order for credit is fulfilled by the E-Commerce service.
        if status["purchased"]:
            provider_id = purchased_credit_providers.get(course_key)
            if provider_id is None:
                status["error"] = True
                log.error(
                    u"Could not find credit provider associated with credit enrollment "
                    u"for user %s in course %s.  The user will not be able to see his or her "
                    u"credit request status on the student dashboard.  This attribute should "
                    u"have been set when the user purchased credit in the course.",
                    user.id, course_key
                )
            else:
                provider_info = provider_info_by_id.get(provider_id, {})
                status["provider_name"] = provider_info.get("display_name")
                status["provider_status_url"] = provider_info.get("status_url")
                status["provider_id"] = provider_id

        statuses[course_key] = status

    return statuses


def _get_urls_for_resume_buttons(user, enrollments):
    '''
    Checks whether a user has made progress in any of a list of enrollments.
    '''
    resume_button_urls = []
    for enrollment in enrollments:
        try:
            block_key = get_key_to_last_completed_course_block(user, enrollment.course_id)
            url_to_block = reverse(
                'jump_to',
                kwargs={'course_id': enrollment.course_id, 'location': block_key}
            )
        except UnavailableCompletionData:
            url_to_block = ''
        resume_button_urls.append(url_to_block)
    return resume_button_urls


@login_required
@ensure_csrf_cookie
@add_maintenance_banner
def student_dashboard(request):
    """
    Provides the LMS dashboard view

    TODO: This is lms specific and does not belong in common code.

    Arguments:
        request: The request object.

    Returns:
        The dashboard response.

    """
    user = request.user
    if not UserProfile.objects.filter(user=user).exists():
        return redirect(reverse('account_settings'))

    platform_name = configuration_helpers.get_value("platform_name", settings.PLATFORM_NAME)

    enable_verified_certificates = configuration_helpers.get_value(
        'ENABLE_VERIFIED_CERTIFICATES',
        settings.FEATURES.get('ENABLE_VERIFIED_CERTIFICATES')
    )
    display_course_modes_on_dashboard = configuration_helpers.get_value(
        'DISPLAY_COURSE_MODES_ON_DASHBOARD',
        settings.FEATURES.get('DISPLAY_COURSE_MODES_ON_DASHBOARD', True)
    )
    activation_email_support_link = configuration_helpers.get_value(
        'ACTIVATION_EMAIL_SUPPORT_LINK', settings.ACTIVATION_EMAIL_SUPPORT_LINK
    ) or settings.SUPPORT_SITE_LINK
    hide_dashboard_courses_until_activated = configuration_helpers.get_value(
        'HIDE_DASHBOARD_COURSES_UNTIL_ACTIVATED',
        settings.FEATURES.get('HIDE_DASHBOARD_COURSES_UNTIL_ACTIVATED', False)
    )
    empty_dashboard_message = configuration_helpers.get_value(
        'EMPTY_DASHBOARD_MESSAGE', None
    )

    # Get the org whitelist or the org blacklist for the current site
    site_org_whitelist, site_org_blacklist = get_org_black_and_whitelist_for_site()
    course_enrollments = list(get_course_enrollments(user, site_org_whitelist, site_org_blacklist))

    # Get the entitlements for the user and a mapping to all available sessions for that entitlement
    # If an entitlement has no available sessions, pass through a mock course overview object
    (course_entitlements,
     course_entitlement_available_sessions,
     unfulfilled_entitlement_pseudo_sessions) = get_filtered_course_entitlements(
        user,
        site_org_whitelist,
        site_org_blacklist
    )
    course_org_filter = configuration_helpers.get_value('course_org_filter')

    # Let's filter out any courses in an "org" that has been declared to be
    # in a configuration
    org_filter_out_set = configuration_helpers.get_all_orgs()

    # remove our current org from the "filter out" list, if applicable
    if course_org_filter:
        org_filter_out_set.remove(course_org_filter)
    # Record how many courses there are so that we can get a better
    # understanding of usage patterns on prod.
    monitoring_utils.accumulate('num_courses', len(course_enrollments))

    # Sort the enrollment pairs by the enrollment date
    # course_enrollments.sort(key=lambda x: x.created, reverse=True)

    if 'status' in request.session:
        multisiteStatus = True
        status = None
    else:
        multisiteStatus = False
        status = None

    print "multisiteStatus = ", multisiteStatus

    # 개강예정, 진행중, 종료 로 구분하여 대시보드 로딩 속도를 개선한다.

    status = request.GET.get('status')
    if status:
        course_enrollments = list(get_course_enrollments(user, course_org_filter, org_filter_out_set, status))
    else:
        print "this is fucking logic"
        course_enrollments = list(get_course_enrollments(user, course_org_filter, org_filter_out_set, status, multisiteStatus))

    # Retrieve the course modes for each course
    enrolled_course_ids = [enrollment.course_id for enrollment in course_enrollments]
    __, unexpired_course_modes = CourseMode.all_and_unexpired_modes_for_courses(enrolled_course_ids)
    course_modes_by_course = {
        course_id: {
            mode.slug: mode
            for mode in modes
        }
        for course_id, modes in iteritems(unexpired_course_modes)
    }

    # Check to see if the student has recently enrolled in a course.
    # If so, display a notification message confirming the enrollment.
    enrollment_message = _create_recent_enrollment_message(
        course_enrollments, course_modes_by_course
    )
    course_optouts = Optout.objects.filter(user=user).values_list('course_id', flat=True)

    course_type1 = []
    course_type2 = []
    course_type3 = []
    course_type4 = []

    # 수정필요. https://github.com/kmoocdev2/edx-platform/commit/8da64778a4c8e758c5a9b012624c39846f100084#diff-55b798ee23a7fde8d1103408afcd0f16

    for c in course_enrollments:
        # 이수증 생성 여부: c.course.has_any_active_web_certificate

        print c.course.id, c.course.display_name, c.course.has_any_active_web_certificate

        if c.course.start and c.course.end and c.course.start > c.course.end:
            continue

        elif c.course.start and c.course.start > datetime.datetime.now(UTC):
            c.status = 'ready'
            course_type1.append(c)

        elif c.course.start and c.course.end and c.course.start <= datetime.datetime.now(
                UTC) <= c.course.end and datetime.datetime.now(UTC) <= c.course.enrollment_end:
            c.status = 'ing'
            course_type2.append(c)

        elif c.course.start and c.course.end and c.course.start <= datetime.datetime.now(
                UTC) <= c.course.end and datetime.datetime.now(UTC) >= c.course.enrollment_end:
            c.status = 'ing'
            course_type2.append(c)

        elif c.course.has_ended():
            c.status = 'end'
            course_type3.append(c)

        else:
            c.status = 'none'
            course_type4.append(c)

    course_type1.sort(key=lambda x: x.created, reverse=True)
    course_type2.sort(key=lambda x: x.created, reverse=True)
    # course_type3.sort(key=lambda x: x.created, reverse=True)
    # course_type4.sort(key=lambda x: x.created, reverse=True)

    '''
    print 'course 1:'
    print course_type1
    print 'course 2:'
    print course_type2
    print 'course 3:'
    print course_type3
    print 'course 4:'
    print course_type4
    '''

    course_enrollments = course_type1 + course_type2 + course_type3 + course_type4

    '''
    print 'check step 1 s'
    for c in course_enrollments:
        print c.course.id, c.course.display_name
    print 'check step 1 e'
    '''

    # Display activation message
    activate_account_message = ''

    print 'is_active', user.is_active
    # message = ""
    # if not user.is_active:
    #     message = render_to_string(
    #         'registration/activate_account_notice.html',
    #         {'email': user.email, 'platform_name': platform_name}
    #     )
    if not user.is_active:

        activate_account_message = Text(_(
            "Check your {email_start}{email}{email_end} inbox for an account activation link from {platform_name}. "
            "If you need help, contact {link_start}{platform_name} Support{link_end}."
        )).format(
            platform_name=platform_name,
            email_start=HTML("<strong>"),
            email_end=HTML("</strong>"),
            email=user.email,
            link_start=HTML("<a target='_blank' href='{activation_email_support_link}'>").format(
                activation_email_support_link=activation_email_support_link,
            ),
            link_end=HTML("</a>"),
        )

        if 'private_info_use_yn' in request.session and 'event_join_yn' in request.session:

            private_info_use_yn = request.session['private_info_use_yn']
            event_join_yn = request.session['event_join_yn']
            org_value = request.session['org_value']
            if private_info_use_yn =='Y':
                private_info_use_yn =1
            else:
                private_info_use_yn =0

            if event_join_yn =='Y':
                event_join_yn = 1
            else:
                event_join_yn = 0

            if request.session['org_value'] ==None:
                org_value =''
            else :
                pass


            try:

                # with connections['default'].cursor() as cur:
                #     query = """
                #         INSERT
                #           INTO registration_flag_history(user_id, private_info_use_yn, event_join_yn)
                #         VALUES ('{user_id}', '{private_info_use_yn}', '{event_join_yn}');
                #     """.format(
                #         user_id=user.id,
                #         private_info_use_yn=private_info_use_yn,
                #         event_join_yn=event_join_yn
                #     )
                with connections['default'].cursor() as cur:
                    query = """
                        INSERT
                          INTO tb_auth_user_addinfo(user_id, private_info_use_yn, event_join_yn,org_id)
                        VALUES ('{user_id}', '{private_info_use_yn}', '{event_join_yn}','{org_id}');
                    """.format(
                        user_id=user.id,
                        private_info_use_yn=private_info_use_yn,
                        event_join_yn=event_join_yn,
                        org_id=org_value
                    )

                    print 'query:', query
                    cur.execute(query)

                del request.session['private_info_use_yn']
                del request.session['event_join_yn']
                del request.session['org_value']

            except Exception as e:
                print 'registration_flag_history error.'
                print e

    enterprise_message = get_dashboard_consent_notification(request, user, course_enrollments)

    # Disable lookup of Enterprise consent_required_course due to ENT-727
    # Will re-enable after fixing WL-1315
    consent_required_courses = set()
    enterprise_customer_name = None

    # Account activation message
    account_activation_messages = [
        message for message in messages.get_messages(request) if 'account-activation' in message.tags
    ]

    # Global staff can see what courses encountered an error on their dashboard
    staff_access = False
    errored_courses = {}
    if has_access(user, 'staff', 'global'):
        # Show any courses that encountered an error on load
        staff_access = True
        errored_courses = modulestore().get_errored_courses()

    show_courseware_links_for = frozenset(
        enrollment.course_id for enrollment in course_enrollments
        if has_access(request.user, 'load', enrollment.course_overview)
    )

    # Find programs associated with course runs being displayed. This information
    # is passed in the template context to allow rendering of program-related
    # information on the dashboard.
    meter = ProgramProgressMeter(request.site, user, enrollments=course_enrollments)
    ecommerce_service = EcommerceService()
    inverted_programs = meter.invert_programs()

    urls, programs_data = {}, {}
    bundles_on_dashboard_flag = WaffleFlag(WaffleFlagNamespace(name=u'student.experiments'), u'bundles_on_dashboard')

    # TODO: Delete this code and the relevant HTML code after testing LEARNER-3072 is complete
    if bundles_on_dashboard_flag.is_enabled() and inverted_programs and inverted_programs.items():
        if len(course_enrollments) < 4:
            for program in inverted_programs.values():
                try:
                    program_uuid = program[0]['uuid']
                    program_data = get_programs(request.site, uuid=program_uuid)
                    program_data = ProgramDataExtender(program_data, request.user).extend()
                    skus = program_data.get('skus')
                    checkout_page_url = ecommerce_service.get_checkout_page_url(*skus)
                    program_data['completeProgramURL'] = checkout_page_url + '&bundle=' + program_data.get('uuid')
                    programs_data[program_uuid] = program_data
                except:  # pylint: disable=bare-except
                    pass

    # Construct a dictionary of course mode information
    # used to render the course list.  We re-use the course modes dict
    # we loaded earlier to avoid hitting the database.
    course_mode_info = {
        enrollment.course_id: complete_course_mode_info(
            enrollment.course_id, enrollment,
            modes=course_modes_by_course[enrollment.course_id]
        )
        for enrollment in course_enrollments
    }

    # Determine the per-course verification status
    # This is a dictionary in which the keys are course locators
    # and the values are one of:
    #
    # VERIFY_STATUS_NEED_TO_VERIFY
    # VERIFY_STATUS_SUBMITTED
    # VERIFY_STATUS_APPROVED
    # VERIFY_STATUS_MISSED_DEADLINE
    #
    # Each of which correspond to a particular message to display
    # next to the course on the dashboard.
    #
    # If a course is not included in this dictionary,
    # there is no verification messaging to display.
    verify_status_by_course = check_verify_status_by_course(user, course_enrollments)
    cert_statuses = {
        enrollment.course_id: cert_info(request.user, enrollment.course_overview)
        for enrollment in course_enrollments
    }

    # only show email settings for Mongo course and when bulk email is turned on
    show_email_settings_for = frozenset(
        enrollment.course_id for enrollment in course_enrollments if (
            BulkEmailFlag.feature_enabled(enrollment.course_id)
        )
    )

    # Verification Attempts
    # Used to generate the "you must reverify for course x" banner
    verification_status = IDVerificationService.user_status(user)
    verification_errors = get_verification_error_reasons_for_display(verification_status['error'])

    # Gets data for midcourse reverifications, if any are necessary or have failed
    statuses = ["approved", "denied", "pending", "must_reverify"]
    reverifications = reverification_info(statuses)

    block_courses = frozenset(
        enrollment.course_id for enrollment in course_enrollments
        if is_course_blocked(
            request,
            CourseRegistrationCode.objects.filter(
                course_id=enrollment.course_id,
                registrationcoderedemption__redeemed_by=request.user
            ),
            enrollment.course_id
        )
    )

    enrolled_courses_either_paid = frozenset(
        enrollment.course_id for enrollment in course_enrollments
        if enrollment.is_paid_course()
    )

    # If there are *any* denied reverifications that have not been toggled off,
    # we'll display the banner
    denied_banner = any(item.display for item in reverifications["denied"])

    # Populate the Order History for the side-bar.
    order_history_list = order_history(
        user,
        course_org_filter=site_org_whitelist,
        org_filter_out_set=site_org_blacklist
    )

    # get list of courses having pre-requisites yet to be completed
    courses_having_prerequisites = frozenset(
        enrollment.course_id for enrollment in course_enrollments
        if enrollment.course_overview.pre_requisite_courses
    )
    courses_requirements_not_met = get_pre_requisite_courses_not_completed(user, courses_having_prerequisites)

    if 'notlive' in request.GET:
        redirect_message = _("The course you are looking for does not start until {date}.").format(
            date=request.GET['notlive']
        )
    elif 'course_closed' in request.GET:
        redirect_message = _("The course you are looking for is closed for enrollment as of {date}.").format(
            date=request.GET['course_closed']
        )
    else:
        redirect_message = ''

    valid_verification_statuses = ['approved', 'must_reverify', 'pending', 'expired']
    display_sidebar_on_dashboard = (len(order_history_list) or
                                    (verification_status['status'] in valid_verification_statuses and
                                     verification_status['should_display']))

    # Filter out any course enrollment course cards that are associated with fulfilled entitlements
    for entitlement in [e for e in course_entitlements if e.enrollment_course_run is not None]:
        course_enrollments = [
            enr for enr in course_enrollments if entitlement.enrollment_course_run.course_id != enr.course_id
        ]


    sys.setdefaultencoding('utf-8')
    con = mdb.connect(settings.DATABASES.get('default').get('HOST'),
                      settings.DATABASES.get('default').get('USER'),
                      settings.DATABASES.get('default').get('PASSWORD'),
                      settings.DATABASES.get('default').get('NAME'),
                      charset='utf8')
    for c in course_enrollments:
        cur = con.cursor()
        query = """
                SELECT DATE_FORMAT(max(modified), "최근 접속일: `%y.%m.%d."), course_id
                  FROM courseware_studentmodule
                 WHERE student_id = '{0}' AND course_id = '{1}';
            """.format(user.id, c.course.id)
        cur.execute(query)
        final_day = cur.fetchall()

        cur.close()

        info_dict = dashboard_course_addinfo(c.course_overview)
        c.teacher_name = info_dict['teacher_name']
        c.course_level = info_dict['course_level']
        c.classfy = info_dict['classfy']
        c.middle_classfy = info_dict['middle_classfy']
        c.course_date = info_dict['course_date']
        c.week = info_dict['week']
        c.final_day = final_day[0][0]

    con.close()


    context = {
        'urls': urls,
        'programs_data': programs_data,
        'enterprise_message': enterprise_message,
        'consent_required_courses': consent_required_courses,
        'enterprise_customer_name': enterprise_customer_name,
        'enrollment_message': enrollment_message,
        'redirect_message': redirect_message,
        'account_activation_messages': account_activation_messages,
        'activate_account_message': activate_account_message,
        'course_enrollments': course_enrollments,
        'course_entitlements': course_entitlements,
        'course_entitlement_available_sessions': course_entitlement_available_sessions,
        'unfulfilled_entitlement_pseudo_sessions': unfulfilled_entitlement_pseudo_sessions,
        'course_optouts': course_optouts,
        'staff_access': staff_access,
        'errored_courses': errored_courses,
        'show_courseware_links_for': show_courseware_links_for,
        'all_course_modes': course_mode_info,
        'cert_statuses': cert_statuses,
        'credit_statuses': _credit_statuses(user, course_enrollments),
        'show_email_settings_for': show_email_settings_for,
        'reverifications': reverifications,
        'verification_display': verification_status['should_display'],
        'verification_status': verification_status['status'],
        'verification_status_by_course': verify_status_by_course,
        'verification_errors': verification_errors,
        'block_courses': block_courses,
        'denied_banner': denied_banner,
        'billing_email': settings.PAYMENT_SUPPORT_EMAIL,
        'user': user,
        'logout_url': reverse('logout'),
        'platform_name': platform_name,
        'enrolled_courses_either_paid': enrolled_courses_either_paid,
        'provider_states': [],
        'order_history_list': order_history_list,
        'courses_requirements_not_met': courses_requirements_not_met,
        'nav_hidden': True,
        'inverted_programs': inverted_programs,
        'show_program_listing': ProgramsApiConfig.is_enabled(),
        'show_dashboard_tabs': True,
        'disable_courseware_js': True,
        'display_course_modes_on_dashboard': enable_verified_certificates and display_course_modes_on_dashboard,
        'display_sidebar_on_dashboard': display_sidebar_on_dashboard,
        'display_sidebar_account_activation_message': not (user.is_active or hide_dashboard_courses_until_activated),
        'display_dashboard_courses': (user.is_active or not hide_dashboard_courses_until_activated),
        'empty_dashboard_message': empty_dashboard_message,
        'status_flag': status,
    }

    if ecommerce_service.is_enabled(request.user):
        context.update({
            'use_ecommerce_payment_flow': True,
            'ecommerce_payment_page': ecommerce_service.payment_page_url(),
        })

    # Gather urls for course card resume buttons.
    resume_button_urls = _get_urls_for_resume_buttons(user, course_enrollments)
    # There must be enough urls for dashboard.html. Template creates course
    # cards for "enrollments + entitlements".
    resume_button_urls += ['' for entitlement in course_entitlements]
    context.update({
        'resume_button_urls': resume_button_urls
    })

    response = render_to_response('dashboard.html', context)
    set_user_info_cookie(response, request)
    # if request.is_ajax():
    #     print "dashboard_ajax-----------ok"
    #     return render_to_response('dashboard_ajax.html', context)



    return response


# addinfo 테이블 데이터
def dashboard_course_addinfo(course_overview):
    with connections['default'].cursor() as cur:
        query = '''
            SELECT course_id,
                   ifnull(teacher_name, ''),
                   ifnull(course_level, 'Not applicable'),
                   b.classfy,
                   c.middle_classfy
              FROM course_overview_addinfo a
                   LEFT JOIN (SELECT detail_code, detail_ename classfy
                                FROM code_detail
                               WHERE group_code = '001') b
                      ON a.classfy = b.detail_code
                   LEFT JOIN (SELECT detail_code, detail_ename middle_classfy
                                FROM code_detail
                               WHERE group_code = '002') c
                      ON a.middle_classfy = c.detail_code
             WHERE course_id = '{course_id}';
                '''.format(course_id=course_overview.id)
        cur.execute(query)
        addinfo_data = cur.fetchone()

        info_dict = dict()
        info_dict['course_id'] = addinfo_data[0]

        if addinfo_data[1].find(',') != -1:
            teacher_len = len(addinfo_data[1].split(','))
            info_dict['teacher_name'] = [addinfo_data[1].split(',')[0].strip(), teacher_len-1]
        else:
            info_dict['teacher_name'] = [addinfo_data[1].strip(), 0]

        info_dict['course_level'] = addinfo_data[2]
        info_dict['classfy'] = addinfo_data[3]
        info_dict['middle_classfy'] = addinfo_data[4]

        c_start = course_overview.start.strftime('`%y.%m.%d.')
        c_end = course_overview.end.strftime('`%y.%m.%d.') if course_overview.end else ''

        # 강좌운영기간
        info_dict['course_date'] = str(c_start) + ' ~ ' + str(c_end)

        # 주차
        effort = course_overview.effort if course_overview.effort else '0'

        if effort != '0' and effort.find('@') != -1 and effort.find('#') != -1:
            info_dict['week'] = effort.split('@')[1].split('#')[0]
        elif effort != '0' and effort.find('@') != -1 and effort.find('#') == -1:
            info_dict['week'] = effort.split('@')[1]
        else:
            info_dict['week'] = '0'

    return info_dict


@csrf_exempt
def modi_course_level(request):
    if request.method == 'POST':
        if request.POST['method'] == 'addinfo':
            print 'modi_course_level!!!!!!'
            addinfo_user_id = request.POST.get('addinfo_user_id')
            addinfo_course_id = request.POST.get('addinfo_course_id')
            course_level = request.POST.get('course_level')

            print 'modi_course_level index ========='
            print addinfo_user_id
            print addinfo_course_id
            print course_level
            print 'modi_course_level index ========='

            sys.setdefaultencoding('utf-8')
            con = mdb.connect(settings.DATABASES.get('default').get('HOST'),
                              settings.DATABASES.get('default').get('USER'),
                              settings.DATABASES.get('default').get('PASSWORD'),
                              settings.DATABASES.get('default').get('NAME'),
                              charset='utf8')
            cur = con.cursor()
            query = """
                    SELECT count(*)
                      FROM course_overview_addinfo
                     WHERE course_id = '{0}';
            """.format(addinfo_course_id)
            cur.execute(query)
            count = cur.fetchall()
            ctn = count[0][0]
            cur.close()

            if (ctn == 1):
                cur = con.cursor()
                query = """
                    UPDATE course_overview_addinfo
                       SET delete_yn = 'N', modify_id = '{0}', modify_date = now(), course_level = '{1}'
                     WHERE course_id = '{2}';
                """.format(addinfo_user_id, course_level, addinfo_course_id)
                cur.execute(query)
                cur.execute('commit')
                cur.close()
                data = json.dumps('success')
            elif (ctn == 0):
                cur = con.cursor()
                query = """
                        INSERT INTO course_overview_addinfo(course_id,
                                    create_type,
                                    create_year,
                                    course_no,
                                    course_level,
                                    delete_yn,
                                    regist_id,
                                    regist_date,
                                    modify_id,
                                    modify_date)
                              VALUES('{0}','001',YEAR(now()),'1','{1}','N','{2}',now(),'{3}',now());
                """.format(addinfo_course_id, course_level, addinfo_user_id, addinfo_user_id)
                cur.execute(query)
                cur.execute('commit')
                cur.close()
                data = json.dumps('success')
            return HttpResponse(data, 'application/json')
        return HttpResponse('success', 'application/json')


@csrf_exempt
def modi_teacher_name(request):
    if request.method == 'POST':
        if request.POST['method'] == 'addinfo':
            addinfo_user_id = request.POST.get('addinfo_user_id')
            addinfo_course_id = request.POST.get('addinfo_course_id')
            teacher_name = request.POST.get('teacher_name')

            with connections['default'].cursor() as cur:
                query = """
                        SELECT count(*)
                          FROM course_overview_addinfo
                         WHERE course_id = '{0}';
                """.format(addinfo_course_id)
                cur.execute(query)
                count = cur.fetchall()
                ctn = count[0][0]

            if ctn == 1:
                with connections['default'].cursor() as cur:
                    query = """
                        UPDATE course_overview_addinfo
                           SET delete_yn = 'N', modify_id = '{0}', modify_date = now(), teacher_name = '{1}'
                         WHERE course_id = '{2}';
                    """.format(addinfo_user_id, teacher_name, addinfo_course_id)
                    cur.execute(query)

            elif ctn == 0:
                with connections['default'].cursor() as cur:
                    query = """
                            INSERT INTO course_overview_addinfo(course_id,
                                        create_type,
                                        create_year,
                                        course_no,
                                        teacher_name,
                                        delete_yn,
                                        regist_id,
                                        regist_date,
                                        modify_id,
                                        modify_date
                                       )
                                  VALUES('{0}','001',YEAR(now()),'1','{1}','N','{2}',now(),'{3}',now());
                    """.format(addinfo_course_id, teacher_name, addinfo_user_id, addinfo_user_id)
                    cur.execute(query)


            # insert or update the teacher_name in mongodb:Il-Hee, Maeng
            # ------------------------------- add start ---------------------------------
            client = MongoClient(settings.CONTENTSTORE.get('DOC_STORE_CONFIG').get('host'),
                                 settings.CONTENTSTORE.get('DOC_STORE_CONFIG').get('port'))
            db = client.edxapp

            course_id = addinfo_course_id   # request.POST.get('addinfo_course_id')
            org = course_id.split('+')[0][10:]
            cid = course_id.split('+')[1]
            run = course_id.split('+')[2]

            cursor_active_versions = db.modulestore.active_versions.find_one({'course': cid, 'run': run, 'org': org})
            pb = cursor_active_versions.get('versions').get('published-branch')

            print "modi_teacher_name > pb = ", pb

            structures_data = db.modulestore.structures.find_one({'_id': ObjectId(pb)})

            blocks = structures_data.get('blocks')

            for block in blocks:
                if block['block_type'] == 'course':
                    block['fields']['teacher_name'] = teacher_name

            db.modulestore.structures.replace_one({'_id': ObjectId(pb)}, structures_data)
            # ------------------------------- add end ---------------------------------
            data = json.dumps('success')

            return HttpResponse(data, 'application/json')

        return HttpResponse('success', 'application/json')
