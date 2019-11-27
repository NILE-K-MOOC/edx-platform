
# -*- coding: utf-8 -*-
from __future__ import absolute_import

import logging

from django.http import HttpResponseBadRequest, Http404, JsonResponse
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.views.decorators.http import require_GET
from django.views.decorators.csrf import csrf_exempt
from django.core.exceptions import PermissionDenied
from django.conf import settings
from opaque_keys import InvalidKeyError
from xmodule.modulestore.exceptions import ItemNotFoundError
from edxmako.shortcuts import render_to_response

from xmodule.modulestore.django import modulestore

from xblock.core import XBlock
from xblock.django.request import webob_to_django_response, django_to_webob_request
from xblock.exceptions import NoSuchHandlerError
from xblock.plugin import PluginMissingError
from xblock.runtime import Mixologist

from contentstore.utils import get_lms_link_for_item
from contentstore.views.helpers import get_parent_xblock, is_unit, xblock_type_display_name, create_xblock, usage_key_with_run
from contentstore.views.item import create_xblock_info, add_container_page_publishing_info, StudioEditModuleRuntime
from contentstore.views.item import _save_xblock, _get_xblock

from opaque_keys.edx.keys import UsageKey

from student.auth import has_course_author_access
from django.utils.translation import ugettext as _

from xblock_django.api import disabled_xblocks, authorable_xblocks
from xblock_django.models import XBlockStudioConfigurationFlag

from openedx.core.djangoapps.content.course_overviews.models import CourseOverview
from opaque_keys.edx.keys import CourseKey

from models.settings.course_grading import CourseGradingModel

__all__ = [
    'container_handler',
    'component_handler',
    'CreateVideoModule'
]

log = logging.getLogger(__name__)

# NOTE: This list is disjoint from ADVANCED_COMPONENT_TYPES
COMPONENT_TYPES = ['discussion', 'html', 'problem', 'video']

ADVANCED_COMPONENT_TYPES = sorted(set(name for name, class_ in XBlock.load_classes()) - set(COMPONENT_TYPES))

ADVANCED_PROBLEM_TYPES = settings.ADVANCED_PROBLEM_TYPES

CONTAINER_TEMPLATES = [
    "basic-modal", "modal-button", "edit-xblock-modal",
    "editor-mode-button", "upload-dialog",
    "add-xblock-component", "add-xblock-component-button", "add-xblock-component-menu",
    "add-xblock-component-support-legend", "add-xblock-component-support-level", "add-xblock-component-menu-problem",
    "xblock-string-field-editor", "publish-xblock", "publish-history",
    "unit-outline", "container-message", "license-selector",
]


