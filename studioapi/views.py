from rest_framework.response import Response
from rest_framework.generics import CreateAPIView
from openedx.core.lib.api.view_utils import view_auth_classes, DeveloperErrorViewMixin
from openedx.core.djangoapps.models.course_details import CourseDetails
from opaque_keys.edx.keys import CourseKey
from xmodule.modulestore.django import modulestore
from cms.djangoapps.contentstore.views.course import get_course_and_check_access
from django.conf import settings
from django.contrib.auth import authenticate, login
from django.db import transaction
from django.utils.translation import ugettext as _, get_language
from student.models import (
    Registration, UserProfile,
    PendingEmailChange, CourseEnrollment, CourseEnrollmentAttribute, unique_id_for_user,
    CourseEnrollmentAllowed, UserStanding, LoginFailures,
    create_comments_service_user, PasswordHistory, UserSignupSource,
    DashboardConfiguration, LinkedInAddToProfileConfiguration, ManualEnrollmentAudit, ALLOWEDTOENROLL_TO_ENROLLED,
    LogoutViewConfiguration, RegistrationCookieConfiguration)
from student.forms import AccountCreationForm, PasswordResetFormNoActive, get_registration_extension_form
from xmodule.modulestore.django import modulestore
from opaque_keys.edx.keys import CourseKey
import dogstats_wrapper as dog_stats_api
import third_party_auth
from third_party_auth import pipeline, provider
from openedx.core.djangoapps.lang_pref import LANGUAGE_KEY
from openedx.core.djangoapps.user_api.preferences import api as preferences_api
from student.views import REGISTER_USER
from student.views import _do_create_account
from datetime import datetime
from django.utils.timezone import UTC
from datetime import datetime, timedelta, tzinfo
from contentstore.views.course import create_new_course_in_store
from student.roles import CourseInstructorRole, CourseStaffRole, LibraryUserRole
from student.auth import STUDIO_EDIT_ROLES, STUDIO_VIEW_USERS, get_user_permissions
from student import auth
from contentstore.utils import reverse_library_url, add_instructor
from course_action_state.models import CourseRerunState
from xmodule.modulestore import EdxJSONEncoder
import json
from contentstore.tasks import rerun_course
from django.core.exceptions import ObjectDoesNotExist
from cms.djangoapps.models.settings.course_metadata import CourseMetadata

from .serializers import UpdateCourseSerializer
from .serializers import CreateUserSerializer
from .serializers import CreateCourseSerializer
from .serializers import EnrollUserSerializer
from .serializers import RerunCourseSerializer
from .serializers import ManageUserSerializer

from django.contrib.auth.models import User

import logging
log = logging.getLogger(__name__)

###############################################################

def user_with_role(user, role):
    """ Build user representation with attached role """
    return {
        'id': user.id,
        'username': user.username,
        'email': user.email,
        'role': role
    }

@view_auth_classes(is_authenticated=False)
class ManageUserView(DeveloperErrorViewMixin, CreateAPIView):

    serializer_class = ManageUserSerializer

    def create(self, request):

        email_string = request.POST.get('email')
        course_key_string = request.POST.get('id')
        course_key = CourseKey.from_string(course_key_string)

        user = User.objects.get(email=email_string)
        user_data = User.objects.get(username='staff')

###
        if(user.is_staff == True):
            """
            requester_perms = 15
            is_library = False
            role_hierarchy = (CourseInstructorRole, CourseStaffRole)
            #new_role = u'staff'
            #new_role = u'instructor'
            old_roles = set()
            role_added = False
            for role_type in role_hierarchy:
                role = role_type(course_key)
                if role_type.ROLE == u'instructor':
                    if (requester_perms & STUDIO_EDIT_ROLES) or (user.id == user_data and old_roles):
                        auth.add_users(user_data, role, user)
                        role_added = True
                elif role.has_user(user, check_user_activation=False):
                    pass
            if u'instructor' and not role_added:
                pass
            for role in old_roles:
                pass
            if u'instructor' and not is_library:
                CourseEnrollment.enroll(user, course_key)
            """
            return Response({"result": "true"})
