# -*- coding: utf-8 -*-
"""
Declaration of CourseOverview model
"""
import json
import logging
from urlparse import urlparse, urlunparse

from django.conf import settings
from django.db import models, transaction
from django.db.models.fields import BooleanField, DateTimeField, DecimalField, TextField, FloatField, IntegerField
from django.db.utils import IntegrityError
from django.template import defaultfilters

from ccx_keys.locator import CCXLocator
from model_utils.models import TimeStampedModel
from opaque_keys.edx.django.models import CourseKeyField, UsageKeyField
from six import text_type

from config_models.models import ConfigurationModel
from lms.djangoapps import django_comment_client
from openedx.core.djangoapps.catalog.models import CatalogIntegration
from openedx.core.djangoapps.lang_pref.api import get_closest_released_language
from openedx.core.djangoapps.models.course_details import CourseDetails
from static_replace.models import AssetBaseUrlConfig
from xmodule import course_metadata_utils, block_metadata_utils
from xmodule.course_module import CourseDescriptor, DEFAULT_START_DATE
from xmodule.error_module import ErrorDescriptor
from xmodule.modulestore.django import modulestore

from util.date_utils import strftime_localized
from pytz import utc
from django.utils.translation import ugettext
from django.db.models import F, Q, Value as V, Count
from django.db.models.functions import Coalesce

import datetime
import pytz
from django.utils import timezone
import time

log = logging.getLogger(__name__)


