# -*- coding: utf-8 -*-
"""
Instructor Dashboard Views
"""

import datetime
import json
import logging
import uuid

import pytz
from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.core.urlresolvers import reverse
from django.http import Http404, HttpResponseServerError
from django.utils.html import escape
from django.utils.translation import ugettext as _, ugettext_noop
from django.views.decorators.cache import cache_control
from django.views.decorators.csrf import ensure_csrf_cookie
from django.views.decorators.http import require_POST
from mock import patch
from opaque_keys import InvalidKeyError
from opaque_keys.edx.keys import CourseKey
from opaque_keys.edx.locations import SlashSeparatedCourseKey
from xblock.fields import ScopeIds

from bulk_email.models import BulkEmailFlag
from certificates import api as certs_api
from certificates.models import (
    CertificateGenerationConfiguration,
    CertificateWhitelist,
    GeneratedCertificate,
    CertificateStatuses,
    CertificateGenerationHistory,
    CertificateInvalidation,
)
from class_dashboard.dashboard_data import get_section_display_name, get_array_section_has_problem
from course_modes.models import CourseMode, CourseModesArchive
from courseware.access import has_access
from courseware.courses import get_course_by_id, get_studio_url
from django_comment_client.utils import has_forum_access
from django_comment_common.models import FORUM_ROLE_ADMINISTRATOR
from edxmako.shortcuts import render_to_response
from lms.djangoapps.lms_xblock.runtime import quote_slashes
from openedx.core.djangoapps.course_groups.cohorts import get_course_cohorts, is_course_cohorted, DEFAULT_COHORT_NAME
from openedx.core.djangolib.markup import HTML, Text
from openedx.core.lib.xblock_utils import wrap_xblock
from shoppingcart.models import Coupon, PaidCourseRegistration, CourseRegCodeItem
from student.models import CourseEnrollment
from student.roles import CourseFinanceAdminRole, CourseSalesAdminRole
from util.date_utils import get_default_time_display
from util.json_request import JsonResponse
from xblock.field_data import DictFieldData
from xmodule.html_module import HtmlDescriptor
from xmodule.modulestore.django import modulestore
from xmodule.tabs import CourseTab
from .tools import get_units_with_due_date, title_or_url
# import add
from pymongo import MongoClient
import MySQLdb as mdb
import sys
from django.http import HttpResponse
# from django.utils import simplejson
import json as simplejson
import csv
from django.db import connections

log = logging.getLogger(__name__)


class InstructorDashboardTab(CourseTab):
    """
    Defines the Instructor Dashboard view type that is shown as a course tab.
    """

    type = "instructor"
    title = ugettext_noop('Instructor')
    view_name = "instructor_dashboard"
    is_dynamic = True  # The "Instructor" tab is instead dynamically added when it is enabled

    @classmethod
    def is_enabled(cls, course, user=None):
        """
        Returns true if the specified user has staff access.
        """
        return bool(user and has_access(user, 'staff', course, course.id))


@ensure_csrf_cookie
@cache_control(no_cache=True, no_store=True, must_revalidate=True)
def instructor_dashboard_2(request, course_id):
    """ Display the instructor dashboard for a course. """
    try:
        course_key = CourseKey.from_string(course_id)
    except InvalidKeyError:
        log.error(u"Unable to find course with course key %s while loading the Instructor Dashboard.", course_id)
        return HttpResponseServerError()

    course = get_course_by_id(course_key, depth=0)

    access = {
        'admin': request.user.is_staff,
        'instructor': bool(has_access(request.user, 'instructor', course)),
        'finance_admin': CourseFinanceAdminRole(course_key).has_user(request.user),
        'sales_admin': CourseSalesAdminRole(course_key).has_user(request.user),
        'staff': bool(has_access(request.user, 'staff', course)),
        'forum_admin': has_forum_access(request.user, course_key, FORUM_ROLE_ADMINISTRATOR),
    }

    if not access['staff']:
        raise Http404()

    is_white_label = CourseMode.is_white_label(course_key)

    sections = [
        _section_course_info(course, access),
        _section_membership(course, access, is_white_label),
        _section_cohort_management(course, access),
        _section_student_admin(course, access),
        _section_data_download(course, access),
    ]

    analytics_dashboard_message = None
    if settings.ANALYTICS_DASHBOARD_URL:
        # Construct a URL to the external analytics dashboard
        analytics_dashboard_url = '{0}/courses/{1}'.format(settings.ANALYTICS_DASHBOARD_URL, unicode(course_key))
        link_start = HTML("<a href=\"{}\" target=\"_blank\">").format(analytics_dashboard_url)
        analytics_dashboard_message = _(
            "To gain insights into student enrollment and participation {link_start}"
            "visit {analytics_dashboard_name}, our new course analytics product{link_end}."
        )
        analytics_dashboard_message = Text(analytics_dashboard_message).format(
            link_start=link_start, link_end=HTML("</a>"), analytics_dashboard_name=settings.ANALYTICS_DASHBOARD_NAME)

        # Temporarily show the "Analytics" section until we have a better way of linking to Insights
        sections.append(_section_analytics(course, access))

    # Check if there is corresponding entry in the CourseMode Table related to the Instructor Dashboard course
    course_mode_has_price = False
    paid_modes = CourseMode.paid_modes_for_course(course_key)
    if len(paid_modes) == 1:
        course_mode_has_price = True
    elif len(paid_modes) > 1:
        log.error(
            u"Course %s has %s course modes with payment options. Course must only have "
            u"one paid course mode to enable eCommerce options.",
            unicode(course_key), len(paid_modes)
        )

    if settings.FEATURES.get('INDIVIDUAL_DUE_DATES') and access['instructor']:
        sections.insert(3, _section_extensions(course))

    # Gate access to course email by feature flag & by course-specific authorization
    if BulkEmailFlag.feature_enabled(course_key):
        sections.append(_section_send_email(course, access))

    # Gate access to Metrics tab by featue flag and staff authorization
    if settings.FEATURES['CLASS_DASHBOARD'] and access['staff']:
        sections.append(_section_metrics(course, access))

    # Gate access to Ecommerce tab
    if course_mode_has_price and (access['finance_admin'] or access['sales_admin']):
        sections.append(_section_e_commerce(course, access, paid_modes[0], is_white_label, is_white_label))

    # Gate access to Special Exam tab depending if either timed exams or proctored exams
    # are enabled in the course

    # NOTE: For now, if we only have procotred exams enabled, then only platform Staff
    # (user.is_staff) will be able to view the special exams tab. This may
    # change in the future
    can_see_special_exams = (
        ((course.enable_proctored_exams and request.user.is_staff) or course.enable_timed_exams) and
        settings.FEATURES.get('ENABLE_SPECIAL_EXAMS', False)
    )
    if can_see_special_exams:
        sections.append(_section_special_exams(course, access))

    # Certificates panel
    # This is used to generate example certificates
    # and enable self-generated certificates for a course.
    certs_enabled = CertificateGenerationConfiguration.current().enabled
    if certs_enabled and access['admin']:
        sections.append(_section_certificates(course))

    disable_buttons = not _is_small_course(course_key)

    certificate_white_list = CertificateWhitelist.get_certificate_white_list(course_key)
    generate_certificate_exceptions_url = reverse(  # pylint: disable=invalid-name
        'generate_certificate_exceptions',
        kwargs={'course_id': unicode(course_key), 'generate_for': ''}
    )
    generate_bulk_certificate_exceptions_url = reverse(  # pylint: disable=invalid-name
        'generate_bulk_certificate_exceptions',
        kwargs={'course_id': unicode(course_key)}
    )
    certificate_exception_view_url = reverse(
        'certificate_exception_view',
        kwargs={'course_id': unicode(course_key)}
    )

    certificate_invalidation_view_url = reverse(  # pylint: disable=invalid-name
        'certificate_invalidation_view',
        kwargs={'course_id': unicode(course_key)}
    )

    certificate_invalidations = CertificateInvalidation.get_certificate_invalidations(course_key)

    context = {
        'course': course,
        'studio_url': get_studio_url(course, 'course'),
        'sections': sections,
        'disable_buttons': disable_buttons,
        'analytics_dashboard_message': analytics_dashboard_message,
        'certificate_white_list': certificate_white_list,
        'certificate_invalidations': certificate_invalidations,
        'generate_certificate_exceptions_url': generate_certificate_exceptions_url,
        'generate_bulk_certificate_exceptions_url': generate_bulk_certificate_exceptions_url,
        'certificate_exception_view_url': certificate_exception_view_url,
        'certificate_invalidation_view_url': certificate_invalidation_view_url,
        'is_assessment': check_assessment(course.wiki_slug),
        'is_assessment_ing': check_assessment_ing(course.id.course, course.id.run),
        'is_assessment_done': check_assessment_done(course.id.course, course.id.run),
    }

    return render_to_response('instructor/instructor_dashboard_2/instructor_dashboard_2.html', context)


