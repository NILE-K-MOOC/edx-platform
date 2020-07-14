# -*- coding: utf-8 -*-
from django.conf import settings
from django.conf.urls import include, url
from django.conf.urls.static import static
from django.contrib.admin import autodiscover as django_autodiscover
from django.utils.translation import ugettext_lazy as _
from django.views.generic.base import RedirectView
from rest_framework_swagger.views import get_swagger_view
from branding import views as branding_views
from config_models.views import ConfigurationModelCurrentAPIView
from courseware.masquerade import handle_ajax as courseware_masquerade_handle_ajax
from courseware.module_render import handle_xblock_callback, handle_xblock_callback_noauth, xblock_view, xqueue_callback
from courseware.views import views as courseware_views
from courseware.views.index import CoursewareIndex
from courseware.views.views import CourseTabView, EnrollStaffView, StaticCourseTabView
from debug import views as debug_views
from django_comment_common.models import ForumsConfig
from django_openid_auth import views as django_openid_auth_views
from lms.djangoapps.certificates import views as certificates_views
from lms.djangoapps.discussion import views as discussion_views
from lms.djangoapps.instructor.views import coupons as instructor_coupons_views
from lms.djangoapps.instructor.views import instructor_dashboard as instructor_dashboard_views
from lms.djangoapps.instructor.views import registration_codes as instructor_registration_codes_views
from lms.djangoapps.instructor_task import views as instructor_task_views
from lms_migration import migrate as lms_migrate_views
from notes import views as notes_views
from notification_prefs import views as notification_prefs_views
from openedx.core.djangoapps.auth_exchange.views import LoginWithAccessTokenView
from openedx.core.djangoapps.catalog.models import CatalogIntegration
from openedx.core.djangoapps.common_views.xblock import xblock_resource
from openedx.core.djangoapps.cors_csrf import views as cors_csrf_views
from openedx.core.djangoapps.course_groups import views as course_groups_views
from openedx.core.djangoapps.debug import views as openedx_debug_views
from openedx.core.djangoapps.external_auth import views as external_auth_views
from openedx.core.djangoapps.lang_pref import views as lang_pref_views
from openedx.core.djangoapps.password_policy import compliance as password_policy_compliance
from openedx.core.djangoapps.password_policy.forms import PasswordPolicyAwareAdminAuthForm
from openedx.core.djangoapps.plugins import constants as plugin_constants
from openedx.core.djangoapps.plugins import plugin_urls
from openedx.core.djangoapps.programs.models import ProgramsApiConfig
from openedx.core.djangoapps.self_paced.models import SelfPacedConfiguration
from openedx.core.djangoapps.site_configuration import helpers as configuration_helpers
from openedx.core.djangoapps.verified_track_content import views as verified_track_content_views
from openedx.features.enterprise_support.api import enterprise_enabled
from ratelimitbackend import admin
from static_template_view import views as static_template_view_views
from staticbook import views as staticbook_views
from student import views as student_views
from student_account import views as student_account_views
from openedx.core.djangoapps.log_action.views import LogAction
from track import views as track_views
from util import views as util_views
from courseware import courses as courses

'''
개발 시에 모듈을 기능별로 분리하여 개발하십시오
아래 모듈에 기생하지 마십시오

- student_account_views
- branding_views
- courses
- courseware_views
'''

# Custom Directory APP
# made by kotech system
from maeps import views as maeps                               # Markani Solution APP
from kotech_common import views as kotech_common_views         # Common APP
from kotech_survey import views as kotech_survey_views         # Course Satisfaction Survey APP
from kotech_series import views as kotech_series_views         # Series Course APP
from kotech_memo import views as kotech_memo_views             # Memo APP
from kotech_community import views as kotech_community_views   # Community APP
from kotech_lifelong import views as kotech_lifelong_views     # Lifelong APP
from kotech_roadmap import views as kotech_roadmap_views     # Lifelong APP

LogAction()
if settings.DEBUG or settings.FEATURES.get('ENABLE_DJANGO_ADMIN_SITE'):
    django_autodiscover()
    admin.site.site_header = _('LMS Administration')
    admin.site.site_title = admin.site.site_header
    if password_policy_compliance.should_enforce_compliance_on_login():
        admin.site.login_form = PasswordPolicyAwareAdminAuthForm