@csrf_exempt
def CreateVideoModule(request):

    # 파라미터 입력
    course_id = request.POST.get('course_id')    # course-v1:pdf+pdf+pdf
    secret_key = request.POST.get('secret_key')  # lgcns2019!@#
    video_url = request.POST.get('video_url')    # http://vod.kmoocs.kr/vod/2018/12/19/e8be85a1-cc00-453f-ad79-569620285f50.mp4

    # 각 섹션 이름 설정
    course_key = CourseKey.from_string(course_id)
    ALL_DEAFULT_NAME = CourseOverview.objects.get(id=course_key).display_name
    section_name = ALL_DEAFULT_NAME
    sub_section_name = ALL_DEAFULT_NAME
    vertical_name = ALL_DEAFULT_NAME
    video_name = ALL_DEAFULT_NAME

    # 파라미터 검증
    if course_id == '' or course_id == None:
        print('ERROR -> Parameter does not exist ... course_id')
        return JsonResponse({'result': 404})
    if secret_key == '' or secret_key == None:
        print('ERROR -> Parameter does not exist ... secret_key')
        return JsonResponse({'result': 404})
    if video_url == '' or video_url == None:
        print('ERROR -> Parameter does not exist ... video_url')
        return JsonResponse({'result': 404})

    # 비밀키 검증
    if secret_key != 'lgcns2019!@#':
        print('ERROR -> The secret key is not valid')
        return JsonResponse({'result': 403})

    # 강좌 아이디 파싱
    if course_id.find('course-v1') == -1:
        print('ERROR -> This is not a valid course id')
        return JsonResponse({'result': 500})
    else:
        course_id = course_id.replace('course-v1:', '')
        try:
            course = course_id.split('+')[0]
            run = course_id.split('+')[1]
            number = course_id.split('+')[2]
            print 'DEBUG -> course : ', course
            print 'DEBUG -> run : ', run
            print 'DEBUG -> number : ', number
        except BaseException as err:
            print('ERROR -> Course ID is not separated to the correct level')
            return JsonResponse({'result': 500})

        try:
            # 대주제 생성
            created_block = create_xblock(
                parent_locator='block-v1:'+course+'+'+run+'+'+number+'+type@course+block@course',
                user=User.objects.filter(is_staff=1).first(),
                category=u'chapter',
                display_name=section_name,
                boilerplate=None
            )
            chapter_block_id = created_block.location.block_id
            print 'DEBUG -> chapter_block_id : ', chapter_block_id

            # 소주제 생성
            created_block = create_xblock(
                parent_locator='block-v1:'+course+'+'+run+'+'+number+'+type@chapter+block@' + chapter_block_id,
                user=User.objects.filter(is_staff=1).first(),
                category=u'sequential',
                display_name=sub_section_name,
                boilerplate=None
            )
            sequential_block_id = created_block.location.block_id
            print 'DEBUG -> sequential_block_id : ', sequential_block_id

            # 이수점수 조정
            payload = {
                u'grace_period': {
                    u'hours': 0,
                    u'minutes': 0
                },
                u'minimum_grade_credit': 0.8,
                u'is_credit_course': False,
                u'graders': [
                    {u'weight': 100, u'short_label': u'EXAM', u'id': 0, u'min_count': 1, u'type': u'EXAM', u'drop_count': 0}
                ],
                u'grade_cutoffs': {
                    u'Pass': 0.90
                }
            }
            CourseGradingModel.update_from_json(course_key, payload, User.objects.filter(is_staff=1).first())

            # 유닛 생성
            created_block = create_xblock(
                parent_locator='block-v1:'+course+'+'+run+'+'+number+'+type@sequential+block@' + sequential_block_id,
                user=User.objects.filter(is_staff=1).first(),
                category=u'vertical',
                display_name=vertical_name,
                boilerplate=None
            )
            vertical_block_id = created_block.location.block_id
            print 'DEBUG -> vertical_block_id : ', vertical_block_id

            # 학습모듈 생성
            created_block = create_xblock(
                parent_locator='block-v1:'+course+'+'+run+'+'+number+'+type@vertical+block@' + vertical_block_id,
                user=User.objects.filter(is_staff=1).first(),
                category=u'video',
                display_name=video_name,
                boilerplate=None
            )
            video_block_id = created_block.location.block_id
            print 'DEBUG -> video_block_id : ', video_block_id

            # 학습모듈(비디오) URL 변경
            usage_key_string = 'block-v1:'+course+'+'+run+'+'+number+'+type@video+block@' + video_block_id
            metadata = {
                'html5_sources': [video_url],
                'display_name': video_name,
                'sub': '',
                'youtube_id_1_0': '',
                'has_score': True
            }
            usage_key = usage_key_with_run(usage_key_string)
            _save_xblock(
                User.objects.filter(is_staff=1).first(),
                _get_xblock(usage_key, User.objects.filter(is_staff=1).first()),
                data=None,
                children_strings=None,
                metadata=metadata,
                nullout=None,
                grader_type='EXAM',
                is_prereq=None,
                prereq_usage_key=None,
                prereq_min_score=None,
                publish=None,
                fields=None,
            )

            # 대주제 퍼블리싱
            usage_key_string = 'block-v1:' + course + '+' + run + '+' + number + '+type@chapter+block@' + chapter_block_id
            usage_key = usage_key_with_run(usage_key_string)
            _save_xblock(
                User.objects.filter(is_staff=1).first(),
                _get_xblock(usage_key, User.objects.filter(is_staff=1).first()),
                data=None,
                children_strings=None,
                metadata=None,
                nullout=None,
                grader_type=None,
                is_prereq=None,
                prereq_usage_key=None,
                prereq_min_score=None,
                publish='make_public',
                fields=None,
            )

            # 소주제 시험 설정
            usage_key_string = 'block-v1:' + course + '+' + run + '+' + number + '+type@sequential+block@' + sequential_block_id
            usage_key = usage_key_with_run(usage_key_string)
            _save_xblock(
                User.objects.filter(is_staff=1).first(),
                _get_xblock(usage_key, User.objects.filter(is_staff=1).first()),
                data=None,
                children_strings=None,
                metadata=None,
                nullout=None,
                grader_type='EXAM',
                is_prereq=None,
                prereq_usage_key=None,
                prereq_min_score=None,
                publish=None,
                fields=None,
            )

            return JsonResponse({'result': 200})

        except BaseException as err:
            print('ERROR -> An error occurred in the module generated core')
            print('ERROR -> err : ', err)
            return JsonResponse({'result': 500})