## Section functions starting with _section return a dictionary of section data.

## The dictionary must include at least {
##     'section_key': 'circus_expo'
##     'section_display_name': 'Circus Expo'
## }

## section_key will be used as a css attribute, javascript tie-in, and template import filename.
## section_display_name will be used to generate link titles in the nav bar.


def _section_e_commerce(course, access, paid_mode, coupons_enabled, reports_enabled):
    """ Provide data for the corresponding dashboard section """
    course_key = course.id
    coupons = Coupon.objects.filter(course_id=course_key).order_by('-is_active')
    course_price = paid_mode.min_price

    total_amount = None
    if access['finance_admin']:
        single_purchase_total = PaidCourseRegistration.get_total_amount_of_purchased_item(course_key)
        bulk_purchase_total = CourseRegCodeItem.get_total_amount_of_purchased_item(course_key)
        total_amount = single_purchase_total + bulk_purchase_total

    section_data = {
        'section_key': 'e-commerce',
        'section_display_name': _('E-Commerce'),
        'access': access,
        'course_id': unicode(course_key),
        'currency_symbol': settings.PAID_COURSE_REGISTRATION_CURRENCY[1],
        'ajax_remove_coupon_url': reverse('remove_coupon', kwargs={'course_id': unicode(course_key)}),
        'ajax_get_coupon_info': reverse('get_coupon_info', kwargs={'course_id': unicode(course_key)}),
        'get_user_invoice_preference_url': reverse('get_user_invoice_preference', kwargs={'course_id': unicode(course_key)}),
        'sale_validation_url': reverse('sale_validation', kwargs={'course_id': unicode(course_key)}),
        'ajax_update_coupon': reverse('update_coupon', kwargs={'course_id': unicode(course_key)}),
        'ajax_add_coupon': reverse('add_coupon', kwargs={'course_id': unicode(course_key)}),
        'get_sale_records_url': reverse('get_sale_records', kwargs={'course_id': unicode(course_key)}),
        'get_sale_order_records_url': reverse('get_sale_order_records', kwargs={'course_id': unicode(course_key)}),
        'instructor_url': reverse('instructor_dashboard', kwargs={'course_id': unicode(course_key)}),
        'get_registration_code_csv_url': reverse('get_registration_codes', kwargs={'course_id': unicode(course_key)}),
        'generate_registration_code_csv_url': reverse('generate_registration_codes', kwargs={'course_id': unicode(course_key)}),
        'active_registration_code_csv_url': reverse('active_registration_codes', kwargs={'course_id': unicode(course_key)}),
        'spent_registration_code_csv_url': reverse('spent_registration_codes', kwargs={'course_id': unicode(course_key)}),
        'set_course_mode_url': reverse('set_course_mode_price', kwargs={'course_id': unicode(course_key)}),
        'download_coupon_codes_url': reverse('get_coupon_codes', kwargs={'course_id': unicode(course_key)}),
        'enrollment_report_url': reverse('get_enrollment_report', kwargs={'course_id': unicode(course_key)}),
        'exec_summary_report_url': reverse('get_exec_summary_report', kwargs={'course_id': unicode(course_key)}),
        'list_financial_report_downloads_url': reverse('list_financial_report_downloads',
                                                       kwargs={'course_id': unicode(course_key)}),
        'list_instructor_tasks_url': reverse('list_instructor_tasks', kwargs={'course_id': unicode(course_key)}),
        'look_up_registration_code': reverse('look_up_registration_code', kwargs={'course_id': unicode(course_key)}),
        'coupons': coupons,
        'sales_admin': access['sales_admin'],
        'coupons_enabled': coupons_enabled,
        'reports_enabled': reports_enabled,
        'course_price': course_price,
        'total_amount': total_amount
    }
    return section_data


def _section_special_exams(course, access):
    """ Provide data for the corresponding dashboard section """
    course_key = course.id

    section_data = {
        'section_key': 'special_exams',
        'section_display_name': _('Special Exams'),
        'access': access,
        'course_id': unicode(course_key)
    }
    return section_data