###

        course_module = modulestore().get_course(course_key)
        instructors = set(CourseInstructorRole(course_key).users_with_role())
        staff = set(CourseStaffRole(course_key).users_with_role()).union(instructors)

        formatted_users = []
        for user in instructors:
            formatted_users.append(user_with_role(user, 'instructor'))
        for user in staff - instructors:
            formatted_users.append(user_with_role(user, 'staff'))

        for email in formatted_users:
            has_email = email['email']
            if(has_email == email_string):
                return Response({"result": "true"})
        return Response({"result": "false"})

###############################################################

@view_auth_classes(is_authenticated=False)
class UpdateCourseView(DeveloperErrorViewMixin, CreateAPIView):

    serializer_class = UpdateCourseSerializer

    def create(self, request):

        display_name_string = request.POST.get('display_name')
        course_key_string = request.POST.get('id')
        start_date_string = request.POST.get('start_date')
        end_date_string = request.POST.get('end_date')
        enrollment_start_string = request.POST.get('enrollment_start')
        enrollment_end_string = request.POST.get('enrollment_end')
        image_dir_string = request.POST.get('image_dir')
        short_description_string = request.POST.get('short_description')
        #description_string = request.POST.get('description')
        overview_string = request.POST.get('overview')

        # ------ TIME CONVERTER ------ #
        log.info("******* TIME CHECK *******")
        log.info(start_date_string) 
        log.info(end_date_string)
        log.info(enrollment_start_string)
        log.info(enrollment_end_string)
        log.info("******* TIME CHECK *******")

        start_date = datetime(
            int(start_date_string[0:4]),
            int(start_date_string[5:7]),
            int(start_date_string[8:10]),
            int(start_date_string[11:13]),
            int(start_date_string[14:16])
        )

        end_date = datetime(
            int(end_date_string[0:4]),
            int(end_date_string[5:7]),
            int(end_date_string[8:10]),
            int(end_date_string[11:13]),
            int(end_date_string[14:16])
        )

        enrollment_start = datetime(
            int(enrollment_start_string[0:4]),
            int(enrollment_start_string[5:7]),
            int(enrollment_start_string[8:10]),
            int(enrollment_start_string[11:13]),
            int(enrollment_start_string[14:16])
        )

        enrollment_end = datetime(
            int(enrollment_end_string[0:4]),
            int(enrollment_end_string[5:7]),
            int(enrollment_end_string[8:10]),
            int(enrollment_end_string[11:13]),
            int(enrollment_end_string[14:16])
        )

        sync_time = timedelta(hours=9)

        start_date = start_date - sync_time
        end_date = end_date - sync_time
        enrollment_start = enrollment_start - sync_time
        enrollment_end = enrollment_end - sync_time

        start_date = str(start_date)
        end_date = str(end_date)
        enrollment_start = str(enrollment_start)
        enrollment_end = str(enrollment_end)

        start_date_string = "{}-{}-{}T{}:{}:{}Z".format(start_date[0:4], start_date[5:7], start_date[8:10], start_date[11:13], start_date[14:16], '00')
        end_date_string = "{}-{}-{}T{}:{}:{}Z".format(end_date[0:4], end_date[5:7], end_date[8:10], end_date[11:13], end_date[14:16], '00')
        enrollment_start_string = "{}-{}-{}T{}:{}:{}Z".format(enrollment_start[0:4], enrollment_start[5:7], enrollment_start[8:10], enrollment_start[11:13], enrollment_start[14:16], '00')
        enrollment_end_string = "{}-{}-{}T{}:{}:{}Z".format(enrollment_end[0:4], enrollment_end[5:7], enrollment_end[8:10], enrollment_end[11:13], enrollment_end[14:16], '00')

        log.info("******* TIME CHECK (CONVERTER) *******")
        log.info(start_date_string)
        log.info(end_date_string)
        log.info(enrollment_start_string)
        log.info(enrollment_end_string)
        log.info("******* TIME CHECK (CONVERTER) ********")
        # ------ TIME CONVERTER ------ #

        update_data = {
            u'org': u'',
            u'course_id': u'',
            u'run': u'',

            u'start_date': start_date_string,
            u'end_date': end_date_string,

            u'enrollment_start': enrollment_start_string,
            u'enrollment_end': enrollment_end_string,

            u'course_image_name': u'',
            u'course_image_asset_path': u'',

            u'banner_image_name': u'',
            u'banner_image_asset_path': u'',

            u'video_thumbnail_image_name': u'',
            u'video_thumbnail_image_asset_path': u'',

            u'language': u'en',

            u'short_description': short_description_string,
            u'description': u'',

            u'overview': overview_string,

            u'entrance_exam_minimum_score_pct': u'50',
            u'entrance_exam_id': u'',
            u'entrance_exam_enabled': u'',

            u'duration': u'',
            u'subtitle': u'',
            u'title': u'testtest',

            u'pre_requisite_courses': [],
            u'instructor_info': {u'instructors': []},
            u'learning_info': [],

            u'effort': None,
            u'license': None,
            u'intro_video': None,
            u'self_paced': False,
            u'syllabus': None
        }

        # validate check #
        from xmodule.fields import Date
        date = Date()
        converted_start_date = date.from_json(update_data['start_date'])
        converted_end_date = date.from_json(update_data['end_date'])
        converted_enrollment_start = date.from_json(update_data['enrollment_start'])
        converted_enrollment_end = date.from_json(update_data['enrollment_end'])
        if(converted_enrollment_start > converted_enrollment_end):
            return Response({"result": "fail - 1"})
        if (converted_start_date > converted_end_date):
            return Response({"result": "fail - 2"})
        # validate check #

        course_key = CourseKey.from_string(course_key_string)
        with modulestore().bulk_operations(course_key):
            user_data = User.objects.get(username='staff')
            course_module = get_course_and_check_access(course_key, user_data)
            CourseDetails.update_from_json_good(course_key, update_data, user_data, image_dir_string)

        descriptor = course_module
        key_values = {u'display_name': display_name_string}
        user = user_data
        CourseMetadata.update_from_dict(key_values, descriptor, user)
        #update display_name

        """
        email_admin_string = request.POST.get('email_admin')
        email_staff_string = request.POST.get('email_staff')

        email_admin_string = email_admin_string.encode("utf8")
        email_staff_string = email_staff_string.encode("utf8")

        email_admin_list = email_admin_string.split(':')
        email_staff_list = email_staff_string.split(':')

        course_key = CourseKey.from_string(course_key_string)
        user_admin_list = []
        user_staff_list = []

        for email_loop in email_admin_list:
            try:
                user_admin_loop = User.objects.get(email=email_loop)
            except ObjectDoesNotExist:
                user_admin_loop = None
            user_admin_list.append(user_admin_loop)

        for email_loop in email_staff_list:
            try:
                user_staff_loop = User.objects.get(email=email_loop)
            except ObjectDoesNotExist:
                user_staff_loop = None
            user_staff_list.append(user_staff_loop)

        requester_perms = 15
        is_library = False
        role_hierarchy = (CourseInstructorRole, CourseStaffRole)
        #new_role = u'staff'
        #new_role = u'instructor'
        old_roles = set()
        role_added = False

        #admin enrollment
        for user in user_admin_list:
            if user is None:
                break
            for role_type in role_hierarchy:
                role = role_type(course_key)
                if role_type.ROLE == u'instructor':
                    if (requester_perms & STUDIO_EDIT_ROLES) or (user.id == user_data and old_roles):
                        auth.add_users(user_data, role, user)
                        role_added = True
                elif role.has_user(user, check_user_activation=False):
                    pass
            if u'instructor' and not role_added:
                pass
            for role in old_roles:
                pass
            if u'instructor' and not is_library:
                CourseEnrollment.enroll(user, course_key)

        # staff enrollment
        for user in user_staff_list:
            if user is None:
                break
            for role_type in role_hierarchy:
                role = role_type(course_key)
                if role_type.ROLE == u'staff':
                    if (requester_perms & STUDIO_EDIT_ROLES) or (user.id == user_data and old_roles):
                        auth.add_users(user_data, role, user)
                        role_added = True
                elif role.has_user(user, check_user_activation=False):
                    pass
            if u'staff' and not role_added:
                pass
            for role in old_roles:
                pass
            if u'staff' and not is_library:
                CourseEnrollment.enroll(user, course_key)
        """

        log.info("******** Update ok")
        return Response({"result": "ok"})

