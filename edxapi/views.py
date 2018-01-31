from rest_framework.generics import CreateAPIView
from openedx.core.lib.api.view_utils import view_auth_classes, DeveloperErrorViewMixin
from rest_framework.response import Response
import subprocess
from course_blocks.api import get_course_blocks
from courseware.courses import get_course_with_access
from django.contrib.auth.models import User
from opaque_keys.edx.keys import CourseKey
from lms.djangoapps.grades.new.course_grade import CourseGradeFactory
from django.core.exceptions import ObjectDoesNotExist

from .serializers import DeleteCourseSerializer
from .serializers import ProgressUserSerializer
from .serializers import CourseEnrollSerializer

import logging
log = logging.getLogger(__name__)

################################################################################################################

from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import urllib, json
import dateutil
import json
from django.contrib.auth.models import User
from django.http import HttpResponseBadRequest
from django.utils.timezone import utc
from django.utils.translation import ugettext as _
from courseware.models import StudentFieldOverride
from courseware.field_overrides import disable_overrides
from courseware.student_field_overrides import (
    clear_override_for_user,
    get_override_for_user,
    override_field_for_user,
)
from xmodule.fields import Date
from opaque_keys.edx.keys import UsageKey
from student.models import (
    CourseEnrollment, unique_id_for_user, anonymous_id_for_user,
    UserProfile, Registration, EntranceExamConfiguration,
    ManualEnrollmentAudit, UNENROLLED_TO_ALLOWEDTOENROLL, ALLOWEDTOENROLL_TO_ENROLLED,
    ENROLLED_TO_ENROLLED, ENROLLED_TO_UNENROLLED, UNENROLLED_TO_ENROLLED,
    UNENROLLED_TO_UNENROLLED, ALLOWEDTOENROLL_TO_UNENROLLED, DEFAULT_TRANSITION_STATE
)
import re
from lms.djangoapps.instructor.views.tools import (
    dump_student_extensions,
    dump_module_extensions,
    find_unit,
    get_student_from_identifier,
    require_student_from_identifier,
    handle_dashboard_error,
    parse_datetime,
    set_due_date_extension,
    strip_if_string,
)
from lms.djangoapps.instructor.enrollment import (
    get_user_email_language,
    enroll_email,
    send_mail_to_student,
    get_email_params,
    send_beta_role_email,
    unenroll_email,
)
from django.core.validators import validate_email
from django.utils.html import strip_tags
from django.core.exceptions import ValidationError, PermissionDenied
from django.core.exceptions import ObjectDoesNotExist

def _get_boolean_param(request, param_name):
    return request.POST.get(param_name, False) in ['true', 'True', True]

def user_with_role(user, role):
    return {
        'id': user.id,
        'username': user.username,
        'email': user.email,
        'role': role
    }

def _split_input_list(str_list):

    new_list = re.split(r'[\n\r\s,]', str_list)
    new_list = [s.strip() for s in new_list]
    new_list = [s for s in new_list if s != '']

    return new_list