def _section_certificates(course):
    """Section information for the certificates panel.

    The certificates panel allows global staff to generate
    example certificates and enable self-generated certificates
    for a course.

    Arguments:
        course (Course)

    Returns:
        dict

    """
    example_cert_status = None
    html_cert_enabled = certs_api.has_html_certificates_enabled(course.id, course)
    if html_cert_enabled:
        can_enable_for_course = True
    else:
        example_cert_status = certs_api.example_certificates_status(course.id)

        # Allow the user to enable self-generated certificates for students
        # *only* once a set of example certificates has been successfully generated.
        # If certificates have been misconfigured for the course (for example, if
        # the PDF template hasn't been uploaded yet), then we don't want
        # to turn on self-generated certificates for students!
        can_enable_for_course = (
            example_cert_status is not None and
            all(
                cert_status['status'] == 'success'
                for cert_status in example_cert_status
            )
        )
    instructor_generation_enabled = settings.FEATURES.get('CERTIFICATES_INSTRUCTOR_GENERATION', False)
    certificate_statuses_with_count = {
        certificate['status']: certificate['count']
        for certificate in GeneratedCertificate.get_unique_statuses(course_key=course.id)
        }

    return {
        'section_key': 'certificates',
        'section_display_name': _('Certificates'),
        'example_certificate_status': example_cert_status,
        'can_enable_for_course': can_enable_for_course,
        'enabled_for_course': certs_api.cert_generation_enabled(course.id),
        'is_self_paced': course.self_paced,
        'instructor_generation_enabled': instructor_generation_enabled,
        'html_cert_enabled': html_cert_enabled,
        'active_certificate': certs_api.get_active_web_certificate(course),
        'certificate_statuses_with_count': certificate_statuses_with_count,
        'status': CertificateStatuses,
        'certificate_generation_history':
            CertificateGenerationHistory.objects.filter(course_id=course.id).order_by("-created"),
        'urls': {
            'generate_example_certificates': reverse(
                'generate_example_certificates',
                kwargs={'course_id': course.id}
            ),
            'enable_certificate_generation': reverse(
                'enable_certificate_generation',
                kwargs={'course_id': course.id}
            ),
            'start_certificate_generation': reverse(
                'start_certificate_generation',
                kwargs={'course_id': course.id}
            ),
            'start_certificate_regeneration': reverse(
                'start_certificate_regeneration',
                kwargs={'course_id': course.id}
            ),
            'list_instructor_tasks_url': reverse(
                'list_instructor_tasks',
                kwargs={'course_id': course.id}
            ),
        }
    }


@ensure_csrf_cookie
@cache_control(no_cache=True, no_store=True, must_revalidate=True)
@require_POST
@login_required
def set_course_mode_price(request, course_id):
    """
    set the new course price and add new entry in the CourseModesArchive Table
    """
    try:
        course_price = int(request.POST['course_price'])
    except ValueError:
        return JsonResponse(
            {'message': _("Please Enter the numeric value for the course price")},
            status=400)  # status code 400: Bad Request

    currency = request.POST['currency']
    course_key = SlashSeparatedCourseKey.from_deprecated_string(course_id)

    course_honor_mode = CourseMode.objects.filter(mode_slug='honor', course_id=course_key)
    if not course_honor_mode:
        return JsonResponse(
            {'message': _("CourseMode with the mode slug({mode_slug}) DoesNotExist").format(mode_slug='honor')},
            status=400)  # status code 400: Bad Request

    CourseModesArchive.objects.create(
        course_id=course_id, mode_slug='honor', mode_display_name='Honor Code Certificate',
        min_price=course_honor_mode[0].min_price, currency=course_honor_mode[0].currency,
        expiration_datetime=datetime.datetime.now(pytz.utc), expiration_date=datetime.date.today()
    )
    course_honor_mode.update(
        min_price=course_price,
        currency=currency
    )
    return JsonResponse({'message': _("CourseMode price updated successfully")})


def _section_course_info(course, access):
    """ Provide data for the corresponding dashboard section """
    course_key = course.id

    section_data = {
        'section_key': 'course_info',
        'section_display_name': _('Course Info'),
        'access': access,
        'course_id': course_key,
        'course_display_name': course.display_name,
        'has_started': course.has_started(),
        'has_ended': course.has_ended(),
        'start_date': get_default_time_display(course.start),
        'end_date': get_default_time_display(course.end) or _('No end date set'),
        'num_sections': len(course.children),
        'list_instructor_tasks_url': reverse('list_instructor_tasks', kwargs={'course_id': unicode(course_key)}),
    }

    if settings.FEATURES.get('DISPLAY_ANALYTICS_ENROLLMENTS'):
        section_data['enrollment_count'] = CourseEnrollment.objects.enrollment_counts(course_key)

    if settings.ANALYTICS_DASHBOARD_URL:
        #  dashboard_link is already made safe in _get_dashboard_link
        dashboard_link = _get_dashboard_link(course_key)
        #  so we can use Text() here so it's not double-escaped and rendering HTML on the front-end
        message = Text(_("Enrollment data is now available in {dashboard_link}.")).format(dashboard_link=dashboard_link)
        section_data['enrollment_message'] = message

    if settings.FEATURES.get('ENABLE_SYSADMIN_DASHBOARD'):
        section_data['detailed_gitlogs_url'] = reverse('gitlogs_detail', kwargs={'course_id': unicode(course_key)})

    try:
        sorted_cutoffs = sorted(course.grade_cutoffs.items(), key=lambda i: i[1], reverse=True)
        advance = lambda memo, (letter, score): "{}: {}, ".format(letter, score) + memo
        section_data['grade_cutoffs'] = reduce(advance, sorted_cutoffs, "")[:-2]
    except Exception:  # pylint: disable=broad-except
        section_data['grade_cutoffs'] = "Not Available"
    # section_data['offline_grades'] = offline_grades_available(course_key)

    try:
        section_data['course_errors'] = [(escape(a), '') for (a, _unused) in modulestore().get_course_errors(course.id)]
    except Exception:  # pylint: disable=broad-except
        section_data['course_errors'] = [('Error fetching errors', '')]

    return section_data