urlpatterns = [
    url(r'^$', branding_views.index, name='root'),

    # Common
    # made by kotech system
    url(r'^api/get_org_value$', kotech_common_views.get_org_value, name='get_org_value'),


    # Course Satisfaction Survey
    # made by kotech system
    url(r'^course_satisfaction_survey/$', kotech_survey_views.course_satisfaction_survey, name='course_satisfaction_survey'),             # render
    url(r'^api_course_satisfaction_survey/$', kotech_survey_views.api_course_satisfaction_survey, name='api_course_satisfaction_survey'), # api


    # AI road map
    url(r'^roadmap/$', kotech_roadmap_views.roadmap, name='roadmap'),
    url(r'^roadmap/down/$', kotech_roadmap_views.roadmap_download, name='roadmap_download'),
    url(r'^roadmap_view/(?P<id>.*?)/$', kotech_roadmap_views.roadmap_view, name='roadmap_view'),
    url(r'^about_intro/$', kotech_roadmap_views.about_intro, name='about_intro'),
    url(r'^about_st/$', kotech_roadmap_views.about_st, name='about_st'),
    url(r'^about_org/$', kotech_roadmap_views.about_org, name='about_org'),


    # Series
    # made by kotech system
    url(r'^new_dashboard$', kotech_series_views.new_dashboard, name='new_dashboard'),
    url(r'^series_print/(?P<id>.*?)/$', kotech_series_views.series_print, name='series_print'),
    url(r'^series/$', kotech_series_views.series, name='series'),
    url(r'^series_view/(?P<id>.*?)/about/$', kotech_series_views.series_about, name='series_about'),
    url(r'^series_view/(?P<id>.*?)/enroll$', kotech_series_views.series_enroll, name='series_enroll'),
    url(r'^series_view/(?P<id>.*?)/$', kotech_series_views.series_view, name='series_view'),
    url(r'^api/series_cancel$', kotech_series_views.series_cancel, name='series_cancel'),
    url(r'series_print$', maeps.series_print, name='series_print'),


    # Memo
    # made by kotech system
    url(r'^memo$', kotech_memo_views.memo, name='memo'),
    url(r'^memo_view/(?P<memo_id>.*?)/$', kotech_memo_views.memo_view, name='memo_view'),
    url(r'^memo_sync$', kotech_memo_views.memo_sync, name='memo_sync'),
    url(r'^dashboard_memo$', kotech_memo_views.dashboard_memo, name='dashboard_memo'),
    url(r'^dashboard_memo_read$', kotech_memo_views.dashboard_memo_read, name='dashboard_memo_read'),
    url(r'^dashboard_memo_detail$', kotech_memo_views.dashboard_memo_detail, name='dashboard_memo_detail'),

    # Xinics Login
    # made by kotech system
    url(r'^api/cb/login_check', kotech_community_views.cb_login_check, name="cb_login_check"),


    # Community
    # made by kotech system
    url(r'^comm_list/(?P<section>.*?)/(?P<curr_page>.*?)$', kotech_community_views.comm_list, name='comm_list'),
    url(r'^comm_view/(?P<section>.*?)/(?P<curr_page>.*?)/(?P<board_id>.*?)$', kotech_community_views.comm_view, name='comm_view'),
    url(r'^comm_tabs/(?P<head_title>.*?)/$', kotech_community_views.comm_tabs, name='comm_tabs'),
    url(r'^comm_file/(?P<file_id>.*?)/$', kotech_community_views.comm_file, name='comm_file'),
    url(r'^comm_notice$', kotech_community_views.comm_notice, name='comm_notice'),
    url(r'^comm_notice_view/(?P<board_id>.*?)/$', kotech_community_views.comm_notice_view, name='comm_notice_view'),
    url(r'^comm_repository$', kotech_community_views.comm_repository, name='comm_repository'),
    url(r'^comm_repo_view/(?P<board_id>.*?)/$', kotech_community_views.comm_repo_view, name='comm_repo_view'),
    url(r'^comm_mobile$', kotech_community_views.comm_mobile, name='comm_mobile'),
    url(r'^comm_mobile_view/(?P<board_id>.*?)/$', kotech_community_views.comm_mobile_view, name='comm_mobile_view'),
    url(r'^comm_faq/(?P<head_title>.*?)/$', kotech_community_views.comm_faq, name='comm_faq'),
    url(r'^comm_faqrequest/$', kotech_community_views.comm_faqrequest, name='comm_faqrequest'),
    url(r'^comm_hope_request/$', kotech_community_views.comm_hope_request, name='comm_hope_request'),
    url(r'^comm_faqrequest/(?P<head_title>.*?)/$', kotech_community_views.comm_faqrequest, name='comm_faqrequest'),
    url(r'^comm_k_news$', kotech_community_views.comm_k_news, name='comm_k_news'),
    url(r'^comm_k_news_view/(?P<board_id>.*?)/$', kotech_community_views.comm_k_news_view, name='comm_k_news_view'),
    url(r'^comm_list_json$', kotech_community_views.comm_list_json, name='comm_list_json'),


    # Lifelong API
    # made by kotech system
    url(r'^api/all_courses$', kotech_lifelong_views.course_api, name="course_api"),
    url(r'^cb_course_list$', kotech_lifelong_views.cb_course_list, name="cb_course_list"),
    url(r'^api/cb_course$', kotech_lifelong_views.cb_course, name="cb_course"),
    url(r'^cb_print/(?P<course_id>.*?)/$', kotech_lifelong_views.cb_print, name='cb_print'),


    # Self Auth
    # made by kotech system
    url(r'^nicecheckplus$', student_account_views.nicecheckplus, name="nicecheckplus"),
    url(r'^nicecheckplus_error$', student_account_views.nicecheckplus_error, name="nicecheckplus_error"),
    url(r'^agree$', student_account_views.agree, name="agree"),
    url(r'^agree_done$', student_account_views.agree_done, name="agree_done"),
    url(r'^parent_agree$', student_account_views.parent_agree, name="parent_agree"),
    url(r'^parent_agree_done$', student_account_views.parent_agree_done, name="parent_agree_done"),
    url(r'^org_check', student_account_views.org_check, name="org_check"),


    # Remove Account
    # made by kotech system
    url(r'^remove_account_view/$', student_account_views.remove_account_view, name="remove_account_view"),
    url(r'^remove_account$', student_account_views.remove_account, name="remove_account"),


    # Multisite (user page)
    # made by kotech system
    url(r'^api/get_org_list$', branding_views.get_org_list, name='get_org_list'),
    url(r'^api/get_multisite_list$', branding_views.get_multisite_list, name='get_multisite_list'),
    url(r'^api/delete_multisite_account$', branding_views.delete_multisite_account, name='delete_multisite_account'),


    # Multisite (index page)
    # made by kotech system
    url(r'^org/(?P<org>.*?)$', branding_views.multisite_index, name="multisite_index"),
    url(r'^multisite_error/$', branding_views.multisite_error, name="multisite_error"),


    # Index Course Detail
    # made by kotech system
    url(r'^course_detail/view/$', student_views.course_detail_view, name='course_detail_view'),
    url(r'^course_detail/excel/$', student_views.course_detail_excel, name='course_detail_excel'),


    # Course List
    # made by kotech system
    url(r'^course_search_list$', courses.course_search_list, name='course_list'),

    # Age Group Preference
    url(r'^age_specific/course/$', courses.age_specific_course, name='age_specific_course'),


    # Schools
    # made by kotech system
    url(r'^schools_make_filter/?$', courseware_views.schools_make_filter, name="schools_make_filter"),
    url(r'^schools_make_item/?$', courseware_views.schools_make_item, name="schools_make_item"),
    url(r'^school/(?P<org>.*?)/view/$', courseware_views.school_view, name="school_view"),
    url(r'^school/(?P<org>.*?)/$', courseware_views.haewoondaex, name="school"),


    # Course Review
    # made by kotech system
    url(r'^course_review/$', courseware_views.course_review, name='course_review'),
    url(r'^course_review_add$', courseware_views.course_review_add, name='course_review_add'),
    url(r'^course_review_del$', courseware_views.course_review_del, name='course_review_del'),
    url(r'^course_review_gb$', courseware_views.course_review_gb, name='course_review_gb'),


    # Interest Course
    # made by kotech system
    url(r'^course_interest$', courseware_views.course_interest, name='course_interest'),


    # footer link
    # made by kotech system
    url(r'^cert_check/?$', courseware_views.cert_check, name="cert_check"),
    url(r'^cert_check_id/?$', courseware_views.cert_check_id, name="cert_check_id"),
    url(r'^Privacy-Policy/?$', courseware_views.privacy, name="privacy"),
    url(r'^Privacy-Policy_old1/?$', courseware_views.privacy_old1, name="privacy_old1"),
    url(r'^Privacy-Policy_old2/?$', courseware_views.privacy_old2, name="privacy_old2"),
    url(r'^Privacy-Policy_old3/?$', courseware_views.privacy_old3, name="privacy_old3"),
    url(r'^Privacy-Policy_old4/?$', courseware_views.privacy_old4, name="privacy_old4"),
    url(r'^Privacy-Policy_old5/?$', courseware_views.privacy_old5, name="privacy_old5"),
    url(r'^agreement/?$', courseware_views.agreement, name="agreement"),
    url(r'^Copyright-Policy/?$', courseware_views.copyright, name="copyright"),

    # save_search_term (검색어 저장)
    url(r'^save_search_term/?$', courseware_views.save_search_term, name="save_search_term"),


    url(r'', include('student.urls')),
    # TODO: Move lms specific student views out of common code
    url(r'^dashboard/?$', student_views.student_dashboard, name='dashboard'),
    url(r'^dashboard_survey/?$', student_views.dashboard_survey_access, name='dashboard_survey_access'),
    url(r'^change_enrollment$', student_views.change_enrollment, name='change_enrollment'),
    url(r'^enrollment_verifi$', student_views.enrollment_verifi, name='enrollment_verifi'),
    # Event tracking endpoints
    url(r'', include('track.urls')),

    # Dashboard append url
    url(r'^call_dashboard$', student_views.call_dashboard, name='call_dashboard'),

    # Static template view endpoints like blog, faq, etc.
    url(r'', include('static_template_view.urls')),

    url(r'^heartbeat', include('openedx.core.djangoapps.heartbeat.urls')),

    # Note: these are older versions of the User API that will eventually be
    # subsumed by api/user listed below.
    url(r'^user_api/', include('openedx.core.djangoapps.user_api.legacy_urls')),

    url(r'^notifier_api/', include('notifier_api.urls')),

    url(r'^i18n/', include('django.conf.urls.i18n')),

    # Feedback Form endpoint
    url(r'^submit_feedback$', util_views.submit_feedback),

    # Enrollment API RESTful endpoints
    url(r'^api/enrollment/v1/', include('enrollment.urls')),

    # Entitlement API RESTful endpoints
    url(r'^api/entitlements/', include('entitlements.api.urls', namespace='entitlements_api')),

    # Courseware search endpoints
    url(r'^search/', include('search.urls')),

    # Course API
    url(r'^api/courses/', include('course_api.urls')),

    # Completion API
    url(r'^api/completion/', include('completion.api.urls', namespace='completion_api')),

    # User API endpoints
    url(r'^api/user/', include('openedx.core.djangoapps.user_api.urls')),

    # Profile Images API endpoints
    url(r'^api/profile_images/', include('openedx.core.djangoapps.profile_images.urls')),

    # Video Abstraction Layer used to allow video teams to manage video assets
    # independently of courseware. https://github.com/edx/edx-val
    url(r'^api/val/v0/', include('edxval.urls')),

    url(r'^api/commerce/', include('commerce.api.urls', namespace='commerce_api')),
    url(r'^api/credit/', include('openedx.core.djangoapps.credit.urls')),
    url(r'^rss_proxy/', include('rss_proxy.urls')),
    url(r'^api/organizations/', include('organizations.urls', namespace='organizations')),

    url(r'^catalog/', include('openedx.core.djangoapps.catalog.urls', namespace='catalog')),

    # Update session view
    url(r'^lang_pref/session_language', lang_pref_views.update_session_language, name='session_language'),

    # Multiple course modes and identity verification
    url(r'^course_modes/', include('course_modes.urls')),
    url(r'^verify_student/', include('verify_student.urls')),

    # URLs for managing dark launches of languages
    url(r'^update_lang/', include('openedx.core.djangoapps.dark_lang.urls', namespace='dark_lang')),

    # For redirecting to help pages.
    url(r'^help_token/', include('help_tokens.urls')),

    # URLs for API access management
    url(r'^api-admin/', include('openedx.core.djangoapps.api_admin.urls', namespace='api_admin')),

    url(r'^dashboard/', include('learner_dashboard.urls')),
    url(r'^api/experiments/', include('experiments.urls', namespace='api_experiments')),

]