def _advanced_component_types(show_unsupported):
    """
    Return advanced component types which can be created.
    Args:
        show_unsupported: if True, unsupported XBlocks may be included in the return value
    Returns:
        A dict of authorable XBlock types and their support levels (see XBlockStudioConfiguration). For example:
        {
            "done": "us",  # unsupported
            "discussion: "fs"  # fully supported
        }
        Note that the support level will be "True" for all XBlocks if XBlockStudioConfigurationFlag
        is not enabled.
    """
    enabled_block_types = _filter_disabled_blocks(ADVANCED_COMPONENT_TYPES)
    if XBlockStudioConfigurationFlag.is_enabled():
        authorable_blocks = authorable_xblocks(allow_unsupported=show_unsupported)
        filtered_blocks = {}
        for block in authorable_blocks:
            if block.name in enabled_block_types:
                filtered_blocks[block.name] = block.support_level
        return filtered_blocks
    else:
        all_blocks = {}
        for block_name in enabled_block_types:
            all_blocks[block_name] = True
        return all_blocks


def _load_mixed_class(category):
    """
    Load an XBlock by category name, and apply all defined mixins
    """
    component_class = XBlock.load_class(category, select=settings.XBLOCK_SELECT_FUNCTION)
    mixologist = Mixologist(settings.XBLOCK_MIXINS)
    return mixologist.mix(component_class)


@require_GET
@login_required
def container_handler(request, usage_key_string):
    """
    The restful handler for container xblock requests.
    GET
        html: returns the HTML page for editing a container
        json: not currently supported
    """
    #if 'text/html' in request.META.get('HTTP_ACCEPT', 'text/html'):
    if True:
        try:
            usage_key = UsageKey.from_string(usage_key_string)
        except InvalidKeyError:  # Raise Http404 on invalid 'usage_key_string'
            raise Http404
        with modulestore().bulk_operations(usage_key.course_key):
            try:
                course, xblock, lms_link, preview_lms_link = _get_item_in_course(request, usage_key)
            except ItemNotFoundError:
                return HttpResponseBadRequest()

            component_templates = get_component_templates(course)
            ancestor_xblocks = []
            parent = get_parent_xblock(xblock)
            action = request.GET.get('action', 'view')

            is_unit_page = is_unit(xblock)
            unit = xblock if is_unit_page else None

            while parent and parent.category != 'course':
                if unit is None and is_unit(parent):
                    unit = parent
                ancestor_xblocks.append(parent)
                parent = get_parent_xblock(parent)
            ancestor_xblocks.reverse()

            assert unit is not None, "Could not determine unit page"
            subsection = get_parent_xblock(unit)
            assert subsection is not None, "Could not determine parent subsection from unit " + unicode(unit.location)
            section = get_parent_xblock(subsection)
            assert section is not None, "Could not determine ancestor section from unit " + unicode(unit.location)

            # Fetch the XBlock info for use by the container page. Note that it includes information
            # about the block's ancestors and siblings for use by the Unit Outline.
            xblock_info = create_xblock_info(xblock, include_ancestor_info=is_unit_page)

            if is_unit_page:
                add_container_page_publishing_info(xblock, xblock_info)

            # need to figure out where this item is in the list of children as the
            # preview will need this
            index = 1
            for child in subsection.get_children():
                if child.location == unit.location:
                    break
                index += 1

            return render_to_response('container.html', {
                'context_course': course,  # Needed only for display of menus at top of page.
                'action': action,
                'xblock': xblock,
                'xblock_locator': xblock.location,
                'unit': unit,
                'is_unit_page': is_unit_page,
                'subsection': subsection,
                'section': section,
                'new_unit_category': 'vertical',
                'ancestor_xblocks': ancestor_xblocks,
                'component_templates': component_templates,
                'xblock_info': xblock_info,
                'draft_preview_link': preview_lms_link,
                'published_preview_link': lms_link,
                'templates': CONTAINER_TEMPLATES
            })
    else:
        return HttpResponseBadRequest("Only supports HTML requests")