def _section_membership(course, access, is_white_label):
    """ Provide data for the corresponding dashboard section """
    course_key = course.id
    ccx_enabled = settings.FEATURES.get('CUSTOM_COURSES_EDX', False) and course.enable_ccx
    section_data = {
        'section_key': 'membership',
        'section_display_name': _('Membership'),
        'access': access,
        'ccx_is_enabled': ccx_enabled,
        'is_white_label': is_white_label,
        'enroll_button_url': reverse('students_update_enrollment', kwargs={'course_id': unicode(course_key)}),
        'unenroll_button_url': reverse('students_update_enrollment', kwargs={'course_id': unicode(course_key)}),
        'upload_student_csv_button_url': reverse('register_and_enroll_students', kwargs={'course_id': unicode(course_key)}),
        'modify_beta_testers_button_url': reverse('bulk_beta_modify_access', kwargs={'course_id': unicode(course_key)}),
        'list_course_role_members_url': reverse('list_course_role_members', kwargs={'course_id': unicode(course_key)}),
        'modify_access_url': reverse('modify_access', kwargs={'course_id': unicode(course_key)}),
        'list_forum_members_url': reverse('list_forum_members', kwargs={'course_id': unicode(course_key)}),
        'update_forum_role_membership_url': reverse('update_forum_role_membership', kwargs={'course_id': unicode(course_key)}),
    }
    return section_data


def _section_cohort_management(course, access):
    """ Provide data for the corresponding cohort management section """
    course_key = course.id
    section_data = {
        'section_key': 'cohort_management',
        'section_display_name': _('Cohorts'),
        'access': access,
        'course_cohort_settings_url': reverse(
            'course_cohort_settings',
            kwargs={'course_key_string': unicode(course_key)}
        ),
        'cohorts_url': reverse('cohorts', kwargs={'course_key_string': unicode(course_key)}),
        'upload_cohorts_csv_url': reverse('add_users_to_cohorts', kwargs={'course_id': unicode(course_key)}),
        'discussion_topics_url': reverse('cohort_discussion_topics', kwargs={'course_key_string': unicode(course_key)}),
        'verified_track_cohorting_url': reverse(
            'verified_track_cohorting', kwargs={'course_key_string': unicode(course_key)}
        ),
    }
    return section_data


def _is_small_course(course_key):
    """ Compares against MAX_ENROLLMENT_INSTR_BUTTONS to determine if course enrollment is considered small. """
    is_small_course = False
    enrollment_count = CourseEnrollment.objects.num_enrolled_in(course_key)
    max_enrollment_for_buttons = settings.FEATURES.get("MAX_ENROLLMENT_INSTR_BUTTONS")
    if max_enrollment_for_buttons is not None:
        is_small_course = enrollment_count <= max_enrollment_for_buttons
    return is_small_course


def _section_student_admin(course, access):
    """ Provide data for the corresponding dashboard section """
    course_key = course.id
    is_small_course = _is_small_course(course_key)

    section_data = {
        'section_key': 'student_admin',
        'section_display_name': _('Student Admin'),
        'access': access,
        'is_small_course': is_small_course,
        'get_student_progress_url_url': reverse('get_student_progress_url', kwargs={'course_id': unicode(course_key)}),
        'enrollment_url': reverse('students_update_enrollment', kwargs={'course_id': unicode(course_key)}),
        'reset_student_attempts_url': reverse('reset_student_attempts', kwargs={'course_id': unicode(course_key)}),
        'reset_student_attempts_for_entrance_exam_url': reverse(
            'reset_student_attempts_for_entrance_exam',
            kwargs={'course_id': unicode(course_key)},
        ),
        'rescore_problem_url': reverse('rescore_problem', kwargs={'course_id': unicode(course_key)}),
        'rescore_entrance_exam_url': reverse('rescore_entrance_exam', kwargs={'course_id': unicode(course_key)}),
        'student_can_skip_entrance_exam_url': reverse(
            'mark_student_can_skip_entrance_exam',
            kwargs={'course_id': unicode(course_key)},
        ),
        'list_instructor_tasks_url': reverse('list_instructor_tasks', kwargs={'course_id': unicode(course_key)}),
        'list_entrace_exam_instructor_tasks_url': reverse('list_entrance_exam_instructor_tasks',
                                                          kwargs={'course_id': unicode(course_key)}),
        'spoc_gradebook_url': reverse('spoc_gradebook', kwargs={'course_id': unicode(course_key)}),
    }
    return section_data


def _section_extensions(course):
    """ Provide data for the corresponding dashboard section """
    section_data = {
        'section_key': 'extensions',
        'section_display_name': _('Extensions'),
        'units_with_due_dates': [(title_or_url(unit), unicode(unit.location))
                                 for unit in get_units_with_due_date(course)],
        'change_due_date_url': reverse('change_due_date', kwargs={'course_id': unicode(course.id)}),
        'reset_due_date_url': reverse('reset_due_date', kwargs={'course_id': unicode(course.id)}),
        'show_unit_extensions_url': reverse('show_unit_extensions', kwargs={'course_id': unicode(course.id)}),
        'show_student_extensions_url': reverse('show_student_extensions', kwargs={'course_id': unicode(course.id)}),
    }
    return section_data


def _section_data_download(course, access):
    """ Provide data for the corresponding dashboard section """
    course_key = course.id

    show_proctored_report_button = (
        settings.FEATURES.get('ENABLE_SPECIAL_EXAMS', False) and
        course.enable_proctored_exams
    )

    section_data = {
        'section_key': 'data_download',
        'section_display_name': _('Data Download'),
        'access': access,
        'show_generate_proctored_exam_report_button': show_proctored_report_button,
        'get_problem_responses_url': reverse('get_problem_responses', kwargs={'course_id': unicode(course_key)}),
        'get_grading_config_url': reverse('get_grading_config', kwargs={'course_id': unicode(course_key)}),
        'get_students_features_url': reverse('get_students_features', kwargs={'course_id': unicode(course_key)}),
        'get_issued_certificates_url': reverse(
            'get_issued_certificates', kwargs={'course_id': unicode(course_key)}
        ),
        'get_students_who_may_enroll_url': reverse(
            'get_students_who_may_enroll', kwargs={'course_id': unicode(course_key)}
        ),
        'get_anon_ids_url': reverse('get_anon_ids', kwargs={'course_id': unicode(course_key)}),
        'get_contents_stat_url': reverse('get_contents_stat', kwargs={'course_id': unicode(course_key)}),
        'get_contents_view_url': reverse('get_contents_view', kwargs={'course_id': unicode(course_key)}),
        'list_proctored_results_url': reverse('get_proctored_exam_results', kwargs={'course_id': unicode(course_key)}),
        'list_instructor_tasks_url': reverse('list_instructor_tasks', kwargs={'course_id': unicode(course_key)}),
        'list_report_downloads_url': reverse('list_report_downloads', kwargs={'course_id': unicode(course_key)}),
        'calculate_grades_csv_url': reverse('calculate_grades_csv', kwargs={'course_id': unicode(course_key)}),
        'problem_grade_report_url': reverse('problem_grade_report', kwargs={'course_id': unicode(course_key)}),
        'course_has_survey': True if course.course_survey_name else False,
        'course_survey_results_url': reverse('get_course_survey_results', kwargs={'course_id': unicode(course_key)}),
        'export_ora2_data_url': reverse('export_ora2_data', kwargs={'course_id': unicode(course_key)}),
    }
    return section_data