# TODO: This needs to move to a separate urls.py once the student_account and
# student views below find a home together
if settings.FEATURES.get('ENABLE_COMBINED_LOGIN_REGISTRATION'):
    # Backwards compatibility with old URL structure, but serve the new views
    urlpatterns += [
        url(r'^login$', student_account_views.login_and_registration_form,
            {'initial_mode': 'login'}, name='signin_user'),
        url(r'^register$', student_account_views.login_and_registration_form,
            {'initial_mode': 'register'}, name='register_user'),
    ]
else:
    # Serve the old views
    urlpatterns += [
        url(r'^login$', student_views.signin_user, name='signin_user'),
        url(r'^register$', student_views.register_user, name='register_user'),
    ]

if settings.FEATURES.get('ENABLE_MOBILE_REST_API'):
    urlpatterns += [
        url(r'^api/mobile/v0.5/', include('mobile_api.urls')),
    ]

if settings.FEATURES.get('ENABLE_OPENBADGES'):
    urlpatterns += [
        url(r'^api/badges/v1/', include('badges.api.urls', app_name='badges', namespace='badges_api')),
    ]

# urlpatterns += [
#    url(r'^openassessment/fileupload/', include('openassessment.fileupload.urls')),
# ]

urlpatterns += [
    url(r'^openassessment/storage/', include('openassessment.fileupload.urls')),
]

# urlpatterns += oraurlpatterns

# sysadmin dashboard, to see what courses are loaded, to delete & load courses
if settings.FEATURES.get('ENABLE_SYSADMIN_DASHBOARD'):
    urlpatterns += [
        url(r'^sysadmin/', include('dashboard.sysadmin_urls')),
    ]