def get_component_templates(courselike, library=False):
    """
    Returns the applicable component templates that can be used by the specified course or library.
    """
    def create_template_dict(name, category, support_level, boilerplate_name=None, tab="common", hinted=False):
        """
        Creates a component template dict.
        Parameters
            display_name: the user-visible name of the component
            category: the type of component (problem, html, etc.)
            support_level: the support level of this component
            boilerplate_name: name of boilerplate for filling in default values. May be None.
            hinted: True if hinted problem else False
            tab: common(default)/advanced, which tab it goes in
        """
        return {
            "display_name": name,
            "category": category,
            "boilerplate_name": boilerplate_name,
            "hinted": hinted,
            "tab": tab,
            "support_level": support_level
        }

    def component_support_level(editable_types, name, template=None):
        """
        Returns the support level for the given xblock name/template combination.
        Args:
            editable_types: a QuerySet of xblocks with their support levels
            name: the name of the xblock
            template: optional template for the xblock
        Returns:
            If XBlockStudioConfigurationFlag is enabled, returns the support level
            (see XBlockStudioConfiguration) or False if this xblock name/template combination
            has no Studio support at all. If XBlockStudioConfigurationFlag is disabled,
            simply returns True.
        """
        # If the Studio support feature is disabled, return True for all.
        if not XBlockStudioConfigurationFlag.is_enabled():
            return True
        if template is None:
            template = ""
        extension_index = template.rfind(".yaml")
        if extension_index >= 0:
            template = template[0:extension_index]
        for block in editable_types:
            if block.name == name and block.template == template:
                return block.support_level

        return False

    def create_support_legend_dict():
        """
        Returns a dict of settings information for the display of the support level legend.
        """
        return {
            "show_legend": XBlockStudioConfigurationFlag.is_enabled(),
            "allow_unsupported_xblocks": allow_unsupported,
            "documentation_label": _("{platform_name} Support Levels:").format(platform_name=settings.PLATFORM_NAME)
        }

    component_display_names = {
        'discussion': _("Discussion"),
        'html': _("HTML"),
        'problem': _("Problem"),
        'video': _("Video")
    }

    component_templates = []
    categories = set()
    # The component_templates array is in the order of "advanced" (if present), followed
    # by the components in the order listed in COMPONENT_TYPES.
    component_types = COMPONENT_TYPES[:]

    # Libraries do not support discussions
    if library:
        component_types = [component for component in component_types if component != 'discussion']

    component_types = _filter_disabled_blocks(component_types)

    # Content Libraries currently don't allow opting in to unsupported xblocks/problem types.
    allow_unsupported = getattr(courselike, "allow_unsupported_xblocks", False)

    for category in component_types:
        authorable_variations = authorable_xblocks(allow_unsupported=allow_unsupported, name=category)
        support_level_without_template = component_support_level(authorable_variations, category)
        templates_for_category = []
        component_class = _load_mixed_class(category)

        if support_level_without_template:
            # add the default template with localized display name
            # TODO: Once mixins are defined per-application, rather than per-runtime,
            # this should use a cms mixed-in class. (cpennington)
            display_name = xblock_type_display_name(category, _('Blank'))  # this is the Blank Advanced problem
            templates_for_category.append(
                create_template_dict(display_name, category, support_level_without_template, None, 'advanced')
            )
            categories.add(category)

        # add boilerplates
        if hasattr(component_class, 'templates'):
            for template in component_class.templates():
                filter_templates = getattr(component_class, 'filter_templates', None)
                if not filter_templates or filter_templates(template, courselike):
                    template_id = template.get('template_id')
                    support_level_with_template = component_support_level(
                        authorable_variations, category, template_id
                    )
                    if support_level_with_template:
                        # Tab can be 'common' 'advanced'
                        # Default setting is common/advanced depending on the presence of markdown
                        tab = 'common'
                        if template['metadata'].get('markdown') is None:
                            tab = 'advanced'
                        hinted = template.get('hinted', False)

                        templates_for_category.append(
                            create_template_dict(
                                _(template['metadata'].get('display_name')),    # pylint: disable=translation-of-non-string
                                category,
                                support_level_with_template,
                                template_id,
                                tab,
                                hinted,
                            )
                        )

        # Add any advanced problem types. Note that these are different xblocks being stored as Advanced Problems.
        if category == 'problem':
            disabled_block_names = [block.name for block in disabled_xblocks()]
            advanced_problem_types = [advanced_problem_type for advanced_problem_type in ADVANCED_PROBLEM_TYPES
                                      if advanced_problem_type['component'] not in disabled_block_names]
            for advanced_problem_type in advanced_problem_types:
                component = advanced_problem_type['component']
                boilerplate_name = advanced_problem_type['boilerplate_name']

                authorable_advanced_component_variations = authorable_xblocks(
                    allow_unsupported=allow_unsupported, name=component
                )
                advanced_component_support_level = component_support_level(
                    authorable_advanced_component_variations, component, boilerplate_name
                )
                if advanced_component_support_level:
                    try:
                        component_display_name = xblock_type_display_name(component)
                    except PluginMissingError:
                        log.warning('Unable to load xblock type %s to read display_name', component, exc_info=True)
                    else:
                        templates_for_category.append(
                            create_template_dict(
                                component_display_name,
                                component,
                                advanced_component_support_level,
                                boilerplate_name,
                                'advanced'
                            )
                        )
                        categories.add(component)

        component_templates.append({
            "type": category,
            "templates": templates_for_category,
            "display_name": component_display_names[category],
            "support_legend": create_support_legend_dict()
        })

    # Libraries do not support advanced components at this time.
    if library:
        return component_templates

    # Check if there are any advanced modules specified in the course policy.
    # These modules should be specified as a list of strings, where the strings
    # are the names of the modules in ADVANCED_COMPONENT_TYPES that should be
    # enabled for the course.
    course_advanced_keys = courselike.advanced_modules
    advanced_component_templates = {
        "type": "advanced",
        "templates": [],
        "display_name": _("Advanced"),
        "support_legend": create_support_legend_dict()
    }
    advanced_component_types = _advanced_component_types(allow_unsupported)
    # Set component types according to course policy file
    if isinstance(course_advanced_keys, list):
        for category in course_advanced_keys:
            if category in advanced_component_types.keys() and category not in categories:
                # boilerplates not supported for advanced components
                try:
                    component_display_name = xblock_type_display_name(category, default_display_name=category)
                    advanced_component_templates['templates'].append(
                        create_template_dict(
                            component_display_name,
                            category,
                            advanced_component_types[category]
                        )
                    )
                    categories.add(category)
                except PluginMissingError:
                    # dhm: I got this once but it can happen any time the
                    # course author configures an advanced component which does
                    # not exist on the server. This code here merely
                    # prevents any authors from trying to instantiate the
                    # non-existent component type by not showing it in the menu
                    log.warning(
                        "Advanced component %s does not exist. It will not be added to the Studio new component menu.",
                        category
                    )
    else:
        log.error(
            "Improper format for course advanced keys! %s",
            course_advanced_keys
        )
    if len(advanced_component_templates['templates']) > 0:
        component_templates.insert(0, advanced_component_templates)

    return component_templates