def null_applicable_aside_types(block):  # pylint: disable=unused-argument
    """
    get_aside method for monkey-patching into applicable_aside_types
    while rendering an HtmlDescriptor for email text editing. This returns
    an empty list.
    """
    return []


def _section_send_email(course, access):
    """ Provide data for the corresponding bulk email section """
    course_key = course.id

    # Monkey-patch applicable_aside_types to return no asides for the duration of this render
    with patch.object(course.runtime, 'applicable_aside_types', null_applicable_aside_types):
        # This HtmlDescriptor is only being used to generate a nice text editor.
        html_module = HtmlDescriptor(
            course.system,
            DictFieldData({'data': ''}),
            ScopeIds(None, None, None, course_key.make_usage_key('html', 'fake'))
        )
        fragment = course.system.render(html_module, 'studio_view')
    fragment = wrap_xblock(
        'LmsRuntime', html_module, 'studio_view', fragment, None,
        extra_data={"course-id": unicode(course_key)},
        usage_id_serializer=lambda usage_id: quote_slashes(unicode(usage_id)),
        # Generate a new request_token here at random, because this module isn't connected to any other
        # xblock rendering.
        request_token=uuid.uuid1().get_hex()
    )
    cohorts = []
    if is_course_cohorted(course_key):
        cohorts = get_course_cohorts(course)
    email_editor = fragment.content
    section_data = {
        'section_key': 'send_email',
        'section_display_name': _('Email'),
        'access': access,
        'send_email': reverse('send_email', kwargs={'course_id': unicode(course_key)}),
        'editor': email_editor,
        'cohorts': cohorts,
        'default_cohort_name': DEFAULT_COHORT_NAME,
        'list_instructor_tasks_url': reverse(
            'list_instructor_tasks', kwargs={'course_id': unicode(course_key)}
        ),
        'email_background_tasks_url': reverse(
            'list_background_email_tasks', kwargs={'course_id': unicode(course_key)}
        ),
        'email_content_history_url': reverse(
            'list_email_content', kwargs={'course_id': unicode(course_key)}
        ),
    }
    return section_data


def _get_dashboard_link(course_key):
    """ Construct a URL to the external analytics dashboard """
    analytics_dashboard_url = '{0}/courses/{1}'.format(settings.ANALYTICS_DASHBOARD_URL, unicode(course_key))
    link = HTML(u"<a href=\"{0}\" target=\"_blank\">{1}</a>").format(
        analytics_dashboard_url, settings.ANALYTICS_DASHBOARD_NAME
    )
    return link


def _section_analytics(course, access):
    """ Provide data for the corresponding dashboard section """
    section_data = {
        'section_key': 'instructor_analytics',
        'section_display_name': _('Analytics'),
        'access': access,
        'course_id': unicode(course.id),
    }
    return section_data


def _section_metrics(course, access):
    """Provide data for the corresponding dashboard section """
    course_key = course.id
    section_data = {
        'section_key': 'metrics',
        'section_display_name': _('Metrics'),
        'access': access,
        'course_id': unicode(course_key),
        'sub_section_display_name': get_section_display_name(course_key),
        'section_has_problem': get_array_section_has_problem(course_key),
        'get_students_opened_subsection_url': reverse('get_students_opened_subsection'),
        'get_students_problem_grades_url': reverse('get_students_problem_grades'),
        'post_metrics_data_csv_url': reverse('post_metrics_data_csv'),
    }
    return section_data


# add copykiller
def check_assessment(active_versions_key):
    # print 'active_versions_key:',active_versions_key

    client = MongoClient(settings.CONTENTSTORE.get('DOC_STORE_CONFIG').get('host'), settings.CONTENTSTORE.get('DOC_STORE_CONFIG').get('port'))
    db = client.edxapp

    cursor = db.modulestore.active_versions.find({'search_targets.wiki_slug': active_versions_key})
    for document in cursor:
        assessmentId = document.get('versions').get('published-branch')
    cursor.close()

    cursor = db.modulestore.structures.find({'_id': assessmentId})
    for document in cursor:
        blocks = document.get('blocks')
        print blocks
    cursor.close()
    client.close()
    is_assessment = False
    for block in blocks:
        # print 'check_assessment 1:::', block.get('block_type') == 'openassessment'
        # print 'check_assessment 2:::', block.get('block_type') == 'edx_sga'

        if block.get('block_type') == 'openassessment' or block.get('block_type') == 'edx_sga':
            is_assessment = True

    return is_assessment


def check_assessment_ing(course_course, course_run):
    con = mdb.connect(settings.DATABASES.get('default').get('HOST'), settings.DATABASES.get('default').get('USER'), settings.DATABASES.get('default').get('PASSWORD'),
                      settings.DATABASES.get('default').get('NAME'))
    cur = con.cursor()
    query = """
        SELECT class_id
          FROM vw_copykiller
         WHERE term_id = '{course_run}' AND class_id = '{course_course}';
    """.format(course_run=course_run, course_course=course_course)

    print 'check_assessment_ing QUERY1: ', query

    query2 = """
        SELECT a.uri
          FROM vw_copykiller a
         WHERE     NOT EXISTS
                      (SELECT 1
                         FROM tb_copykiller_copyratio b
                        WHERE a.uri = b.uri AND complete_status != 'N')
               AND class_id = '{course_course}'
               AND term_id = '{course_run}';
    """.format(course_course=course_course, course_run=course_run)

    print 'check_assessment_ing QUERY2: ', query2

    query3 = """
       SELECT item_type
          FROM submissions_submission, submissions_studentitem a
         WHERE     student_item_id = a.id
               AND a.course_id LIKE '%{course_course}+{course_run}%'
               AND attempt_number = (SELECT max(attempt_number)
                                       FROM submissions_submission
                                      WHERE student_item_id = a.id)
               AND a.item_type = 'sga';
    """.format(course_course=course_course, course_run=course_run)

    query4 = """
        SELECT submission_uuid
          FROM assessment_peerworkflow a
               JOIN student_anonymoususerid b ON a.student_id = b.anonymous_user_id
               JOIN auth_user c ON b.user_id = c.id
         WHERE a.course_id LIKE '%{course_course}+{course_run}%'
               AND completed_at != FALSE;
    """.format(course_course=course_course, course_run=course_run)

    cur.execute(query)
    cur_rowcount = cur.rowcount
    cur.execute(query2)
    cur_rowcount2 = cur.rowcount
    cur.execute(query3)
    copy_cnt = cur.rowcount
    cur.execute(query4)
    copy_cnt += cur.rowcount
    cur.close()
    con.close()
    print copy_cnt
    print 'cur_rowcount :::  ', cur_rowcount, '     ----------    cur_rowcount2 ::: ', cur_rowcount2
    if (cur_rowcount > 0 and (copy_cnt == cur_rowcount)) or (cur_rowcount > 0 and cur_rowcount2 == 0):
        return True
    else:
        return False