@view_auth_classes(is_authenticated=False)
class CreateUserView(DeveloperErrorViewMixin, CreateAPIView):

    serializer_class = CreateUserSerializer

    def create(self, request):

        ###### REQUEST POST DATA #####
        email_string = request.POST.get('email')
        full_name_string = request.POST.get('full_name')
        public_username_string = request.POST.get('public_username')
        password_string = request.POST.get('password')
        location_string = request.POST.get('location')
        language_string = request.POST.get('language')
        ###### REQUEST POST DATA #####

        params = {
            u'username': public_username_string,
            u'name': full_name_string,
            u'language': language_string,
            u'location': location_string,
            u'honor_code': u'true',
            u'terms_of_service': u'true',
            u'password': password_string,
            u'email': email_string
        }

        extra_fields = {}
        should_link_with_social_auth = False
        extra_fields = {'data_sharing_consent': None}
        do_external_auth = False
        extended_profile_fields = {}
        enforce_password_policy = False
        registration_fields = {}
        tos_required = True
        form = AccountCreationForm(
            data = params,
            extra_fields = {'data_sharing_consent': None},
            extended_profile_fields = {},
            enforce_username_neq_password = True,
            enforce_password_policy = False,
            tos_required = True,
        )
        custom_form = None
        with transaction.atomic():
            (user, profile, registration) = _do_create_account(form, custom_form)
        preferences_api.set_user_preference(user, LANGUAGE_KEY, get_language())
        if settings.FEATURES.get('ENABLE_DISCUSSION_EMAIL_DIGEST'):
            pass
        dog_stats_api.increment("common.student.account_created")
        third_party_provider = None
        running_pipeline = None
        if third_party_auth.is_enabled() and pipeline.running(request):
            pass
        if hasattr(settings, 'LMS_SEGMENT_KEY') and settings.LMS_SEGMENT_KEY:
            pass
        REGISTER_USER.send(sender=None, user=user, profile=profile)
        create_comments_service_user(user)
        send_email = False
        if send_email:
            pass
        else:
            registration.activate()
        new_user = authenticate(username=user.username, password=params['password'])
        login(request, new_user)
        request.session.set_expiry(0)
        try:
            pass
        except Exception:
            pass
        if new_user is not None:
            pass
        if do_external_auth:
            pass
        return Response({"result": "ok"})