class CourseOverview(TimeStampedModel):
    """
    Model for storing and caching basic information about a course.

    This model contains basic course metadata such as an ID, display name,
    image URL, and any other information that would be necessary to display
    a course as part of:
        user dashboard (enrolled courses)
        course catalog (courses to enroll in)
        course about (meta data about the course)
    """

    class Meta(object):
        app_label = 'course_overviews'

    # classfy = None

    # IMPORTANT: Bump this whenever you modify this model and/or add a migration.
    VERSION = 6

    # Cache entry versioning.
    version = IntegerField()

    # Course identification
    id = CourseKeyField(db_index=True, primary_key=True, max_length=255)
    _location = UsageKeyField(max_length=255)
    org = TextField(max_length=255, default='outdated_entry')
    display_name = TextField(null=True)
    display_number_with_default = TextField()
    display_org_with_default = TextField()

    # Start/end dates
    start = DateTimeField(null=True)
    end = DateTimeField(null=True)
    advertised_start = TextField(null=True)
    announcement = DateTimeField(null=True)

    # URLs
    course_image_url = TextField()
    social_sharing_url = TextField(null=True)
    end_of_course_survey_url = TextField(null=True)

    # Certification data
    certificates_display_behavior = TextField(null=True)
    certificates_show_before_end = BooleanField(default=False)
    cert_html_view_enabled = BooleanField(default=False)
    has_any_active_web_certificate = BooleanField(default=False)
    cert_name_short = TextField()
    cert_name_long = TextField()
    certificate_available_date = DateTimeField(default=None, null=True)

    # Grading
    lowest_passing_grade = DecimalField(max_digits=5, decimal_places=2, null=True)

    # Access parameters
    days_early_for_beta = FloatField(null=True)
    mobile_available = BooleanField(default=False)
    visible_to_staff_only = BooleanField(default=False)
    _pre_requisite_courses_json = TextField()  # JSON representation of list of CourseKey strings

    # Enrollment details
    enrollment_start = DateTimeField(null=True)
    enrollment_end = DateTimeField(null=True)
    enrollment_domain = TextField(null=True)
    invitation_only = BooleanField(default=False)
    max_student_enrollments_allowed = IntegerField(null=True)

    # Catalog information
    catalog_visibility = TextField(null=True)
    short_description = TextField(null=True)
    course_video_url = TextField(null=True)
    effort = TextField(null=True)
    self_paced = BooleanField(default=False)
    marketing_url = TextField(null=True)
    eligible_for_financial_aid = BooleanField(default=True)

    language = TextField(null=True)

    @classmethod
    def _create_or_update(cls, course):
        """
        Creates or updates a CourseOverview object from a CourseDescriptor.

        Does not touch the database, simply constructs and returns an overview
        from the given course.

        Arguments:
            course (CourseDescriptor): any course descriptor object

        Returns:
            CourseOverview: created or updated overview extracted from the given course
        """
        from lms.djangoapps.certificates.api import get_active_web_certificate
        from openedx.core.lib.courses import course_image_url

        # Workaround for a problem discovered in https://openedx.atlassian.net/browse/TNL-2806.
        # If the course has a malformed grading policy such that
        # course._grading_policy['GRADE_CUTOFFS'] = {}, then
        # course.lowest_passing_grade will raise a ValueError.
        # Work around this for now by defaulting to None.
        try:
            lowest_passing_grade = course.lowest_passing_grade
        except ValueError:
            lowest_passing_grade = None

        display_name = course.display_name
        start = course.start
        end = course.end
        max_student_enrollments_allowed = course.max_student_enrollments_allowed
        if isinstance(course.id, CCXLocator):
            from lms.djangoapps.ccx.utils import get_ccx_from_ccx_locator
            ccx = get_ccx_from_ccx_locator(course.id)
            display_name = ccx.display_name
            start = ccx.start
            end = ccx.due
            max_student_enrollments_allowed = ccx.max_student_enrollments_allowed

        course_overview = cls.objects.filter(id=course.id)
        if course_overview.exists():
            log.debug('Updating course overview for %s.', unicode(course.id))
            course_overview = course_overview.first()
        else:
            log.debug('Creating course overview for %s.', unicode(course.id))
            course_overview = cls()

        course_overview.version = cls.VERSION
        course_overview.id = course.id
        course_overview._location = course.location
        course_overview.org = course.location.org
        course_overview.display_name = display_name
        course_overview.display_number_with_default = course.display_number_with_default
        course_overview.display_org_with_default = course.display_org_with_default

        course_overview.start = start
        course_overview.end = end
        course_overview.advertised_start = course.advertised_start
        course_overview.announcement = course.announcement

        course_overview.course_image_url = course_image_url(course)
        course_overview.social_sharing_url = course.social_sharing_url

        course_overview.certificates_display_behavior = course.certificates_display_behavior
        course_overview.certificates_show_before_end = course.certificates_show_before_end
        course_overview.cert_html_view_enabled = course.cert_html_view_enabled
        course_overview.has_any_active_web_certificate = (get_active_web_certificate(course) is not None)
        course_overview.cert_name_short = course.cert_name_short
        course_overview.cert_name_long = course.cert_name_long
        course_overview.certificate_available_date = course.certificate_available_date
        course_overview.lowest_passing_grade = lowest_passing_grade
        course_overview.end_of_course_survey_url = course.end_of_course_survey_url

        course_overview.days_early_for_beta = course.days_early_for_beta
        course_overview.mobile_available = course.mobile_available
        course_overview.visible_to_staff_only = course.visible_to_staff_only
        course_overview._pre_requisite_courses_json = json.dumps(course.pre_requisite_courses)

        course_overview.enrollment_start = course.enrollment_start
        course_overview.enrollment_end = course.enrollment_end
        course_overview.enrollment_domain = course.enrollment_domain
        course_overview.invitation_only = course.invitation_only
        course_overview.max_student_enrollments_allowed = max_student_enrollments_allowed

        course_overview.catalog_visibility = course.catalog_visibility
        course_overview.short_description = CourseDetails.fetch_about_attribute(course.id, 'short_description')
        course_overview.effort = CourseDetails.fetch_about_attribute(course.id, 'effort')
        course_overview.course_video_url = CourseDetails.fetch_video_url(course.id)
        course_overview.self_paced = course.self_paced

        if not CatalogIntegration.is_enabled():
            course_overview.language = course.language

        return course_overview

    @classmethod
    def load_from_module_store(cls, course_id):
        """
        Load a CourseDescriptor, create or update a CourseOverview from it, cache the
        overview, and return it.

        Arguments:
            course_id (CourseKey): the ID of the course overview to be loaded.

        Returns:
            CourseOverview: overview of the requested course.

        Raises:
            - CourseOverview.DoesNotExist if the course specified by course_id
                was not found.
            - IOError if some other error occurs while trying to load the
                course from the module store.
        """
        store = modulestore()
        with store.bulk_operations(course_id):
            course = store.get_course(course_id)
            if isinstance(course, CourseDescriptor):
                course_overview = cls._create_or_update(course)
                try:
                    with transaction.atomic():
                        course_overview.save()
                        # Remove and recreate all the course tabs
                        CourseOverviewTab.objects.filter(course_overview=course_overview).delete()
                        CourseOverviewTab.objects.bulk_create([
                            CourseOverviewTab(tab_id=tab.tab_id, course_overview=course_overview)
                            for tab in course.tabs
                        ])
                        # Remove and recreate course images
                        CourseOverviewImageSet.objects.filter(course_overview=course_overview).delete()
                        CourseOverviewImageSet.create(course_overview, course)

                except IntegrityError:
                    # There is a rare race condition that will occur if
                    # CourseOverview.get_from_id is called while a
                    # another identical overview is already in the process
                    # of being created.
                    # One of the overviews will be saved normally, while the
                    # other one will cause an IntegrityError because it tries
                    # to save a duplicate.
                    # (see: https://openedx.atlassian.net/browse/TNL-2854).
                    pass
                except Exception:  # pylint: disable=broad-except
                    log.exception(
                        "CourseOverview for course %s failed!",
                        course_id,
                    )
                    raise

                return course_overview
            elif course is not None:
                raise IOError(
                    "Error while loading course {} from the module store: {}",
                    unicode(course_id),
                    course.error_msg if isinstance(course, ErrorDescriptor) else unicode(course)
                )
            else:
                raise cls.DoesNotExist()

    @classmethod
    def get_from_id(cls, course_id):

        start = time.time()

        log.debug('***** def get_from_id time check1 [%s]' % format(time.time() - start, ".6f"))

        """
        Load a CourseOverview object for a given course ID.

        First, we try to load the CourseOverview from the database. If it
        doesn't exist, we load the entire course from the modulestore, create a
        CourseOverview object from it, and then cache it in the database for
        future use.

        Arguments:
            course_id (CourseKey): the ID of the course overview to be loaded.

        Returns:
            CourseOverview: overview of the requested course.

        Raises:
            - CourseOverview.DoesNotExist if the course specified by course_id
                was not found.
            - IOError if some other error occurs while trying to load the
                course from the module store.
        """
        try:
            course_overview = cls.objects.select_related('image_set').get(id=course_id)
            if course_overview.version < cls.VERSION:
                # Throw away old versions of CourseOverview, as they might contain stale data.
                course_overview.delete()
                course_overview = None
        except cls.DoesNotExist:
            course_overview = None

        log.debug('***** def get_from_id time check2 [%s]' % format(time.time() - start, ".6f"))

        # Regenerate the thumbnail images if they're missing (either because
        # they were never generated, or because they were flushed out after
        # a change to CourseOverviewImageConfig.
        if course_overview and not hasattr(course_overview, 'image_set'):
            CourseOverviewImageSet.create(course_overview)

        log.debug('***** def get_from_id time check3 [%s]' % format(time.time() - start, ".6f"))

        if course_overview:

            try:

                log.debug('***** def get_from_id time check4 [%s]' % format(time.time() - start, ".6f"))
                from courseware.models import CourseOverviewAddinfo, CodeDetail
                addinfo = CourseOverviewAddinfo.objects.get(course_id=course_overview.id)

                course_overview.teachers = addinfo.teacher_name
                course_overview.classfy = addinfo.classfy
                course_overview.classfy_plus = addinfo.classfy_plus
                course_overview.middle_classfy = addinfo.middle_classfy
                course_overview.preview_video = addinfo.preview_video
                course_overview.course_period = addinfo.course_period
                course_overview.level = addinfo.course_level
                course_overview.passing_grade = course_overview.lowest_passing_grade
                course_overview.audit_yn = addinfo.audit_yn
                course_overview.fourth_industry_yn = addinfo.fourth_industry_yn
                course_overview.home_course_yn = addinfo.home_course_yn
                course_overview.home_course_step = addinfo.home_course_step
                course_overview.ribbon_yn = addinfo.ribbon_yn
                course_overview.ribbon_year = addinfo.ribbon_year
                course_overview.job_edu_yn = addinfo.job_edu_yn
                course_overview.ai_sec_yn = addinfo.ai_sec_yn
                course_overview.basic_science_sec_yn = addinfo.basic_science_sec_yn
                course_overview.linguistics = addinfo.linguistics
                course_overview.liberal_arts_yn = addinfo.liberal_arts_yn
                course_overview.liberal_arts = addinfo.liberal_arts
                course_overview.career_readiness_competencies_yn = addinfo.career_readiness_competencies_yn
                course_overview.classfy_name = CodeDetail.objects.get(group_code='001', detail_code=addinfo.classfy).detail_name
                course_overview.middle_classfy_name = CodeDetail.objects.get(group_code='002', detail_code=addinfo.middle_classfy).detail_name
                course_overview.org_name = CodeDetail.objects.get(group_code='003', detail_code=course_overview.org).detail_name
                course_overview.language_name = '한국어' if course_overview.language == 'ko' else \
                    '영어' if course_overview.language == 'en' else \
                        '일본어' if course_overview.language == 'ja' else \
                            '프랑스어' if course_overview.language == 'fr' else \
                                course_overview.language
                course_overview.effort_time = str(course_overview.effort)[0:5]
                course_overview.week = str(course_overview.effort)[6:8]
                course_overview.video_time = str(course_overview.effort)[9:14]
                course_overview.learning_time = str(course_overview.effort)[15:]
                course_overview.preview_video = addinfo.preview_video
                course_overview.matchup_yn = addinfo.matchup_yn

                log.debug('***** def get_from_id time check5 [%s]' % format(time.time() - start, ".6f"))
            except Exception as e:
                course_overview.teachers = ''
                course_overview.classfy = ''
                course_overview.middle_classfy = ''
                course_overview.course_period = ''
                course_overview.level = ''
                course_overview.audit_yn = ''
                course_overview.fourth_industry_yn = ''
                course_overview.home_course_yn = ''
                course_overview.home_course_step = ''
                course_overview.ribbon_yn = ''
                course_overview.ribbon_year = ''
                course_overview.job_edu_yn = ''
                course_overview.linguistics = ''
                course_overview.liberal_arts_yn = ''
                course_overview.liberal_arts = ''
                course_overview.career_readiness_competencies_yn = ''
                course_overview.classfy_name = ''
                course_overview.classfy_plus = ''
                course_overview.preview_video = ''
                course_overview.middle_classfy_name = ''
                course_overview.org_name = ''
                course_overview.language_name = ''
                course_overview.effort_time = ''
                course_overview.week = ''
                course_overview.video_time = ''
                course_overview.learning_time = ''
                course_overview.ai_sec_yn = ''
                course_overview.basic_science_sec_yn = ''
                course_overview.preview_video = ''
                course_overview.matchup_yn = ''

                log.debug('CourseOverview get_from_id e.message [%s]' % e.message)

        log.debug('***** def get_from_id get_from_id check6 [%s]' % format(time.time() - start, ".6f"))

        return course_overview or cls.load_from_module_store(course_id)

    @classmethod
    def get_from_ids_if_exists(cls, course_ids):
        """
        Return a dict mapping course_ids to CourseOverviews, if they exist.

        This method will *not* generate new CourseOverviews or delete outdated
        ones. It exists only as a small optimization used when CourseOverviews
        are known to exist, for common situations like the student dashboard.

        Callers should assume that this list is incomplete and fall back to
        get_from_id if they need to guarantee CourseOverview generation.
        """
        return {
            overview.id: overview
            for overview
            in cls.objects.select_related('image_set').filter(
            id__in=course_ids,
            version__gte=cls.VERSION
        )
        }

    @classmethod
    def get_from_id_if_exists(cls, course_id):
        """
        Return a CourseOverview for the provided course_id if it exists.
        Returns None if no CourseOverview exists with the provided course_id

        This method will *not* generate new CourseOverviews or delete outdated
        ones. It exists only as a small optimization used when CourseOverviews
        are known to exist, for common situations like the student dashboard.

        Callers should assume that this list is incomplete and fall back to
        get_from_id if they need to guarantee CourseOverview generation.
        """
        try:
            course_overview = cls.objects.select_related('image_set').get(
                id=course_id,
                version__gte=cls.VERSION
            )
        except cls.DoesNotExist:
            course_overview = None

        return course_overview

    def clean_id(self, padding_char='='):
        """
        Returns a unique deterministic base32-encoded ID for the course.

        Arguments:
            padding_char (str): Character used for padding at end of base-32
                                -encoded string, defaulting to '='
        """
        return course_metadata_utils.clean_course_key(self.location.course_key, padding_char)

    @property
    def location(self):
        """
        Returns the UsageKey of this course.

        UsageKeyField has a strange behavior where it fails to parse the "run"
        of a course out of the serialized form of a Mongo Draft UsageKey. This
        method is a wrapper around _location attribute that fixes the problem
        by calling map_into_course, which restores the run attribute.
        """
        if self._location.run is None:
            self._location = self._location.map_into_course(self.id)
        return self._location

    @property
    def number(self):
        """
        Returns this course's number.

        This is a "number" in the sense of the "course numbers" that you see at
        lots of universities. For example, given a course
        "Intro to Computer Science" with the course key "edX/CS-101/2014", the
        course number would be "CS-101"
        """
        return course_metadata_utils.number_for_course_location(self.location)

    @property
    def url_name(self):
        """
        Returns this course's URL name.
        """
        return block_metadata_utils.url_name_for_block(self)

    @property
    def display_name_with_default(self):
        """
        Return reasonable display name for the course.
        """
        return block_metadata_utils.display_name_with_default(self)

    @property
    def display_name_with_default_escaped(self):
        """
        DEPRECATED: use display_name_with_default

        Return html escaped reasonable display name for the course.

        Note: This newly introduced method should not be used.  It was only
        introduced to enable a quick search/replace and the ability to slowly
        migrate and test switching to display_name_with_default, which is no
        longer escaped.
        """
        return block_metadata_utils.display_name_with_default_escaped(self)

    @property
    def dashboard_start_display(self):
        """
         Return start date to diplay on learner's dashboard, preferably `Course Advertised Start`
        """
        return self.advertised_start or self.start

    def has_started(self):
        """
        Returns whether the the course has started.
        """
        return course_metadata_utils.has_course_started(self.start)

    def has_ended(self):
        """
        Returns whether the course has ended.
        """
        return course_metadata_utils.has_course_ended(self.end)

    def has_marketing_url(self):
        """
        Returns whether the course has marketing url.
        """
        return settings.FEATURES.get('ENABLE_MKTG_SITE') and bool(self.marketing_url)

    def has_social_sharing_url(self):
        """
        Returns whether the course has social sharing url.
        """
        is_social_sharing_enabled = getattr(settings, 'SOCIAL_SHARING_SETTINGS', {}).get('CUSTOM_COURSE_URLS')
        return is_social_sharing_enabled and bool(self.social_sharing_url)

    def starts_within(self, days):
        """
        Returns True if the course starts with-in given number of days otherwise returns False.
        """
        return course_metadata_utils.course_starts_within(self.start, days)

    def start_datetime_text(self, format_string="SHORT_DATE", time_zone=utc):
        """
        Returns the desired text corresponding to the course's start date and
        time in the specified time zone, or utc if no time zone given.
        Prefers .advertised_start, then falls back to .start.
        """
        return course_metadata_utils.course_start_datetime_text(
            self.start,
            self.advertised_start,
            format_string,
            time_zone,
            ugettext,
            strftime_localized
        )

    @property
    def start_date_is_still_default(self):
        """
        Checks if the start date set for the course is still default, i.e.
        .start has not been modified, and .advertised_start has not been set.
        """
        return course_metadata_utils.course_start_date_is_default(
            self.start,
            self.advertised_start,
        )

    @property
    def sorting_score(self):
        """
        Returns a tuple that can be used to sort the courses according
        the how "new" they are. The "newness" score is computed using a
        heuristic that takes into account the announcement and
        (advertised) start dates of the course if available.

        The lower the number the "newer" the course.
        """
        return course_metadata_utils.sorting_score(self.start, self.advertised_start, self.announcement)

    @property
    def start_type(self):
        """
        Returns the type of the course's 'start' field.
        """
        if self.advertised_start:
            return u'string'
        elif self.start != DEFAULT_START_DATE:
            return u'timestamp'
        else:
            return u'empty'

    @property
    def start_display(self):
        """
        Returns the display value for the course's start date.
        """
        if self.advertised_start:
            return self.advertised_start
        elif self.start != DEFAULT_START_DATE:
            return defaultfilters.date(self.start, "DATE_FORMAT")
        else:
            return None

    def may_certify(self):
        """
        Returns whether it is acceptable to show the student a certificate
        download link.
        """
        return course_metadata_utils.may_certify_for_course(
            self.certificates_display_behavior,
            self.certificates_show_before_end,
            self.has_ended(),
            self.certificate_available_date,
            self.self_paced
        )

    @property
    def pre_requisite_courses(self):
        """
        Returns a list of ID strings for this course's prerequisite courses.
        """
        return json.loads(self._pre_requisite_courses_json)

    @pre_requisite_courses.setter
    def pre_requisite_courses(self, value):
        """
        Django requires there be a setter for this, but it is not
        necessary for the way we currently use it. Due to the way
        CourseOverviews are constructed raising errors here will
        cause a lot of issues. These should not be mutable after
        construction, so for now we just eat this.
        """
        pass

    @classmethod
    def update_select_courses(cls, course_keys, force_update=False):
        """
        A side-effecting method that updates CourseOverview objects for
        the given course_keys.

        Arguments:
            course_keys (list[CourseKey]): Identifies for which courses to
                return CourseOverview objects.
            force_update (boolean): Optional parameter that indicates
                whether the requested CourseOverview objects should be
                forcefully updated (i.e., re-synched with the modulestore).
        """
        log.debug('Generating course overview for %d courses.', len(course_keys))
        log.debug('Generating course overview(s) for the following courses: %s', course_keys)

        action = CourseOverview.load_from_module_store if force_update else CourseOverview.get_from_id

        for course_key in course_keys:
            try:
                action(course_key)
            except Exception as ex:  # pylint: disable=broad-except
                log.exception(
                    'An error occurred while generating course overview for %s: %s',
                    unicode(course_key),
                    text_type(ex),
                )

        log.debug('Finished generating course overviews.')

    @classmethod
    def get_all_courses(cls, org=None, filter_=None):
        """
        Returns all CourseOverview objects in the database.

        Arguments:
            orgs (list[string]): Optional parameter that allows case-insensitive
                filtering by organization.
            filter_ (dict): Optional parameter that allows custom filtering.
        """
        # Note: If a newly created course is not returned in this QueryList,
        # make sure the "publish" signal was emitted when the course was
        # created. For tests using CourseFactory, use emit_signals=True.

        # global variables
        order = '-enrollment_start', '-start', '-enrollment_end', '-end', 'display_name'
        utcnow = timezone.now()
        is_api = False

        if filter_ and 'is_api' in filter_:
            is_api = filter_.get('is_api')
            filter_.pop('is_api')

        log.debug('is_api = %s' % is_api)

        if is_api:
            if not filter_:
                filter_ = {}

            if org:
                filter_.update(org=org)

            course_overviews = CourseOverview \
                .objects \
                .filter(**filter_) \
                .filter(visible_to_staff_only=False, catalog_visibility='both') \
                .filter(Q(enrollment_end__isnull=True) | Q(start__lt=utcnow) | Q(enrollment_start__lte=utcnow, enrollment_end__gte=utcnow))

        elif org:
            if org == 'ACEk':
                org = org.replace('k', '')
                if filter_:
                    course_overviews = CourseOverview.objects.filter(Q(id__icontains='%s.' % org) | Q(id__icontains='%s_' % org) | Q(id__icontains='FA.HGU01')).filter(**filter_).order_by(*order)
                else:
                    course_overviews = CourseOverview.objects.filter(Q(id__icontains='%s.' % org) | Q(id__icontains='%s_' % org) | Q(id__icontains='FA.HGU01')).order_by(*order)

            elif org == 'COREk':
                org = org.replace('k', '')
                if filter_:
                    course_overviews = CourseOverview.objects.filter(
                        Q(id__icontains='%s.' % org) | Q(id__icontains='%s_' % org) | Q(id__icontains='SKKU_COS2021.01K') | Q(id__icontains='SKKU_COS2022.01K') | Q(
                            id__icontains='SKKU_NTST100.01K') | Q(id__icontains='HYUKMOOC2016-4k') | Q(
                            id__icontains='HYUKMOOC2016-5k')).filter(**filter_).order_by(*order)
                else:
                    course_overviews = CourseOverview.objects.filter(
                        Q(id__icontains='%s.' % org) | Q(id__icontains='%s_' % org) | Q(id__icontains='SKKU_COS2021.01K') | Q(id__icontains='SKKU_COS2022.01K') | Q(
                            id__icontains='SKKU_NTST100.01K') | Q(id__icontains='HYUKMOOC2016-4k') | Q(
                            id__icontains='HYUKMOOC2016-5k')).order_by(*order)

            elif org == 'CKk' or org == 'KOCWk':
                org = org.replace('k', '')
                if filter_:
                    course_overviews = CourseOverview.objects.filter(Q(id__icontains='%s.' % org) | Q(id__icontains='%s_' % org)).filter(**filter_).order_by(*order)
                else:
                    course_overviews = CourseOverview.objects.filter(Q(id__icontains='%s.' % org) | Q(id__icontains='%s_' % org)).order_by(*order)

            elif org == 'SNUk' or org == 'POSTECHk' or org == 'KAISTk':
                if filter_:
                    course_overviews = CourseOverview.objects.filter(Q(org__iexact=org) | Q(id__icontains='SKP')).filter(**filter_).order_by(*order)
                else:
                    course_overviews = CourseOverview.objects.filter(Q(org__iexact=org) | Q(id__icontains='SKP')).order_by(*order)
            elif org == 'SMUk':
                if filter_:
                    course_overviews = CourseOverview.objects.filter(Q(org__iexact=org) | Q(id__icontains='SMUCk')).filter(**filter_).order_by(*order)
                else:
                    course_overviews = CourseOverview.objects.filter(Q(org__iexact=org) | Q(id__icontains='SMUCk')).order_by(*order)

            else:
                if filter_:
                    course_overviews = CourseOverview.objects.filter(org__iexact=org).filter(**filter_).order_by(*order)
                else:
                    course_overviews = CourseOverview.objects.filter(org__iexact=org).order_by(*order)

        else:
            if filter_ and 'mobile_available' in filter_ and filter_['mobile_available'] is True:
                course_overviews = CourseOverview.objects.filter(**filter_).order_by(*order)
                course_overviews = [c for c in course_overviews if not c.has_ended() and c.enrollment_start and c.enrollment_end and c.enrollment_start <= utcnow <= c.enrollment_end]
            elif filter_:
                course_overviews = CourseOverview.objects.filter(**filter_)
            else:
                course_overviews = CourseOverview.objects.all().order_by(*order)

        # 표시 항목 추가 (ORM)
        course_overviews = course_overviews.annotate(
            teachers=Coalesce(F('courseoverviewaddinfo__teacher_name'), V('')),
            classfy=Coalesce(F('courseoverviewaddinfo__classfy'), V('')),
            classfy_plus=Coalesce(F('courseoverviewaddinfo__classfy_plus'), V('')),
            middle_classfy=Coalesce(F('courseoverviewaddinfo__middle_classfy'), V('')),
            course_period=Coalesce(F('courseoverviewaddinfo__course_period'), V('')),
            level=Coalesce(F('courseoverviewaddinfo__course_level'), V('')),
            passing_grade=Coalesce(F('lowest_passing_grade'), V('')),
            audit_yn=Coalesce(F('courseoverviewaddinfo__audit_yn'), V('N')),
            fourth_industry_yn=Coalesce(F('courseoverviewaddinfo__fourth_industry_yn'), V('N')),
            home_course_yn=Coalesce(F('courseoverviewaddinfo__home_course_yn'), V('N')),
            home_course_step=Coalesce(F('courseoverviewaddinfo__home_course_step'), V('')),
            ribbon_yn=Coalesce(F('courseoverviewaddinfo__ribbon_yn'), V('N')),
            ribbon_year=Coalesce(F('courseoverviewaddinfo__ribbon_year'), V('')),
            job_edu_yn=Coalesce(F('courseoverviewaddinfo__job_edu_yn'), V('N')),
            linguistics=Coalesce(F('courseoverviewaddinfo__linguistics'), V('N')),
            liberal_arts_yn=Coalesce(F('courseoverviewaddinfo__liberal_arts_yn'), V('liberal_arts_n')),
            liberal_arts=Coalesce(F('courseoverviewaddinfo__liberal_arts'), V('')),
            career_readiness_competencies_yn=Coalesce(F('courseoverviewaddinfo__career_readiness_competencies_yn'), V('career_readiness_competencies_n')),
            ai_sec_yn=Coalesce(F('courseoverviewaddinfo__ai_sec_yn'), V('N')),
            basic_science_sec_yn=Coalesce(F('courseoverviewaddinfo__basic_science_sec_yn'), V('N')),
            preview_video=Coalesce(F('courseoverviewaddinfo__preview_video'), V('')),
            matchup_yn=Coalesce(F('courseoverviewaddinfo__matchup_yn'), V('matchup_n')),
        )

        # 표시 항목 추가 (EXTRA)
        course_overviews = course_overviews.extra(select={
            "teacher_name": """
                ifnull(CASE
                    WHEN INSTR(teacher_name, ',') = 0 THEN teacher_name
                    ELSE CONCAT(SUBSTRING_INDEX(teacher_name, ',', 1),
                            ' 외 ',
                            LENGTH(teacher_name) - LENGTH(REPLACE(teacher_name, ',', '')),
                            '명')
                END, '')            
            """,
            "org_name": "select detail_name from code_detail where group_code = '003' and detail_code = course_overviews_courseoverview.org",
            "org_kname": "select detail_name from code_detail where group_code = '003' and detail_code = course_overviews_courseoverview.org",
            "org_ename": "select detail_ename from code_detail where group_code = '003' and detail_code = course_overviews_courseoverview.org",
            "classfy_name": """
                select detail_name 
                  from code_detail, course_overview_addinfo 
                 where course_overviews_courseoverview.id = course_overview_addinfo.course_id 
                   and code_detail.group_code = '001' 
                   and code_detail.detail_code = course_overview_addinfo.classfy
            """,
            "middle_classfy_name": """
                select detail_name 
                  from code_detail, course_overview_addinfo 
                 where course_overviews_courseoverview.id = course_overview_addinfo.course_id 
                   and code_detail.group_code = '002' 
                   and code_detail.detail_code = course_overview_addinfo.middle_classfy
            """,
            "language_name": """
                CASE language
                    WHEN 'ko' THEN '한국어'
                    WHEN 'en' THEN '영어'
                    WHEN 'fr' THEN '프랑스어'
                    WHEN 'zh_HANS' THEN '중국어 간체'
                    WHEN 'zh_HANT' THEN '중국어 번체'
                    ELSE language
                END
            """,
            "learning_time": "SUBSTRING_INDEX(effort, '@', 1)",
            "effort_time": "SUBSTRING_INDEX(effort, '$', - 1)",
            "video_time": "substr(effort, instr(effort, '#') + 1, instr(effort, '$') - instr(effort, '#') - 1)",
            "week": "SUBSTR(effort, INSTR(effort, '@') + 1, INSTR(effort, '#') - INSTR(effort, '@') - 1)",
            "status": """
                CASE
                    WHEN UTC_TIMESTAMP < start THEN 'ready'
                    WHEN UTC_TIMESTAMP BETWEEN start AND `end` THEN 'ing'
                    WHEN UTC_TIMESTAMP > `end` THEN 'end'
                    ELSE 'none'
                END
            """,
        })

        # print 'len ------------------------------------------------>', course_overviews.count()
        log.debug(course_overviews.query)

        # log.debug(course_overviews.query)
        return course_overviews

    def start_datetime_text(self, format_string="SHORT_DATE", time_zone=utc):
        """
        Returns the desired text corresponding to the course's start date and
        time in the specified time zone, or utc if no time zone given.
        Prefers .advertised_start, then falls back to .start.
        """
        return course_metadata_utils.course_start_datetime_text(
            self.start,
            self.advertised_start,
            format_string,
            time_zone,
            ugettext,
            strftime_localized
        )

    @classmethod
    def get_all_course_keys(cls):
        """
        Returns all course keys from course overviews.
        """
        return CourseOverview.objects.values_list('id', flat=True)

    def is_discussion_tab_enabled(self):
        """
        Returns True if course has discussion tab and is enabled
        """
        tabs = self.tabs.all()
        # creates circular import; hence explicitly referenced is_discussion_enabled
        for tab in tabs:
            if tab.tab_id == "discussion" and django_comment_client.utils.is_discussion_enabled(self.id):
                return True
        return False

    @property
    def image_urls(self):
        """
        Return a dict with all known URLs for this course image.

        Current resolutions are:
          raw = original upload from the user
          small = thumbnail with dimensions CourseOverviewImageConfig.current().small
          large = thumbnail with dimensions CourseOverviewImageConfig.current().large

        If no thumbnails exist, the raw (originally uploaded) image will be
        returned for all resolutions.
        """
        # This is either the raw image that the course team uploaded, or the
        # settings.DEFAULT_COURSE_ABOUT_IMAGE_URL if they didn't specify one.
        raw_image_url = self.course_image_url

        # Default all sizes to return the raw image if there is no
        # CourseOverviewImageSet associated with this CourseOverview. This can
        # happen because we're disabled via CourseOverviewImageConfig.
        urls = {
            'raw': raw_image_url,
            'small': raw_image_url,
            'large': raw_image_url,
        }

        # If we do have a CourseOverviewImageSet, we still default to the raw
        # images if our thumbnails are blank (might indicate that there was a
        # processing error of some sort while trying to generate thumbnails).
        if hasattr(self, 'image_set') and CourseOverviewImageConfig.current().enabled:
            urls['small'] = self.image_set.small_url or raw_image_url
            urls['large'] = self.image_set.large_url or raw_image_url

        return self.apply_cdn_to_urls(urls)

    @property
    def pacing(self):
        """ Returns the pacing for the course.

        Potential values:
            self: Self-paced courses
            instructor: Instructor-led courses
        """
        return 'self' if self.self_paced else 'instructor'

    @property
    def closest_released_language(self):
        """
        Returns the language code that most closely matches this course' language and is fully
        supported by the LMS, or None if there are no fully supported languages that
        match the target.
        """
        return get_closest_released_language(self.language) if self.language else None

    def apply_cdn_to_urls(self, image_urls):
        """
        Given a dict of resolutions -> urls, return a copy with CDN applied.

        If CDN does not exist or is disabled, just returns the original. The
        URLs that we store in CourseOverviewImageSet are all already top level
        paths, so we don't need to go through the /static remapping magic that
        happens with other course assets. We just need to add the CDN server if
        appropriate.
        """
        cdn_config = AssetBaseUrlConfig.current()
        if not cdn_config.enabled:
            return image_urls

        base_url = cdn_config.base_url

        return {
            resolution: self._apply_cdn_to_url(url, base_url)
            for resolution, url in image_urls.items()
        }

    def _apply_cdn_to_url(self, url, base_url):
        """
        Applies a new CDN/base URL to the given URL.

        If a URL is absolute, we skip switching the host since it could
        be a hostname that isn't behind our CDN, and we could unintentionally
        break the URL overall.
        """

        # The URL can't be empty.
        if not url:
            return url

        _, netloc, path, params, query, fragment = urlparse(url)

        # If this is an absolute URL, just return it as is.  It could be a domain
        # that isn't ours, and thus CDNing it would actually break it.
        if netloc:
            return url

        return urlunparse((None, base_url, path, params, query, fragment))

    def __unicode__(self):
        """Represent ourselves with the course key."""
        return unicode(self.id)