urlpatterns += [
    url(r'^support/', include('support.urls')),
]

# Favicon
favicon_path = configuration_helpers.get_value('favicon_path', settings.FAVICON_PATH)  # pylint: disable=invalid-name
urlpatterns += [
    url(r'^favicon\.ico$', RedirectView.as_view(url=settings.STATIC_URL + favicon_path, permanent=True)),
]

# Multicourse wiki (Note: wiki urls must be above the courseware ones because of
# the custom tab catch-all)
if settings.WIKI_ENABLED:
    from wiki.urls import get_pattern as wiki_pattern
    from course_wiki import views as course_wiki_views
    from django_notify.urls import get_pattern as notify_pattern

    urlpatterns += [
        # First we include views from course_wiki that we use to override the default views.
        # They come first in the urlpatterns so they get resolved first
        url('^wiki/create-root/$', course_wiki_views.root_create, name='root_create'),
        url(r'^wiki/', include(wiki_pattern())),
        url(r'^notify/', include(notify_pattern())),

        # These urls are for viewing the wiki in the context of a course. They should
        # never be returned by a reverse() so they come after the other url patterns
        url(r'^courses/{}/course_wiki/?$'.format(settings.COURSE_ID_PATTERN),
            course_wiki_views.course_wiki_redirect, name='course_wiki'),
        url(r'^courses/{}/wiki/'.format(settings.COURSE_KEY_REGEX),
            include(wiki_pattern(app_name='course_wiki_do_not_reverse', namespace='course_wiki_do_not_reverse'))),
    ]

COURSE_URLS = [
    url(
        r'^look_up_registration_code$',
        instructor_registration_codes_views.look_up_registration_code,
        name='look_up_registration_code',
    ),
    url(
        r'^registration_code_details$',
        instructor_registration_codes_views.registration_code_details,
        name='registration_code_details',
    ),
]