def _filter_disabled_blocks(all_blocks):
    """
    Filter out disabled xblocks from the provided list of xblock names.
    """
    disabled_block_names = [block.name for block in disabled_xblocks()]
    return [block_name for block_name in all_blocks if block_name not in disabled_block_names]


@login_required
def _get_item_in_course(request, usage_key):
    """
    Helper method for getting the old location, containing course,
    item, lms_link, and preview_lms_link for a given locator.
    Verifies that the caller has permission to access this item.
    """
    # usage_key's course_key may have an empty run property
    usage_key = usage_key.replace(course_key=modulestore().fill_in_run(usage_key.course_key))

    course_key = usage_key.course_key

    if not has_course_author_access(request.user, course_key):
        raise PermissionDenied()

    course = modulestore().get_course(course_key)
    item = modulestore().get_item(usage_key, depth=1)
    lms_link = get_lms_link_for_item(item.location)
    preview_lms_link = get_lms_link_for_item(item.location, preview=True)

    return course, item, lms_link, preview_lms_link


@login_required
def component_handler(request, usage_key_string, handler, suffix=''):
    """
    Dispatch an AJAX action to an xblock
    Args:
        usage_id: The usage-id of the block to dispatch to
        handler (str): The handler to execute
        suffix (str): The remainder of the url to be passed to the handler
    Returns:
        :class:`django.http.HttpResponse`: The response from the handler, converted to a
            django response
    """

    usage_key = UsageKey.from_string(usage_key_string)

    descriptor = modulestore().get_item(usage_key)
    descriptor.xmodule_runtime = StudioEditModuleRuntime(request.user)
    # Let the module handle the AJAX
    req = django_to_webob_request(request)

    try:
        resp = descriptor.handle(handler, req, suffix)

    except NoSuchHandlerError:
        log.info("XBlock %s attempted to access missing handler %r", descriptor, handler, exc_info=True)
        raise Http404

    # unintentional update to handle any side effects of handle call
    # could potentially be updating actual course data or simply caching its values
    modulestore().update_item(descriptor, request.user.id)

    return webob_to_django_response(resp)