class CourseOverviewTab(models.Model):
    """
    Model for storing and caching tabs information of a course.
    """
    tab_id = models.CharField(max_length=50)
    course_overview = models.ForeignKey(CourseOverview, db_index=True, related_name="tabs", on_delete=models.CASCADE)


class CourseOverviewImageSet(TimeStampedModel):
    """
    Model for Course overview images. Each column is an image type/size.

    You should basically never use this class directly. Read from
    CourseOverview.image_urls instead.

    Special Notes on Deployment/Rollback/Changes:

    1. By default, this functionality is disabled. To turn it on, you have to
       create a CourseOverviewImageConfig entry via Django Admin and select
       enabled=True.

    2. If it is enabled in configuration, it will lazily create thumbnails as
       individual CourseOverviews are requested. This is independent of the
       CourseOverview's cls.VERSION scheme. This is to better support the use
       case where someone might want to change the thumbnail resolutions for
       their theme -- we didn't want to tie the code-based data schema of
       CourseOverview to configuration changes.

    3. A CourseOverviewImageSet is automatically deleted when the CourseOverview
       it belongs to is deleted. So it will be regenerated whenever there's a
       new publish or the CourseOverview schema version changes. It's not
       particularly smart about this, and will just re-write the same thumbnails
       over and over to the same location without checking to see if there were
       changes.

    4. Just because a CourseOverviewImageSet is successfully created does not
       mean that any thumbnails exist. There might have been a processing error,
       or there might simply be no source image to create a thumbnail out of.
       In this case, accessing CourseOverview.image_urls will return the value
       for course.course_image_url for all resolutions. CourseOverviewImageSet
       will *not* try to regenerate if there is a model entry with blank values
       for the URLs -- the assumption is that either there's no data there or
       something has gone wrong and needs fixing in code.

    5. If you want to change thumbnail resolutions, you need to create a new
       CourseOverviewImageConfig with the desired dimensions and then wipe the
       values in CourseOverviewImageSet.

    Logical next steps that I punted on for this first cut:

    1. Converting other parts of the app to use this.

       Our first cut only affects About Pages and the Student Dashboard. But
       most places that use course_image_url() should be converted -- e.g.
       course discovery, mobile, etc.

    2. Center cropping the image before scaling.

       This is desirable, but it involves a few edge cases (what the rounding
       policy is, what to do with undersized images, etc.) The behavior that
       we implemented is at least no worse than what was already there in terms
       of distorting images.

    3. Automatically invalidating entries based on CourseOverviewImageConfig.

       There are two basic paths I can think of for this. The first is to
       completely wipe this table when the config changes. The second is to
       actually tie the config as a foreign key from this model -- so you could
       do the comparison to see if the image_set's config_id matched
       CourseOverviewImageConfig.current() and invalidate it if they didn't
       match. I punted on this mostly because it's just not something that
       happens much at all in practice, there is an understood (if manual)
       process to do it, and it can happen in a follow-on PR if anyone is
       interested in extending this functionality.

    """
    course_overview = models.OneToOneField(CourseOverview, db_index=True, related_name="image_set",
                                           on_delete=models.CASCADE)
    small_url = models.TextField(blank=True, default="")
    large_url = models.TextField(blank=True, default="")

    @classmethod
    def create(cls, course_overview, course=None):
        """
        Create thumbnail images for this CourseOverview.

        This will save the CourseOverviewImageSet before it returns.
        """
        from openedx.core.lib.courses import create_course_image_thumbnail

        # If image thumbnails are not enabled, do nothing.
        config = CourseOverviewImageConfig.current()
        if not config.enabled:
            return

        # If a course object was provided, use that. Otherwise, pull it from
        # CourseOverview's course_id. This happens because sometimes we are
        # generated as part of the CourseOverview creation (course is available
        # and passed in), and sometimes the CourseOverview already exists.
        if not course:
            course = modulestore().get_course(course_overview.id)

        image_set = cls(course_overview=course_overview)

        if course.course_image:
            # Try to create a thumbnails of the course image. If this fails for any
            # reason (weird format, non-standard URL, etc.), the URLs will default
            # to being blank. No matter what happens, we don't want to bubble up
            # a 500 -- an image_set is always optional.
            try:
                image_set.small_url = create_course_image_thumbnail(course, config.small)
                image_set.large_url = create_course_image_thumbnail(course, config.large)
            except Exception:  # pylint: disable=broad-except
                log.exception(
                    "Could not create thumbnail for course %s with image %s (small=%s), (large=%s)",
                    course.id,
                    course.course_image,
                    config.small,
                    config.large
                )

        # Regardless of whether we created thumbnails or not, we need to save
        # this record before returning. If no thumbnails were created (there was
        # an error or the course has no source course_image), our url fields
        # just keep their blank defaults.
        try:
            with transaction.atomic():
                image_set.save()
                course_overview.image_set = image_set
        except (IntegrityError, ValueError):
            # In the event of a race condition that tries to save two image sets
            # to the same CourseOverview, we'll just silently pass on the one
            # that fails. They should be the same data anyway.
            #
            # The ValueError above is to catch the following error that can
            # happen in Django 1.8.4+ if the CourseOverview object fails to save
            # (again, due to race condition).
            #
            # Example: ValueError: save() prohibited to prevent data loss due
            #          to unsaved related object 'course_overview'.")
            pass

    def __unicode__(self):
        return u"CourseOverviewImageSet({}, small_url={}, large_url={})".format(
            self.course_overview_id, self.small_url, self.large_url
        )


class CourseOverviewImageConfig(ConfigurationModel):
    """
    This sets the size of the thumbnail images that Course Overviews will generate
    to display on the about, info, and student dashboard pages. If you make any
    changes to this, you will have to regenerate CourseOverviews in order for it
    to take effect. You might want to do this if you're doing precise theming of
    your install of edx-platform... but really, you probably don't want to do this
    at all at the moment, given how new this is. :-P
    """
    # Small thumbnail, for things like the student dashboard
    small_width = models.IntegerField(default=375)
    small_height = models.IntegerField(default=200)

    # Large thumbnail, for things like the about page
    large_width = models.IntegerField(default=750)
    large_height = models.IntegerField(default=400)

    @property
    def small(self):
        """Tuple for small image dimensions in pixels -- (width, height)"""
        return (self.small_width, self.small_height)

    @property
    def large(self):
        """Tuple for large image dimensions in pixels -- (width, height)"""
        return (self.large_width, self.large_height)

    def __unicode__(self):
        return u"CourseOverviewImageConfig(enabled={}, small={}, large={})".format(
            self.enabled, self.small, self.large
        )