urlpatterns += [
    # jump_to URLs for direct access to a location in the course
    url(
        r'^courses/{}/jump_to/(?P<location>.*)$'.format(
            settings.COURSE_ID_PATTERN,
        ),
        courseware_views.jump_to,
        name='jump_to',
    ),
    url(
        r'^courses/{}/jump_to_id/(?P<module_id>.*)$'.format(
            settings.COURSE_ID_PATTERN,
        ),
        courseware_views.jump_to_id,
        name='jump_to_id',
    ),

    # xblock Handler APIs
    url(
        r'^courses/{course_key}/xblock/{usage_key}/handler/(?P<handler>[^/]*)(?:/(?P<suffix>.*))?$'.format(
            course_key=settings.COURSE_ID_PATTERN,
            usage_key=settings.USAGE_ID_PATTERN,
        ),
        handle_xblock_callback,
        name='xblock_handler',
    ),
    url(
        r'^courses/{course_key}/xblock/{usage_key}/handler_noauth/(?P<handler>[^/]*)(?:/(?P<suffix>.*))?$'.format(
            course_key=settings.COURSE_ID_PATTERN,
            usage_key=settings.USAGE_ID_PATTERN,
        ),
        handle_xblock_callback_noauth,
        name='xblock_handler_noauth',
    ),

    # xblock View API
    # (unpublished) API that returns JSON with the HTML fragment and related resources
    # for the xBlock's requested view.
    url(
        r'^courses/{course_key}/xblock/{usage_key}/view/(?P<view_name>[^/]*)$'.format(
            course_key=settings.COURSE_ID_PATTERN,
            usage_key=settings.USAGE_ID_PATTERN,
        ),
        xblock_view,
        name='xblock_view',
    ),

    # xblock Rendering View URL
    # URL to provide an HTML view of an xBlock. The view type (e.g., student_view) is
    # passed as a 'view' parameter to the URL.
    # Note: This is not an API. Compare this with the xblock_view API above.
    url(
        r'^xblock/{usage_key_string}$'.format(usage_key_string=settings.USAGE_KEY_PATTERN),
        courseware_views.render_xblock,
        name='render_xblock',
    ),

    # xblock Resource URL
    url(
        r'xblock/resource/(?P<block_type>[^/]+)/(?P<uri>.*)$',
        xblock_resource,
        name='xblock_resource_url',
    ),

    url(
        r'^courses/{}/xqueue/(?P<userid>[^/]*)/(?P<mod_id>.*?)/(?P<dispatch>[^/]*)$'.format(
            settings.COURSE_ID_PATTERN,
        ),
        xqueue_callback,
        name='xqueue_callback',
    ),

    # TODO: These views need to be updated before they work
    url(r'^calculate$', util_views.calculate),

    url(r'^courses/?$', branding_views.courses, name='courses'),
    url(r'^search_org/?$', courseware_views.search_org_name, name='search_org_name'),

    url(r'^mobile/comm_list/(?P<section>.*?)/(?P<curr_page>.*?)$', kotech_community_views.mobile_comm_list, name='mobile_comm_list'),
    url(r'^mobile/comm_tabs/$', kotech_community_views.mobile_comm_tabs, name='mobile_comm_tabs'),
    url(r'^mobile/comm_view/(?P<section>.*?)/(?P<curr_page>.*?)/(?P<board_id>.*?)$', kotech_community_views.mobile_comm_view, name='mobile_comm_view'),
    url(r'^mobile/series/$', kotech_series_views.mobile_series, name='mobile_series'),
    url(r'^mobile_courses/?$', branding_views.mobile_courses, name='mobile_courses'),

    # About the course
    url(
        r'^course/{}$'.format(
            settings.COURSE_ID_PATTERN,
        ),
        courseware_views.mobile_course_about,
        name='mobile_about_course',
    ),

    url(
        r'^courses/{}/about$'.format(
            settings.COURSE_ID_PATTERN,
        ),
        courseware_views.course_about,
        name='about_course',
    ),

    url(
        r'^courses/{}/enroll_staff$'.format(
            settings.COURSE_ID_PATTERN,
        ),
        EnrollStaffView.as_view(),
        name='enroll_staff',
    ),

    # Inside the course
    url(
        r'^courses/{}/$'.format(
            settings.COURSE_ID_PATTERN,
        ),
        courseware_views.course_info,
        name='course_root',
    ),
    url(
        r'^courses/{}/info$'.format(
            settings.COURSE_ID_PATTERN,
        ),
        courseware_views.course_info,
        name='info',
    ),
    # TODO arjun remove when custom tabs in place, see courseware/courses.py
    url(
        r'^courses/{}/syllabus$'.format(
            settings.COURSE_ID_PATTERN,
        ),
        courseware_views.syllabus,
        name='syllabus',
    ),

    # Survey associated with a course
    url(
        r'^courses/{}/survey$'.format(
            settings.COURSE_ID_PATTERN,
        ),
        courseware_views.course_survey,
        name='course_survey',
    ),

    url(
        r'^courses/{}/book/(?P<book_index>\d+)/$'.format(
            settings.COURSE_ID_PATTERN,
        ),
        staticbook_views.index,
        name='book',
    ),
    url(
        r'^courses/{}/book/(?P<book_index>\d+)/(?P<page>\d+)$'.format(
            settings.COURSE_ID_PATTERN,
        ),
        staticbook_views.index,
        name='book',
    ),

    url(
        r'^courses/{}/pdfbook/(?P<book_index>\d+)/$'.format(
            settings.COURSE_ID_PATTERN,
        ),
        staticbook_views.pdf_index,
        name='pdf_book',
    ),
    url(
        r'^courses/{}/pdfbook/(?P<book_index>\d+)/(?P<page>\d+)$'.format(
            settings.COURSE_ID_PATTERN,
        ),
        staticbook_views.pdf_index,
        name='pdf_book',
    ),

    url(
        r'^courses/{}/pdfbook/(?P<book_index>\d+)/chapter/(?P<chapter>\d+)/$'.format(
            settings.COURSE_ID_PATTERN,
        ),
        staticbook_views.pdf_index,
        name='pdf_book',
    ),
    url(
        r'^courses/{}/pdfbook/(?P<book_index>\d+)/chapter/(?P<chapter>\d+)/(?P<page>\d+)$'.format(
            settings.COURSE_ID_PATTERN,
        ),
        staticbook_views.pdf_index,
        name='pdf_book',
    ),

    url(
        r'^courses/{}/htmlbook/(?P<book_index>\d+)/$'.format(
            settings.COURSE_ID_PATTERN,
        ),
        staticbook_views.html_index,
        name='html_book',
    ),
    url(
        r'^courses/{}/htmlbook/(?P<book_index>\d+)/chapter/(?P<chapter>\d+)/$'.format(
            settings.COURSE_ID_PATTERN,
        ),
        staticbook_views.html_index,
        name='html_book',
    ),

    url(
        r'^courses/{}/courseware/?$'.format(
            settings.COURSE_ID_PATTERN,
        ),
        CoursewareIndex.as_view(),
        name='courseware',
    ),
    url(
        r'^courses/{}/courseware/(?P<chapter>[^/]*)/$'.format(
            settings.COURSE_ID_PATTERN,
        ),
        CoursewareIndex.as_view(),
        name='courseware_chapter',
    ),
    url(
        r'^courses/{}/courseware/(?P<chapter>[^/]*)/(?P<section>[^/]*)/$'.format(
            settings.COURSE_ID_PATTERN,
        ),
        CoursewareIndex.as_view(),
        name='courseware_section',
    ),
    url(
        r'^courses/{}/courseware/(?P<chapter>[^/]*)/(?P<section>[^/]*)/(?P<position>[^/]*)/?$'.format(
            settings.COURSE_ID_PATTERN,
        ),
        CoursewareIndex.as_view(),
        name='courseware_position',
    ),

    # progress page
    url(
        r'^courses/{}/progress$'.format(
            settings.COURSE_ID_PATTERN,
        ),
        courseware_views.progress,
        name='progress',
    ),

    # Takes optional student_id for instructor use--shows profile as that student sees it.
    url(
        r'^courses/{}/progress/(?P<student_id>[^/]*)/$'.format(
            settings.COURSE_ID_PATTERN,
        ),
        courseware_views.progress,
        name='student_progress',
    ),

    url(
        r'^programs/{}/about'.format(
            r'(?P<program_uuid>[0-9a-f-]+)',
        ),
        courseware_views.program_marketing,
        name='program_marketing_view',
    ),

    # For the instructor
    url(
        r'^courses/{}/instructor$'.format(
            settings.COURSE_ID_PATTERN,
        ),
        instructor_dashboard_views.instructor_dashboard_2,
        name='instructor_dashboard',
    ),

    # For copykiller
    url(
        r'^courses/{}/instructor/copykiller$'.format(settings.COURSE_ID_PATTERN),
        instructor_dashboard_views.copykiller,
        name="copykiller"
    ),

    url(
        r'^courses/{}/instructor/copykiller_csv'.format(settings.COURSE_ID_PATTERN),
        instructor_dashboard_views.copykiller_csv,
        name="copykiller_csv"
    ),

    url(
        r'^courses/{}/set_course_mode_price$'.format(
            settings.COURSE_ID_PATTERN,
        ),
        instructor_dashboard_views.set_course_mode_price,
        name='set_course_mode_price',
    ),
    url(
        r'^courses/{}/remove_coupon$'.format(
            settings.COURSE_ID_PATTERN,
        ),
        instructor_coupons_views.remove_coupon,
        name='remove_coupon',
    ),
    url(
        r'^courses/{}/add_coupon$'.format(
            settings.COURSE_ID_PATTERN,
        ),
        instructor_coupons_views.add_coupon,
        name='add_coupon',
    ),
    url(
        r'^courses/{}/update_coupon$'.format(
            settings.COURSE_ID_PATTERN,
        ),
        instructor_coupons_views.update_coupon,
        name='update_coupon',
    ),
    url(
        r'^courses/{}/get_coupon_info$'.format(
            settings.COURSE_ID_PATTERN,
        ),
        instructor_coupons_views.get_coupon_info,
        name='get_coupon_info',
    ),

    url(
        r'^courses/{}/'.format(
            settings.COURSE_ID_PATTERN,
        ),
        include(COURSE_URLS)
    ),
    # url(
    #     r'^course/{}/search_reindex?$'.format(
    #         settings.COURSE_KEY_PATTERN),
    #     'course_search_index_handler',
    #     name='course_search_index_handler'
    # ),
    # Discussions Management
    url(
        r'^courses/{}/discussions/settings$'.format(
            settings.COURSE_KEY_PATTERN,
        ),
        discussion_views.course_discussions_settings_handler,
        name='course_discussions_settings',
    ),

    # Cohorts management
    url(
        r'^courses/{}/cohorts/settings$'.format(
            settings.COURSE_KEY_PATTERN,
        ),
        course_groups_views.course_cohort_settings_handler,
        name='course_cohort_settings',
    ),
    url(
        r'^courses/{}/cohorts/(?P<cohort_id>[0-9]+)?$'.format(
            settings.COURSE_KEY_PATTERN,
        ),
        course_groups_views.cohort_handler,
        name='cohorts',
    ),
    url(
        r'^courses/{}/cohorts/(?P<cohort_id>[0-9]+)$'.format(
            settings.COURSE_KEY_PATTERN,
        ),
        course_groups_views.users_in_cohort,
        name='list_cohort',
    ),
    url(
        r'^courses/{}/cohorts/(?P<cohort_id>[0-9]+)/add$'.format(
            settings.COURSE_KEY_PATTERN,
        ),
        course_groups_views.add_users_to_cohort,
        name='add_to_cohort',
    ),
    url(
        r'^courses/{}/cohorts/(?P<cohort_id>[0-9]+)/delete$'.format(
            settings.COURSE_KEY_PATTERN,
        ),
        course_groups_views.remove_user_from_cohort,
        name='remove_from_cohort',
    ),
    url(
        r'^courses/{}/cohorts/debug$'.format(
            settings.COURSE_KEY_PATTERN,
        ),
        course_groups_views.debug_cohort_mgmt,
        name='debug_cohort_mgmt',
    ),
    url(
        r'^courses/{}/discussion/topics$'.format(
            settings.COURSE_KEY_PATTERN,
        ),
        discussion_views.discussion_topics,
        name='discussion_topics',
    ),
    url(
        r'^courses/{}/verified_track_content/settings'.format(
            settings.COURSE_KEY_PATTERN,
        ),
        verified_track_content_views.cohorting_settings,
        name='verified_track_cohorting',
    ),
    url(
        r'^courses/{}/notes$'.format(
            settings.COURSE_ID_PATTERN,
        ),
        notes_views.notes,
        name='notes',
    ),
    url(
        r'^courses/{}/notes/'.format(
            settings.COURSE_ID_PATTERN,
        ),
        include('notes.urls')
    ),

    # LTI endpoints listing
    url(
        r'^courses/{}/lti_rest_endpoints/'.format(
            settings.COURSE_ID_PATTERN,
        ),
        courseware_views.get_course_lti_endpoints,
        name='lti_rest_endpoints',
    ),

    # Student account
    url(
        r'^account/',
        include('student_account.urls')
    ),

    # Student Notes
    url(
        r'^courses/{}/edxnotes/'.format(
            settings.COURSE_ID_PATTERN,
        ),
        include('edxnotes.urls'),
        name='edxnotes_endpoints',
    ),

    # Student Notes API
    url(
        r'^api/edxnotes/v1/',
        include('edxnotes.api_urls'),
    ),

    # Branding API
    url(
        r'^api/branding/v1/',
        include('branding.api_urls')
    ),

    # Course experience
    url(
        r'^courses/{}/course/'.format(
            settings.COURSE_ID_PATTERN,
        ),
        include('openedx.features.course_experience.urls'),
    ),

    # Course bookmarks UI in LMS
    url(
        r'^courses/{}/bookmarks/'.format(
            settings.COURSE_ID_PATTERN,
        ),
        include('openedx.features.course_bookmarks.urls'),
    ),

    # Course search
    url(
        r'^courses/{}/search/'.format(
            settings.COURSE_ID_PATTERN,
        ),
        include('openedx.features.course_search.urls'),
    ),

    # Learner profile
    url(
        r'^u/',
        include('openedx.features.learner_profile.urls'),
    ),

    # Learner analytics dashboard
    url(
        r'^courses/{}/learner_analytics/'.format(
            settings.COURSE_ID_PATTERN,
        ),
        include('openedx.features.learner_analytics.urls'),
    ),

    # Portfolio project experiment
    url(
        r'^courses/{}/xfeature/portfolio/'.format(
            settings.COURSE_ID_PATTERN,
        ),
        include('openedx.features.portfolio_project.urls'),
    ),
]
if settings.FEATURES.get('ENABLE_TEAMS'):
    # Teams endpoints
    urlpatterns += [
        url(
            r'^api/team/',
            include('lms.djangoapps.teams.api_urls')
        ),
        url(
            r'^courses/{}/teams/'.format(
                settings.COURSE_ID_PATTERN,
            ),
            include('lms.djangoapps.teams.urls'),
            name='teams_endpoints',
        ),
    ]