def check_assessment_done(course_course, course_run):
    print 'check_assessment_done'
    with connections['default'].cursor() as cur:
        query = """
            SELECT count(uri)
              FROM vw_copykiller
             WHERE class_id = '{course_course}'
              AND term_id = '{course_run}';
        """.format(course_course=course_course, course_run=course_run)

        print 'check_assessment_done query : ', query
        cur.execute(query)
        result = cur.fetchone()
        if result[0] == 0:
            return False

        query2 = """
            SELECT if(count(DISTINCT a.uri) = count(DISTINCT b.uri)
                AND count(DISTINCT a.uri) != 0, 'True', 'False') complete
              FROM vw_copykiller a JOIN tb_copykiller_copyratio b ON a.uri = b.uri
             WHERE class_id = '{course_course}'
             AND term_id = '{course_run}';
        """.format(course_course=course_course, course_run=course_run)

        print 'check_assessment_done query2 :', query2

        cur.execute(query2)
        result = cur.fetchone()

    if result[0] == 'True':
        return True
    else:
        return False


def return_course(course_id):
    try:
        course_key = CourseKey.from_string(course_id)
    except InvalidKeyError:
        log.error(u"Unable to find course with course key %s while loading the Instructor Dashboard.", course_id)
        return HttpResponseServerError()

    course = get_course_by_id(course_key, depth=0)

    return course


def get_assessment_info(course):
    accessment_info = {}

    con = mdb.connect(settings.DATABASES.get('default').get('HOST'), settings.DATABASES.get('default').get('USER'), settings.DATABASES.get('default').get('PASSWORD'),
                      settings.DATABASES.get('default').get('NAME'))

    client = MongoClient(settings.CONTENTSTORE.get('DOC_STORE_CONFIG').get('host'), settings.CONTENTSTORE.get('DOC_STORE_CONFIG').get('port'))
    db = client.edxapp
    # org = str(course.wiki_slug).split('.')

    query = '''
        SELECT start, end FROM course_overviews_courseoverview WHERE id = '{course_id}';
    '''.format(course_id=course.id)

    print 'date query --------    ', course.display_name, '\n', course.id, '\n', query

    cur = con.cursor()
    cur.execute(query)
    course_date = cur.fetchone()

    start_course = datetime.datetime.strftime(course_date[0], '%Y-%m-%dT%H:%M:%S')
    end_course = datetime.datetime.strftime(course_date[1], '%Y-%m-%dT%H:%M:%S')

    cur.close()

    cursor = db.modulestore.active_versions.find({'search_targets.wiki_slug': course.wiki_slug})
    for document in cursor:
        published_branch = document.get('versions').get('published-branch')
    cursor.close()
    cursor = db.modulestore.structures.find_one({'_id': published_branch})

    dict1 = {}
    dict2 = {}

    # 1. 강좌 종료일 확인
    course_end = [block.get("fields")['end'] if 'end' in block.get("fields") else None for block in cursor.get("blocks") if block.get("block_type") == "course"][0]
    course_start = [block.get("fields")['start'] if 'start' in block.get("fields") else None for block in cursor.get("blocks") if block.get("block_type") == "course"][0]

    # 2. edx_sga, ora 확인
    ora_sga_list = [block.get("block_id") for block in cursor.get("blocks") if block.get("block_type") in ['edx_sga', 'openassessment']]
    print 'ora_sga_list:', ora_sga_list

    # * ora 의 경우 submission_start, submission_due 값이 존재 하므로 해당 값을 dict2 로 셋팅. 단, 강좌종료일 보다 앞서야함.
    for block in cursor.get("blocks"):
        if block.get("block_type") == "openassessment" and "submission_due" in block.get("fields"):
            submission_due = datetime.datetime.strptime(block.get("fields")["submission_due"][:19], "%Y-%m-%dT%H:%M:%S")
            submission_start = datetime.datetime.strptime(block.get("fields")["submission_start"][:19], "%Y-%m-%dT%H:%M:%S") if block.get('fields').has_key('submission_start') else course_start
            ora_display_name = block.get('fields')['display_name'] if block.get('fields').has_key('display_name') else 'No Title'
            dict2['submission_start'] = submission_start
            dict2['submission_due'] = submission_due if submission_due < course_end else course_end
            dict2['ora_display_name'] = ora_display_name

    # 3. vertical 에서 해당 xblock 을 포함하는지 확인
    for block_id in ora_sga_list:
        for block in cursor.get("blocks"):
            if block.get("block_type") == 'vertical':
                children = block.get("fields")["children"] if "children" in block.get("fields") else list()
                for child in children:
                    if block_id == child[1]:
                        dict1[block.get("block_id")] = block_id
                        break

    # 4. sequential 에서 vertical 을 포함하는지 확인
    for key, value in dict1.items():
        for block in cursor.get("blocks"):
            if block.get("block_type") == 'sequential':
                children = block.get("fields")["children"] if "children" in block.get("fields") else list()
                for child in children:
                    if key == child[1] and not dict2.has_key(dict1[key]):
                        dict2['start'] = start_course
                        dict2['due'] = block.get("fields")["due"] if "due" in block.get("fields") else end_course
                        sga_display_name = block.get('fields')['display_name'] if block.get('fields').has_key('display_name') or block.get('fields')['display_name'] is None or block.get('fields')['display_name'] == "" else 'SGA file'
                        dict2['sga_display_name'] = sga_display_name
                        break

    print 'dict2:', dict2

    accessment_info = {'ora_display_name': ora_display_name if dict2.has_key('ora_display_name') else '', 'submission_start': dict2['submission_start'] if dict2.has_key('submission_start') else '',
                       'submission_due': dict2['submission_due'] if dict2.has_key('submission_due') else '', 'sga_display_name': sga_display_name if dict2.has_key('sga_display_name') else '',
                       'start': dict2['start'] if dict2.has_key('start') else '', 'due': dict2['due'] if dict2.has_key('due') else ''}

    return accessment_info