@view_auth_classes(is_authenticated=False)
class CreateCourseView(DeveloperErrorViewMixin, CreateAPIView):

    serializer_class = CreateCourseSerializer

    def create(self, request):

        ###### REQUEST POST DATA #####
        display_name_string = request.POST.get('display_name')
        org_string = request.POST.get('org')
        number_string = request.POST.get('number')
        run_string = request.POST.get('run')

        has_org_string = request.POST.get('has_org')
        has_number_string = request.POST.get('has_number')
        has_run_string = request.POST.get('has_run')
        ###### REQUEST POST DATA #####

        #new
        display_name = display_name_string
        org = org_string
        course = number_string
        number = number_string
        run = run_string

        #old
        has_org = has_org_string
        has_course = has_number_string
        has_number = has_number_string
        has_run = has_run_string

        #create staff
        user_data = User.objects.get(username='staff')

        #create new key
        course_key_string = "course-v1:" + org + "+" + number + "+" + run
        course_key = CourseKey.from_string(course_key_string)

        #create old key
        has_course_key_string = "course-v1:" + has_org + "+" + has_number + "+" + has_run
        try:
            has_course_key = CourseKey.from_string(has_course_key_string)
        except BaseException:
            has_course_key = None

        #DB check (new)
        course_module = get_course_and_check_access(course_key, user_data)

        # DB check (old)
        try:
            has_course_module = get_course_and_check_access(has_course_key, user_data)
        except BaseException:
            has_course_module = None

        if(course_module != None):
            ### Course PASS OK ###
            return Response({"result": "ok"})

        else:
            if (has_course_module != None):
                # copy
                src_course_key = CourseKey.from_string(has_course_key_string)
                des_course_key = CourseKey.from_string(course_key_string)

                display_name = display_name_string
                org = org_string
                course = number_string
                number = number_string
                run = run_string

                test = datetime(2030, 1, 1, 00, 00, 00)

                fields = {'start': test}

                fields['display_name'] = display_name
                wiki_slug = u"{0}.{1}.{2}".format(org, course, run)
                definition_data = {'wiki_slug': wiki_slug}
                fields.update(definition_data)

                store = 'split'

                add_instructor(des_course_key, user_data, user_data)
                CourseRerunState.objects.initiated(src_course_key, des_course_key, user_data, fields['display_name'])
                fields['advertised_start'] = None
                json_fields = json.dumps(fields, cls=EdxJSONEncoder)
                rerun_course(unicode(src_course_key), unicode(des_course_key), user_data.id, json_fields) #bugfix
                ### Course COPY OK ###
                return Response({"result": "ok"})
            else:
                #non copy
                test = datetime(2030, 1, 1, 00, 00, 00)
                fields = {'start': test}
                fields['display_name'] = display_name
                wiki_slug = u"{0}.{1}.{2}".format(org, course, run)
                definition_data = {'wiki_slug': wiki_slug}
                fields.update(definition_data)
                store = 'split'
                create_new_course_in_store(store, user_data, org, number, run, fields)
                ### Course Created OK ###
                return Response({"result": "ok"})