# allow course staff to change to student view of courseware
if settings.FEATURES.get('ENABLE_MASQUERADE'):
    urlpatterns += [
        url(
            r'^courses/{}/masquerade$'.format(
                settings.COURSE_KEY_PATTERN,
            ),
            courseware_masquerade_handle_ajax,
            name='masquerade_update',
        ),
    ]

urlpatterns += [
    url(
        r'^courses/{}/generate_user_cert'.format(
            settings.COURSE_ID_PATTERN,
        ),
        courseware_views.generate_user_cert,
        name='generate_user_cert',
    ),
]

# discussion forums live within courseware, so courseware must be enabled first
if settings.FEATURES.get('ENABLE_DISCUSSION_SERVICE'):
    urlpatterns += [
        url(
            r'^api/discussion/',
            include('discussion_api.urls')
        ),
        url(
            r'^courses/{}/discussion/'.format(
                settings.COURSE_ID_PATTERN,
            ),
            include('django_comment_client.urls')
        ),
        url(
            r'^notification_prefs/enable/',
            notification_prefs_views.ajax_enable
        ),
        url(
            r'^notification_prefs/disable/',
            notification_prefs_views.ajax_disable
        ),
        url(
            r'^notification_prefs/status/',
            notification_prefs_views.ajax_status
        ),
        url(
            r'^notification_prefs/unsubscribe/(?P<token>[a-zA-Z0-9-_=]+)/',
            notification_prefs_views.set_subscription,
            {
                'subscribe': False,
            },
            name='unsubscribe_forum_update',
        ),
        url(
            r'^notification_prefs/resubscribe/(?P<token>[a-zA-Z0-9-_=]+)/',
            notification_prefs_views.set_subscription,
            {
                'subscribe': True,
            },
            name='resubscribe_forum_update',
        ),
    ]