def course_block_id(published_branch, children_id, sga_id):
    client = MongoClient(settings.CONTENTSTORE.get('DOC_STORE_CONFIG').get('host'), settings.CONTENTSTORE.get('DOC_STORE_CONFIG').get('port'))
    db = client.edxapp
    cursor2 = db.modulestore.structures.find({'_id': published_branch}, {'_id': 0, 'blocks': {'$elemMatch': {'block_id': children_id}}})

    for cur in cursor2:
        submission_blocks = cur.get('blocks')
        for sblock in submission_blocks:
            submission_fields = sblock.get('fields')
            for sf in submission_fields['children']:
                if sga_id == sf[1]:
                    block_id = submission_blocks['block_id']

    return block_id


def create_temp_answer(course_id):
    reload(sys)
    sys.setdefaultencoding('utf-8')

    ora_file = ''

    con = mdb.connect(settings.DATABASES.get('default').get('HOST'), settings.DATABASES.get('default').get('USER'), settings.DATABASES.get('default').get('PASSWORD'),
                      settings.DATABASES.get('default').get('NAME'));
    query = "delete from tb_tmp_answer where course_id = '" + course_id + "'"
    cur = con.cursor()
    cur.execute(query)
    print 'query :::', query

    query1 = """
        SELECT item_type,
             uuid,
             raw_answer
        FROM submissions_studentitem a, submissions_submission b
       WHERE a.id = b.student_item_id
         and a.course_id = '{course_id}';
    """.format(
        course_id=course_id
    )

    arr_course_id = course_id.split('+')
    query3 = "delete from vw_copykiller where class_id='{course}'".format(course=arr_course_id[1])
    with con:
        cur.execute("set names utf8")
        log.info(u'create_temp_answer query1 ::: %s', query1)
        cur.execute(query1)
        for (item_type, uuid, raw_answer) in cur:
            ans_json = json.loads(raw_answer)

            if item_type == 'openassessment':
                try:
                    answer = ans_json['parts'][0]['text']
                except Exception as e:
                    answer = 'no_answer'
                    log.error(ans_json)
                    log.error(e)

            elif item_type == 'sga':
                answer = ans_json['sha1'] + ":" + str(ans_json['filename'])
            else:
                answer = 'no_answer'

            log.info(u'item_type == %s, answer == %s' % (item_type, answer))

            # answer = answer.decode('unicode_escape')
            # answer = answer.encode('utf-8')
            # answer = answer.decode('utf-8')

            # query2 = "insert into tb_tmp_answer (course_id, uuid, raw_answer, item_type) "
            # query2 += "select '" + course_id + "', '" + uuid + "', '" + answer + "', '" + item_type + "' "

            answer = answer.replace('"', '\\\"')

            query2 = '''
                 insert into tb_tmp_answer (course_id, uuid, raw_answer, item_type)
                    select "{course_id}", "{uuid}","{answer}", "{item_type}"
            '''.format(course_id=course_id, uuid=uuid, answer=answer, item_type=item_type)

            query2 = str(query2)
            log.info(u'query2 ========= %s' % (query2))
            # print 'create_temp_answer query2 :::', query2
            cur.execute(query2)

        # print 'create_temp_answer query3 :::', query3
        cur.execute(query3)
    cur.close()
    con.close()