@view_auth_classes(is_authenticated=False)
class EnrollUserView(DeveloperErrorViewMixin, CreateAPIView):

    serializer_class = EnrollUserSerializer

    def create(self, request):

        email_string = request.POST.get('email')
        course_key_string = request.POST.get('course_key')

        user_data = User.objects.get(username='staff')

        log.info("#############")
        log.info(email_string)
        log.info("#############")
        log.info(course_key_string)
        try:
            user = User.objects.get(email=email_string)
            course_key = CourseKey.from_string(course_key_string)

            requester_perms = 15
            is_library = False
            role_hierarchy = (CourseInstructorRole, CourseStaffRole)
            #new_role = u'staff'
            new_role = u'instructor'
            old_roles = set()
            role_added = False

            for role_type in role_hierarchy:
                role = role_type(course_key)
                if role_type.ROLE == new_role:
                    if (requester_perms & STUDIO_EDIT_ROLES) or (user.id == user_data and old_roles):
                        auth.add_users(user_data, role, user)
                        role_added = True
                elif role.has_user(user, check_user_activation=False):
                    pass
            if new_role and not role_added:
                pass
            for role in old_roles:
                pass
            if new_role and not is_library:
                CourseEnrollment.enroll(user, course_key)

        except ObjectDoesNotExist:
            log.info("return false")
            return Response({"result": "false"})
        log.info("return true")
        return Response({"result": "true"})

@view_auth_classes(is_authenticated=False)
class RerunCourseView(DeveloperErrorViewMixin, CreateAPIView):

    serializer_class = RerunCourseSerializer

    def create(self, request):

        ###### REQUEST POST DATA #####
        src_course_key_string = request.POST.get('id')
        display_name_string = request.POST.get('display_name')
        org_string = request.POST.get('org')
        number_string = request.POST.get('number')
        run_string = request.POST.get('run')
        ###### REQUEST POST DATA #####

        user_data = User.objects.get(username='staff')
        des_course_key_string = "course-v1:" + org_string + "+" + number_string + "+" + run_string

        src_course_key = CourseKey.from_string(src_course_key_string)
        des_course_key = CourseKey.from_string(des_course_key_string)

        display_name = display_name_string
        org = org_string
        course = number_string
        number = number_string
        run = run_string

        test = datetime(2030, 1, 1, 00, 00, 00)

        fields = {'start': test}

        fields['display_name'] = display_name
        wiki_slug = u"{0}.{1}.{2}".format(org, course, run)
        definition_data = {'wiki_slug': wiki_slug}
        fields.update(definition_data)

        store = 'split'

        add_instructor(des_course_key, user_data, user_data)
        CourseRerunState.objects.initiated(src_course_key, des_course_key, user_data, fields['display_name'])
        fields['advertised_start'] = None
        json_fields = json.dumps(fields, cls=EdxJSONEncoder)
        rerun_course.delay(unicode(src_course_key), unicode(des_course_key), request.user.id, json_fields)

        return Response({"result": "ok"})