urlpatterns += [
    url(
        r'^courses/{}/tab/(?P<tab_type>[^/]+)/$'.format(
            settings.COURSE_ID_PATTERN,
        ),
        CourseTabView.as_view(),
        name='course_tab_view',
    ),
]

urlpatterns += [
    # This MUST be the last view in the courseware--it's a catch-all for custom tabs.
    url(
        r'^courses/{}/(?P<tab_slug>[^/]+)/$'.format(
            settings.COURSE_ID_PATTERN,
        ),
        StaticCourseTabView.as_view(),
        name='static_tab',
    ),
]

if settings.FEATURES.get('ENABLE_STUDENT_HISTORY_VIEW'):
    urlpatterns += [
        url(
            r'^courses/{}/submission_history/(?P<student_username>[^/]*)/(?P<location>.*?)$'.format(
                settings.COURSE_ID_PATTERN
            ),
            courseware_views.submission_history,
            name='submission_history',
        ),
    ]

if settings.FEATURES.get('CLASS_DASHBOARD'):
    urlpatterns += [
        url(r'^class_dashboard/', include('class_dashboard.urls')),
    ]

if settings.DEBUG or settings.FEATURES.get('ENABLE_DJANGO_ADMIN_SITE'):
    # Jasmine and admin
    urlpatterns += [
        url(r'^admin/', include(admin.site.urls)),
    ]

if settings.FEATURES.get('AUTH_USE_OPENID'):
    urlpatterns += [
        url(r'^openid/login/$', django_openid_auth_views.login_begin, name='openid-login'),
        url(
            r'^openid/complete/$',
            external_auth_views.openid_login_complete,
            name='openid-complete',
        ),
        url(r'^openid/logo.gif$', django_openid_auth_views.logo, name='openid-logo'),
    ]

if settings.FEATURES.get('AUTH_USE_SHIB'):
    urlpatterns += [
        url(r'^shib-login/$', external_auth_views.shib_login, name='shib-login'),
    ]

if settings.FEATURES.get('AUTH_USE_CAS'):
    from django_cas import views as django_cas_views

    urlpatterns += [
        url(r'^cas-auth/login/$', external_auth_views.cas_login, name='cas-login'),
        url(r'^cas-auth/logout/$', django_cas_views.logout, {'next_page': '/'}, name='cas-logout'),
    ]

if settings.FEATURES.get('RESTRICT_ENROLL_BY_REG_METHOD'):
    urlpatterns += [
        url(r'^course_specific_login/{}/$'.format(settings.COURSE_ID_PATTERN),
            external_auth_views.course_specific_login, name='course-specific-login'),
        url(r'^course_specific_register/{}/$'.format(settings.COURSE_ID_PATTERN),
            external_auth_views.course_specific_register, name='course-specific-register'),
    ]

if configuration_helpers.get_value('ENABLE_BULK_ENROLLMENT_VIEW', settings.FEATURES.get('ENABLE_BULK_ENROLLMENT_VIEW')):
    urlpatterns += [
        url(r'^api/bulk_enroll/v1/', include('bulk_enroll.urls')),
    ]

# Shopping cart
urlpatterns += [
    url(r'^shoppingcart/', include('shoppingcart.urls')),
    url(r'^commerce/', include('lms.djangoapps.commerce.urls', namespace='commerce')),
]

# Course goals
urlpatterns += [
    url(r'^api/course_goals/', include('lms.djangoapps.course_goals.urls', namespace='course_goals_api')),
]

# Embargo
if settings.FEATURES.get('EMBARGO'):
    urlpatterns += [
        url(r'^embargo/', include('openedx.core.djangoapps.embargo.urls', namespace='embargo')),
        url(r'^api/embargo/', include('openedx.core.djangoapps.embargo.urls', namespace='api_embargo')),
    ]

# Survey Djangoapp
urlpatterns += [
    url(r'^survey/', include('survey.urls')),
]

if settings.FEATURES.get('AUTH_USE_OPENID_PROVIDER'):
    urlpatterns += [
        url(
            r'^openid/provider/login/$',
            external_auth_views.provider_login,
            name='openid-provider-login',
        ),
        url(
            r'^openid/provider/login/(?:.+)$',
            external_auth_views.provider_identity,
            name='openid-provider-login-identity'
        ),
        url(
            r'^openid/provider/identity/$',
            external_auth_views.provider_identity,
            name='openid-provider-identity',
        ),
        url(
            r'^openid/provider/xrds/$',
            external_auth_views.provider_xrds,
            name='openid-provider-xrds',
        ),
    ]

if settings.FEATURES.get('ENABLE_OAUTH2_PROVIDER'):
    urlpatterns += [
        # These URLs dispatch to django-oauth-toolkit or django-oauth2-provider as appropriate.
        # Developers should use these routes, to maintain compatibility for existing client code
        url(r'^oauth2/', include('openedx.core.djangoapps.oauth_dispatch.urls')),
        # These URLs contain the django-oauth2-provider default behavior.  It exists to provide
        # URLs for django-oauth2-provider to call using reverse() with the oauth2 namespace, and
        # also to maintain support for views that have not yet been wrapped in dispatch views.
        url(r'^oauth2/', include('edx_oauth2_provider.urls', namespace='oauth2')),
        # The /_o/ prefix exists to provide a target for code in django-oauth-toolkit that
        # uses reverse() with the 'oauth2_provider' namespace.  Developers should not access these
        # views directly, but should rather use the wrapped views at /oauth2/
        url(r'^_o/', include('oauth2_provider.urls', namespace='oauth2_provider')),
    ]

if settings.FEATURES.get('ENABLE_LMS_MIGRATION'):
    urlpatterns += [
        url(r'^migrate/modules$', lms_migrate_views.manage_modulestores),
        url(r'^migrate/reload/(?P<reload_dir>[^/]+)$', lms_migrate_views.manage_modulestores),
        url(
            r'^migrate/reload/(?P<reload_dir>[^/]+)/(?P<commit_id>[^/]+)$',
            lms_migrate_views.manage_modulestores
        ),
        url(r'^gitreload$', lms_migrate_views.gitreload),
        url(r'^gitreload/(?P<reload_dir>[^/]+)$', lms_migrate_views.gitreload),
    ]