def copykiller(request, course_id):
    reload(sys)
    sys.setdefaultencoding('utf-8')
    print course_id

    course = return_course(course_id)
    assessment_info = get_assessment_info(course)
    create_temp_answer(course_id)

    con = mdb.connect(settings.DATABASES.get('default').get('HOST'), settings.DATABASES.get('default').get('USER'), settings.DATABASES.get('default').get('PASSWORD'),
                      settings.DATABASES.get('default').get('NAME'))

    query = """
        INSERT INTO vw_copykiller(uri,
                                  year_id,
                                  year_name,
                                  term_id,
                                  term_name,
                                  class_id,
                                  class_name,
                                  report_id,
                                  report_name,
                                  student_id,
                                  student_name,
                                  student_number,
                                  start_date,
                                  end_date,
                                  submit_date,
                                  title,
                                  content,
                                  attach_file_name,
                                  attach_file_path)
            SELECT submission_uuid,
                   year(curdate())                year_id,
                   concat(year(curdate()), '년') year_name,
                  '{course_run}'                   term_id,
                  '{course_run}'                   term_name,
                  '{course_course}'                class_id,
                  '{course_display_name}'          class_name,
                   a.item_id                          report_id,
                  '{ora_display_name}'             report_name,
                   c.username                     student_id,
                   d.name                         student_name,
                   c.id                           student_number,
                   DATE_FORMAT('{submission_start}', '%Y%m%d%H%i%s')                start_date,
                   DATE_FORMAT('{submission_due}', '%Y%m%d%H%i%s')                end_date,
                   DATE_FORMAT(completed_at, '%Y%m%d%H%i%s')                   submit_date,
                   '{ora_display_name}'        title,
                   e.raw_answer                   content,
                   if(
                      LOCATE('"file_key":', g.raw_answer) = 0,
                          '',
                          'content')
                      attach_file_name,
                   if(
                      LOCATE('"file_key":', g.raw_answer) = 0,
                      '',
                      CONCAT(
                         CONCAT(
                            '/edx/var/edxapp/media/ora-upload/submissions_attachments/',
                            SUBSTRING_INDEX(
                               SUBSTRING_INDEX(g.raw_answer, "file_key\\\":\\\"", -1),
                               '\\\"',
                               1)),
                         '/content'))
                      attach_file_path
              FROM assessment_peerworkflow a
                   JOIN student_anonymoususerid b ON a.student_id = b.anonymous_user_id
                   JOIN auth_user c ON b.user_id = c.id
                   JOIN auth_userprofile d ON c.id = d.user_id
                   JOIN tb_tmp_answer e ON a.submission_uuid = e.uuid
                   JOIN submissions_studentitem f ON a.student_id = f.student_id
                   JOIN submissions_submission g
                      ON f.id = g.student_item_id AND a.submission_uuid = g.uuid
             WHERE     completed_at IS NOT NULL
                   AND a.item_id NOT LIKE '%DEMOk%'
                   AND a.course_id = '{course_id}'
                   AND g.attempt_number = (SELECT max(attempt_number)
                                             FROM submissions_submission
                                            WHERE student_item_id = f.id)
            UNION ALL
            SELECT b.uuid,
               year(curdate())                                       year_id,
               concat(year(curdate()), '년')                        year_name,
               '{course_run}'                   term_id,
                  '{course_run}'                   term_name,
                  '{course_course}'                class_id,
                  '{course_display_name}'          class_name,
               item_id                                               report_id,
               '{sga_display_name}'                                           report_name,
               e.username                                            student_id,
               f.name                                                student_name,
               e.id                                                  student_number,
               DATE_FORMAT('{start}', '%Y%m%d%H%i%s')    start_date,
               DATE_FORMAT('{due}', '%Y%m%d%H%i%s')    end_date,
               DATE_FORMAT(submitted_at, '%Y%m%d%H%i%s')             submit_date,
               ''                                                    title,
               ''                                                    content,
               SUBSTRING(d.raw_answer, instr(d.raw_answer, ':') + 1) attach_file_name,
               concat('/edx/var/edxapp/media',
                      '/',
                      '{course_org}',
                      '/',
                      '{course_course}',
                      '/edx_sga/',
                      substring_index(item_id, '@', -1),
                      '/',
                      SUBSTRING_INDEX(d.raw_answer, ':', 1),
                      SUBSTRING(d.raw_answer, instr(d.raw_answer, '.')))
                  attach_file_path
          FROM submissions_studentitem a
               JOIN submissions_submission b ON a.id = b.student_item_id
               JOIN student_anonymoususerid c ON a.student_id = c.anonymous_user_id
               JOIN tb_tmp_answer d ON a.course_id = d.course_id AND b.uuid = d.uuid
               JOIN auth_user e ON c.user_id = e.id
               JOIN auth_userprofile f ON c.user_id = f.user_id AND e.id = f.user_id
         WHERE     a.course_id = '{course_id}'
               AND a.item_type = 'sga'
               AND b.attempt_number = (SELECT max(attempt_number)
                                         FROM submissions_submission
                                        WHERE student_item_id = a.id)
    """.format(course_run=str(course.id.run), course_course=str(course.id.course),
               course_display_name=str(course.display_name),
               ora_display_name=str(assessment_info['ora_display_name']),
               submission_start=str(assessment_info['submission_start']),
               submission_due=str(assessment_info['submission_due']), course_id=str(course_id),
               sga_display_name=str(assessment_info['sga_display_name']), start=str(assessment_info['start']),
               due=str(assessment_info['due']), course_org=str(course.id.org))

    query1 = "delete from tb_tmp_answer where 1=1"

    print 'query =', query
    print 'query1 = ', query1

    with con:
        cur = con.cursor()
        cur.execute("set names utf8")
        cur.execute(query)
        cur.execute(query1)

    response_data = {}
    response_data['result'] = 'success'
    # return HttpResponse(simplejson.dumps(response_data), mimetype='application/javascript')
    return HttpResponse(simplejson.dumps(response_data), content_type='application/javascript')


def get_copykiller_result(request, course_id):
    con = mdb.connect(settings.DATABASES.get('default').get('HOST'), settings.DATABASES.get('default').get('USER'), settings.DATABASES.get('default').get('PASSWORD'),
                      settings.DATABASES.get('default').get('NAME'));
    cur = con.cursor()
    query = "select "
    query += "v.student_id, "
    query += "v.report_id assessment_no, "
    query += "concat('=HYPERLINK(\"',concat('http://pjsearch.kmooc.kr:8080/ckplus/copykiller.jsp?uri=', v.uri, '&property_id=0&lang=ko'),'\",\"',(select r.disp_total_copy_ratio from tb_copykiller_copyratio r where r.uri=v.uri and r.check_type='total'),'\")') total, "
    query += "concat('=HYPERLINK(\"',concat('http://pjsearch.kmooc.kr:8080/ckplus/copykiller.jsp?uri=', v.uri, '&property_id=1&lang=ko'),'\",\"',(select r.disp_total_copy_ratio from tb_copykiller_copyratio r where r.uri=v.uri and r.check_type='year'),'\")') year, "
    query += "concat('=HYPERLINK(\"',concat('http://pjsearch.kmooc.kr:8080/ckplus/copykiller.jsp?uri=', v.uri, '&property_id=2&lang=ko'),'\",\"',(select r.disp_total_copy_ratio from tb_copykiller_copyratio r where r.uri=v.uri and r.check_type='term'),'\")') term, "
    query += "concat('=HYPERLINK(\"',concat('http://pjsearch.kmooc.kr:8080/ckplus/copykiller.jsp?uri=', v.uri, '&property_id=3&lang=ko'),'\",\"',(select r.disp_total_copy_ratio from tb_copykiller_copyratio r where r.uri=v.uri and r.check_type='class'),'\")') class, "
    query += "concat('=HYPERLINK(\"',concat('http://pjsearch.kmooc.kr:8080/ckplus/copykiller.jsp?uri=', v.uri, '&property_id=4&lang=ko'),'\",\"',(select r.disp_total_copy_ratio from tb_copykiller_copyratio r where r.uri=v.uri and r.check_type='report'),'\")') report, "
    query += "concat('=HYPERLINK(\"',concat('http://pjsearch.kmooc.kr:8080/ckplus/copykiller.jsp?uri=', v.uri, '&property_id=100&lang=ko'),'\",\"',(select r.disp_total_copy_ratio from tb_copykiller_copyratio r where r.uri=v.uri and r.check_type='internet' and r.complete_status = 'Y'),'\")') internet "
    query += "from "
    query += "vw_copykiller v "
    query += "where "
    query += "v.uri in (select uri from tb_copykiller_copyratio) "
    query += "and concat(class_id, '+', term_id) = '" + course_id[course_id.index('+') + 1:] + "'"
    query += "order by assessment_no, student_id "

    print 'get_copykiller_result query :', query

    log.info(u'get_copykiller_result query:', query)
    cur.execute(query)
    rows = cur.fetchall()
    cur.close()
    con.close()
    result_list = list()
    for row in rows:
        result_list.append(row[0:])
    return result_list


def copykiller_csv(request, course_id):
    result_list = get_copykiller_result(request, course_id)
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="' + course_id + '.csv"'
    writer = csv.writer(response)
    writer.writerow(['student id', 'assessment no', 'total', 'year', 'term', 'class', 'report', 'internet'])
    for value in result_list:
        writer.writerow(value)
    return response