@view_auth_classes(is_authenticated=False)
class CourseEnrollView(DeveloperErrorViewMixin, CreateAPIView):

    serializer_class = CourseEnrollSerializer

    def create(self, request):

        #course_id = SlashSeparatedCourseKey.from_deprecated_string(course_id)

        course_id = request.POST.get('id')
        identifiers_raw = request.POST.get('email')
        action = request.POST.get('action') #enroll #unenroll

        course_key = CourseKey.from_string(course_id)
        user_data = User.objects.get(username='staff')

        identifiers = _split_input_list(identifiers_raw)

        auto_enroll = False
        email_students = False
        is_white_label = False
        reason = None
        enrollment_obj = None
        state_transition = DEFAULT_TRANSITION_STATE

        email_params = {}

        results = []
        for identifier in identifiers:
            user = None
            email = None
            language = None
            try:
                user = get_student_from_identifier(identifier)
            except User.DoesNotExist:
                email = identifier
            else:
                email = user.email
                language = get_user_email_language(user)
            try:
                try:
                    check = User.objects.get(email=email)
                except ObjectDoesNotExist:
                    return Response({"result": "invalid email"})
                ##### ENROLL #####
                if action == 'enroll':
                    before, after, enrollment_obj = enroll_email(
                        course_key, email, auto_enroll, email_students, email_params, language=language
                    )
                    before_enrollment = before.to_dict()['enrollment']
                    before_user_registered = before.to_dict()['user']
                    before_allowed = before.to_dict()['allowed']
                    after_enrollment = after.to_dict()['enrollment']
                    after_allowed = after.to_dict()['allowed']
                    if before_user_registered:
                        if after_enrollment:
                            if before_enrollment:
                                state_transition = ENROLLED_TO_ENROLLED
                            else:
                                if before_allowed:
                                    state_transition = ALLOWEDTOENROLL_TO_ENROLLED
                                else:
                                    state_transition = UNENROLLED_TO_ENROLLED
                    else:
                        if after_allowed:
                            state_transition = UNENROLLED_TO_ALLOWEDTOENROLL
                 ##### UN ENROLL #####
                elif action == 'unenroll':
                    before, after = unenroll_email(
                        course_key, email, email_students, email_params, language=language
                    )
                    before_enrollment = before.to_dict()['enrollment']
                    before_allowed = before.to_dict()['allowed']
                    enrollment_obj = CourseEnrollment.get_enrollment(user, course_id)
                    if before_enrollment:
                        state_transition = ENROLLED_TO_UNENROLLED
                    else:
                        if before_allowed:
                            state_transition = ALLOWEDTOENROLL_TO_UNENROLLED
                        else:
                            state_transition = UNENROLLED_TO_UNENROLLED
                else:
                    return HttpResponseBadRequest(strip_tags(
                        "Unrecognized action '{}'".format(action)
                    ))
            except ValidationError:
                results.append({
                    'identifier': identifier,
                    'invalidIdentifier': True,
                })
            except Exception as exc:
                log.exception(u"Error while #{}ing student")
                log.exception(exc)
                results.append({
                    'identifier': identifier,
                    'error': True,
                })
            else:
                ManualEnrollmentAudit.create_manual_enrollment_audit(user_data, email, state_transition, reason, enrollment_obj)
        return Response({"result": "ok"})

################################################################################################################

@view_auth_classes(is_authenticated=False)
class DeleteCourseView(DeveloperErrorViewMixin, CreateAPIView):

    serializer_class = DeleteCourseSerializer

    def create(self, request):

        COURSE_ID = request.POST.get('id')
        data = "/edx/bin/python.edxapp /edx/bin/manage.edxapp cms delete_course " + COURSE_ID + " --settings aws < /edx/app/edxapp/edx-platform/tt"
        subprocess.call (data, shell=True)
        return Response({"result": "ok"})

@view_auth_classes(is_authenticated=False)
class ProgressUserView(DeveloperErrorViewMixin, CreateAPIView):

    serializer_class = ProgressUserSerializer

    def create(self, request):

        course_key_string = request.POST.get('id')
        email_string = request.POST.get('email')

        # DEBUG #
        log.info(course_key_string)
        log.info(email_string)

        course_key = CourseKey.from_string(course_key_string)
        master_user = User.objects.get(username='staff')

        try:
            course = get_course_with_access(master_user, 'load', course_key, depth=None, check_if_enrolled=True)
        except BaseException:
            return Response({"result": 0.0})

        try:
            user_data = User.objects.get(email=email_string)
        except ObjectDoesNotExist:
            return Response({"result": 0.0})

        course_grade = CourseGradeFactory().create(user_data, course)

        # EXEPTION #
        if(course_grade == "false"):
            return Response({"result": 0.0})

        grade_summary = course_grade.summary
        result = grade_summary['percent']
        return Response({"result": result * 100})