if settings.FEATURES.get('ENABLE_SQL_TRACKING_LOGS'):
    urlpatterns += [
        url(r'^event_logs$', track_views.view_tracking_log),
        url(r'^event_logs/(?P<args>.+)$', track_views.view_tracking_log),
    ]

if settings.FEATURES.get('ENABLE_SERVICE_STATUS'):
    urlpatterns += [
        url(r'^status/', include('openedx.core.djangoapps.service_status.urls')),
    ]

if settings.FEATURES.get('ENABLE_INSTRUCTOR_BACKGROUND_TASKS'):
    urlpatterns += [
        url(
            r'^instructor_task_status/$',
            instructor_task_views.instructor_task_status,
            name='instructor_task_status'
        ),
    ]

if settings.FEATURES.get('RUN_AS_ANALYTICS_SERVER_ENABLED'):
    urlpatterns += [
        url(r'^edinsights_service/', include('edinsights.core.urls')),
    ]

if settings.FEATURES.get('ENABLE_DEBUG_RUN_PYTHON'):
    urlpatterns += [
        url(r'^debug/run_python$', debug_views.run_python),
    ]

urlpatterns += [
    url(r'^debug/show_parameters$', debug_views.show_parameters),
]

# Third-party auth.
if settings.FEATURES.get('ENABLE_THIRD_PARTY_AUTH'):
    urlpatterns += [
        url(r'', include('third_party_auth.urls')),
        url(r'api/third_party_auth/', include('third_party_auth.api.urls')),
        # NOTE: The following login_oauth_token endpoint is DEPRECATED.
        # Please use the exchange_access_token endpoint instead.
        url(r'^login_oauth_token/(?P<backend>[^/]+)/$', student_views.login_oauth_token),
    ]

# Enterprise
if enterprise_enabled():
    urlpatterns += [
        url(r'', include('enterprise.urls')),
    ]

# OAuth token exchange
if settings.FEATURES.get('ENABLE_OAUTH2_PROVIDER'):
    urlpatterns += [
        url(
            r'^oauth2/login/$',
            LoginWithAccessTokenView.as_view(),
            name='login_with_access_token'
        ),
    ]

# Certificates
urlpatterns += [
    url(r'^certificates/', include('certificates.urls')),

    # Backwards compatibility with XQueue, which uses URLs that are not prefixed with /certificates/
    url(r'^update_certificate$', certificates_views.update_certificate, name='update_certificate'),
    url(r'^update_example_certificate$', certificates_views.update_example_certificate,
        name='update_example_certificate'),
    url(r'^request_certificate$', certificates_views.request_certificate,
        name='request_certificate'),

    # REST APIs
    url(r'^api/certificates/',
        include('lms.djangoapps.certificates.apis.urls', namespace='certificates_api')),
]

# XDomain proxy
urlpatterns += [
    url(r'^xdomain_proxy.html$', cors_csrf_views.xdomain_proxy, name='xdomain_proxy'),
]

# Custom courses on edX (CCX) URLs
if settings.FEATURES.get('CUSTOM_COURSES_EDX'):
    urlpatterns += [
        url(r'^courses/{}/'.format(settings.COURSE_ID_PATTERN),
            include('ccx.urls')),
        url(r'^api/ccx/', include('lms.djangoapps.ccx.api.urls', namespace='ccx_api')),
    ]

# Access to courseware as an LTI provider
if settings.FEATURES.get('ENABLE_LTI_PROVIDER'):
    urlpatterns += [
        url(r'^lti_provider/', include('lti_provider.urls')),
    ]

urlpatterns += [
    url(r'config/self_paced', ConfigurationModelCurrentAPIView.as_view(model=SelfPacedConfiguration)),
    url(r'config/programs', ConfigurationModelCurrentAPIView.as_view(model=ProgramsApiConfig)),
    url(r'config/catalog', ConfigurationModelCurrentAPIView.as_view(model=CatalogIntegration)),
    url(r'config/forums', ConfigurationModelCurrentAPIView.as_view(model=ForumsConfig)),
]

if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(
        settings.PROFILE_IMAGE_BACKEND['options']['base_url'],
        document_root=settings.PROFILE_IMAGE_BACKEND['options']['location']
    )

# UX reference templates
urlpatterns += [
    url(r'^template/(?P<template>.+)$', openedx_debug_views.show_reference_template),
]

if 'debug_toolbar' in settings.INSTALLED_APPS:
    import debug_toolbar

    urlpatterns += [
        url(r'^__debug__/', include(debug_toolbar.urls)),
    ]

# Custom error pages
# These are used by Django to render these error codes. Do not remove.
# pylint: disable=invalid-name
handler404 = static_template_view_views.render_404
handler500 = static_template_view_views.render_500

# include into our URL patterns the HTTP REST API that comes with edx-proctoring.
urlpatterns += [
    url(r'^api/', include('edx_proctoring.urls')),
]

if settings.FEATURES.get('ENABLE_FINANCIAL_ASSISTANCE_FORM'):
    urlpatterns += [
        url(
            r'^financial-assistance/$',
            courseware_views.financial_assistance,
            name='financial_assistance'
        ),
        url(
            r'^financial-assistance/apply/$',
            courseware_views.financial_assistance_form,
            name='financial_assistance_form'
        ),
        url(
            r'^financial-assistance/submit/$',
            courseware_views.financial_assistance_request,
            name='submit_financial_assistance_request'
        )
    ]

# Branch.io Text Me The App
if settings.BRANCH_IO_KEY:
    urlpatterns += [
        url(r'^text-me-the-app', student_views.text_me_the_app, name='text_me_the_app'),
    ]

if settings.FEATURES.get('ENABLE_API_DOCS'):
    urlpatterns += [
        url(r'^api-docs/$', get_swagger_view(title='LMS API')),
    ]

urlpatterns.extend(plugin_urls.get_patterns(plugin_constants.ProjectType.LMS))

# markany
urlpatterns += (
    url(r'^maeps/', include('maeps.urls')),
)
