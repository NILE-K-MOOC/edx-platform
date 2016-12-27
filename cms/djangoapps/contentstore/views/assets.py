#-*- coding: utf-8 -*-
import os
import logging
from functools import partial
import math
import json

from django.http import HttpResponseBadRequest
from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import ensure_csrf_cookie
from django.views.decorators.http import require_http_methods, require_POST
from django.conf import settings

from edxmako.shortcuts import render_to_response
from contentserver.caching import del_cached_content

from contentstore.utils import reverse_course_url
from xmodule.contentstore.django import contentstore
from xmodule.modulestore.django import modulestore
from xmodule.contentstore.content import StaticContent
from xmodule.exceptions import NotFoundError
from contentstore.views.exception import AssetNotFoundException
from django.core.exceptions import PermissionDenied
from opaque_keys.edx.keys import CourseKey, AssetKey

from util.date_utils import get_default_time_display
from util.json_request import JsonResponse
from django.http import HttpResponseNotFound
from django.utils.translation import ugettext as _
from pymongo import ASCENDING, DESCENDING
from student.auth import has_course_author_access
from xmodule.modulestore.exceptions import ItemNotFoundError

from django.views.decorators.csrf import csrf_exempt

import urllib2, urlparse, urllib
import json
__all__ = ['assets_handler', 'assets_callback']

# pylint: disable=unused-argument


@login_required
@csrf_exempt
def assets_handler(request, course_key_string=None, asset_key_string=None):
    """
    The restful handler for assets.
    It allows retrieval of all the assets (as an HTML page), as well as uploading new assets,
    deleting assets, and changing the "locked" state of an asset.

    GET
        html: return an html page which will show all course assets. Note that only the asset container
            is returned and that the actual assets are filled in with a client-side request.
        json: returns a page of assets. The following parameters are supported:
            page: the desired page of results (defaults to 0)
            page_size: the number of items per page (defaults to 50)
            sort: the asset field to sort by (defaults to "date_added")
            direction: the sort direction (defaults to "descending")
    POST
        json: create (or update?) an asset. The only updating that can be done is changing the lock state.
    PUT
        json: update the locked state of an asset
    DELETE
        json: delete an asset
    """
    course_key = CourseKey.from_string(course_key_string)
    if not has_course_author_access(request.user, course_key):
        raise PermissionDenied()

    response_format = request.GET.get('format') or request.POST.get('format') or 'html'
    if response_format == 'json' or 'application/json' in request.META.get('HTTP_ACCEPT', 'application/json'):
        if request.method == 'GET':
            return _assets_json(request, course_key)
        else:
            asset_key = AssetKey.from_string(asset_key_string) if asset_key_string else None
            return _update_asset(request, course_key, asset_key)
    elif request.method == 'GET':  # assume html
        return _asset_index(request, course_key)
    else:
        return HttpResponseNotFound()


def _asset_index(request, course_key):
    """
    Display an editable asset library.

    Supports start (0-based index into the list of assets) and max query parameters.
    """
    course_module = modulestore().get_course(course_key)

    return render_to_response('asset_index.html', {
        'context_course': course_module,
        'max_file_size_in_mbs': settings.MAX_ASSET_UPLOAD_FILE_SIZE_IN_MB,
        'chunk_size_in_mbs': settings.UPLOAD_CHUNK_SIZE_IN_MB,
        'max_file_size_redirect_url': settings.MAX_ASSET_UPLOAD_FILE_SIZE_URL,
        'asset_callback_url': reverse_course_url('assets_handler', course_key)
    })


def _assets_json(request, course_key):
    """
    Display an editable asset library.

    Supports start (0-based index into the list of assets) and max query parameters.
    """
    requested_page = int(request.GET.get('page', 0))
    requested_page_size = int(request.GET.get('page_size', 50))
    requested_sort = request.GET.get('sort', 'date_added')
    requested_filter = request.GET.get('asset_type', '')
    requested_file_types = settings.FILES_AND_UPLOAD_TYPE_FILTERS.get(
        requested_filter, None)
    filter_params = None
    if requested_filter:
        if requested_filter == 'OTHER':
            all_filters = settings.FILES_AND_UPLOAD_TYPE_FILTERS
            where = []
            for all_filter in all_filters:
                extension_filters = all_filters[all_filter]
                where.extend(
                    ["JSON.stringify(this.contentType).toUpperCase() != JSON.stringify('{}').toUpperCase()".format(
                        extension_filter) for extension_filter in extension_filters])
            filter_params = {
                "$where": ' && '.join(where),
            }
        else:
            where = ["JSON.stringify(this.contentType).toUpperCase() == JSON.stringify('{}').toUpperCase()".format(
                req_filter) for req_filter in requested_file_types]
            filter_params = {
                "$where": ' || '.join(where),
            }

    sort_direction = DESCENDING
    if request.GET.get('direction', '').lower() == 'asc':
        sort_direction = ASCENDING

    # Convert the field name to the Mongo name
    if requested_sort == 'date_added':
        requested_sort = 'uploadDate'
    elif requested_sort == 'display_name':
        requested_sort = 'displayname'
    sort = [(requested_sort, sort_direction)]

    current_page = max(requested_page, 0)
    start = current_page * requested_page_size
    options = {
        'current_page': current_page,
        'page_size': requested_page_size,
        'sort': sort,
        'filter_params': filter_params
    }
    assets, total_count = _get_assets_for_page(request, course_key, options)
    end = start + len(assets)

    # If the query is beyond the final page, then re-query the final page so
    # that at least one asset is returned
    if requested_page > 0 and start >= total_count:
        options['current_page'] = current_page = int(math.floor((total_count - 1) / requested_page_size))
        start = current_page * requested_page_size
        assets, total_count = _get_assets_for_page(request, course_key, options)
        end = start + len(assets)

    asset_json = []
    for asset in assets:
        asset_location = asset['asset_key']
        # note, due to the schema change we may not have a 'thumbnail_location'
        # in the result set
        thumbnail_location = asset.get('thumbnail_location', None)
        if thumbnail_location:
            thumbnail_location = course_key.make_asset_key(
                'thumbnail', thumbnail_location[4])

        asset_locked = asset.get('locked', False)
        '''
        kmooc MME로 전면 수정함.
        '''
        url_split = request.META.get('HTTP_REFERER').split("/")
        if url_split[3] == 'cdn':
            # try:
            #     thumbnail_location = asset['cdn_url'][:asset['cdn_url'].rfind('.')] + "_0.png"
            #     thumbnail_location = thumbnail_location[:thumbnail_location.rfind('/')] + "/thumb" + thumbnail_location[thumbnail_location.rfind('/'):]
            # except Exception as e:
            #     pass

            uuid = asset.get('uuid', '')
            playtime = asset.get('playtime', '')
            state = asset.get('state', '')
            cdn_url = asset.get('cdn_url', '')

            displayname = asset.get('displayname', '')
            contentType = asset.get('contentType', 'video/mp4')

            uploadDate = asset.get('uploadDate', '')

            get_thumbnail_url = asset.get('thumbnail_url', None)
            if get_thumbnail_url is None:
                if cdn_url:
                    cdn_sp = cdn_url[:cdn_url.rfind('.')]
                    cdn_name = os.path.basename(cdn_sp)
                    thumbnail_url = os.path.join(cdn_sp.replace(cdn_name,''), 'thumb', cdn_name + '_0.png')
                    # thumbnail_location = cdn_url[:cdn_url.rfind('.')] + '_0.png'
                    # thumbnail_url = thumbnail_location
                else:
                    thumbnail_url = ''
            else:
                thumbnail_url = get_thumbnail_url

            '''
            상태변환 처리
            '''
            if state not in ('E', 'F'):

                try:
                    cdn_parse = urlparse.urlparse(cdn_url)
                    mme_url = "http://%s" % cdn_parse.netloc
                except Exception as e:
                    logging.log("urlparse Error: %s" % e)
                    cdn_parse = ''
                    mme_url = "-"


                # print content
                # print uuid


                try:
                    trans_state = status_check(mme_url, uuid, playtime)
                except:
                    trans_state = 'I'

                if trans_state == 'E' or trans_state == 'F':
                    ''' 데이터 갱신함.'''
                    # print '++++++++++++'
                    # print asset

                    content = request.REQUEST

                    content.name = displayname
                    content.cdn_url = cdn_url
                    content.content_type = contentType
                    content.thumbnail_location = thumbnail_url
                    content.thumbnail_url = thumbnail_url
                    content.location = StaticContent.compute_cdn_location(course_key, displayname)
                    # content.location = asset['filename']
                    content.uuid = uuid
                    content.playtime = playtime
                    content.state = trans_state
                    content.mme = 'mme'


                    state_update = contentstore().save_cdn(
                        content
                    )

            else:
                trans_state = state # 완료와 실패 이외의 상태는 등록시 설정된 값으로 구성된다.

            asset_json.append(_get_cdn_json(
                displayname,
                contentType,
                uploadDate,
                asset_location,
                thumbnail_url,
                cdn_url, uuid, playtime, trans_state
            ))

        else:
            asset_json.append(_get_asset_json(
                asset['displayname'],
                asset['contentType'],
                asset['uploadDate'],
                asset_location,
                thumbnail_location,
                asset_locked
            ))

    return JsonResponse({
        'start': start,
        'end': end,
        'page': current_page,
        'pageSize': requested_page_size,
        'totalCount': total_count,
        'assets': asset_json,
        'sort': requested_sort,
    })


def _get_assets_for_page(request, course_key, options):
    """
    Returns the list of assets for the specified page and page size.
    """
    current_page = options['current_page']
    page_size = options['page_size']
    sort = options['sort']
    filter_params = options['filter_params'] if options['filter_params'] else None
    start = current_page * page_size
    '''
    kmooc MME
    메소드 수정함.
    '''
    url_split = request.META.get('HTTP_REFERER').split("/")

    if (url_split[3] == 'cdn'):

        return contentstore().get_all_cdn_content_for_course(
            course_key, start=start, maxresults=page_size, sort=sort, filter_params=filter_params
        )
    else:
        return contentstore().get_all_content_for_course(
            course_key, start=start, maxresults=page_size, sort=sort, filter_params=filter_params
        )


def get_file_size(upload_file):
    """
    Helper method for getting file size of an upload file.
    Can be used for mocking test file sizes.
    """
    return upload_file.size


@require_POST
@ensure_csrf_cookie
@login_required
def _upload_asset(request, course_key):
    '''
    This method allows for POST uploading of files into the course asset
    library, which will be supported by GridFS in MongoDB.
    '''
    # Does the course actually exist?!? Get anything from it to prove its
    # existence
    try:
        modulestore().get_course(course_key)
    except ItemNotFoundError:
        # no return it as a Bad Request response
        logging.error("Could not find course: %s", course_key)
        return HttpResponseBadRequest()

    # compute a 'filename' which is similar to the location formatting, we're
    # using the 'filename' nomenclature since we're using a FileSystem paradigm
    # here. We're just imposing the Location string formatting expectations to
    # keep things a bit more consistent
    upload_file = request.FILES['file']
    filename = upload_file.name
    mime_type = upload_file.content_type
    size = get_file_size(upload_file)

    # If file is greater than a specified size, reject the upload
    # request and send a message to the user. Note that since
    # the front-end may batch large file uploads in smaller chunks,
    # we validate the file-size on the front-end in addition to
    # validating on the backend. (see cms/static/js/views/assets.js)
    max_file_size_in_bytes = settings.MAX_ASSET_UPLOAD_FILE_SIZE_IN_MB * 1000 ** 2
    if size > max_file_size_in_bytes:
        return JsonResponse({
            'error': _(
                'File {filename} exceeds maximum size of '
                '{size_mb} MB. Please follow the instructions here '
                'to upload a file elsewhere and link to it instead: '
                '{faq_url}'
            ).format(
                filename=filename,
                size_mb=settings.MAX_ASSET_UPLOAD_FILE_SIZE_IN_MB,
                faq_url=settings.MAX_ASSET_UPLOAD_FILE_SIZE_URL,
            )
        }, status=413)

    content_loc = StaticContent.compute_location(course_key, filename)

    chunked = upload_file.multiple_chunks()
    sc_partial = partial(StaticContent, content_loc, filename, mime_type)
    if chunked:
        content = sc_partial(upload_file.chunks())
        tempfile_path = upload_file.temporary_file_path()
    else:
        content = sc_partial(upload_file.read())
        tempfile_path = None

    # first let's see if a thumbnail can be created
    (thumbnail_content, thumbnail_location) = contentstore().generate_thumbnail(
        content,
        tempfile_path=tempfile_path,
    )

    # delete cached thumbnail even if one couldn't be created this time (else
    # the old thumbnail will continue to show)
    del_cached_content(thumbnail_location)
    # now store thumbnail location only if we could create it
    if thumbnail_content is not None:
        content.thumbnail_location = thumbnail_location

    # then commit the content
    contentstore().save(content)
    del_cached_content(content.location)

    # readback the saved content - we need the database timestamp
    readback = contentstore().find(content.location)
    locked = getattr(content, 'locked', False)
    response_payload = {
        'asset': _get_asset_json(
            content.name,
            content.content_type,
            readback.last_modified_at,
            content.location,
            content.thumbnail_location,
            locked
        ),
        'msg': _('Upload completed')
    }

    return JsonResponse(response_payload)

def save_cdn(request, course_key):
    '''
    kmooc MME
    메소드 추가
    '''
    content = request.REQUEST
    content.name=request.REQUEST['file_name']

    try:
        req_cdn_url = request.REQUEST['cdn_url'].replace("mme.", "vod.")
        content.cdn_url= req_cdn_url
    except:
        try:
            content.cdn_url = request.REQUEST['cdn_url']
        except:
            content.cdn_url = '-'

    content.content_type=request.REQUEST['file_type']
    content.thumbnail_location=request.REQUEST['thumbnail_url']
    content.thumbnail_url=request.REQUEST['thumbnail_url']
    content.location = StaticContent.compute_cdn_location(course_key, request.REQUEST['file_name'])
    # print content

    try:
        content.uuid = request.REQUEST['uuid']
        content.playtime = request.REQUEST['playtime']
        content.state = request.REQUEST['state']
        content.mme = request.REQUEST['mme']
    except:
        content.uuid = ''
        content.playtime = ''
        content.state = ''
        content.mme = ''

    # print "@@@@@@@@@@@@@@@@@@@"
    # print content.name

    contentstore().save_cdn(content)


    readback = contentstore().find_cdn(content.location)
    locked = False;
    response_payload = {
        'asset': _get_asset_json(
            content.name,
            content.content_type,
            readback.last_modified_at,
            content.location,
            content.thumbnail_location,
            locked
        ),
        'msg': _('Upload completed'),
        'result': 'success'
    }
    return JsonResponse(response_payload)

@require_http_methods(("DELETE", "POST", "PUT"))
@login_required
@ensure_csrf_cookie
def _update_asset(request, course_key, asset_key):
    """
    restful CRUD operations for a course asset.
    Currently only DELETE, POST, and PUT methods are implemented.

    asset_path_encoding: the odd /c4x/org/course/category/name repr of the asset (used by Backbone as the id)
    """
    # print request
    if request.method == 'DELETE':
        try:

            """
            todo 아래의 코드는 uuid를 찾지 못함. find_cdn 과 같은 메소드를 만들고 uuid값을 가져와 처리해야 한다
             ** 우선 몽고(아래코드)를 처리하고 곧바로 mme데이터를 삭제하자.
             ** 그리고 신규 파일 업로드 후 삭제 버튼 이벤트가 잘 처리 안된다. 그러므로 이벤트를 두군데에 처리해야 한다.
             1. asset_index.html : javascript로 그냥 처리함.
             2. assets.py : uuid를 조회하여 처리함
             asset-v1:e1+e1+e1+type@cdn+block@robot_arms.mp4
             asset-v1:e1+e1+e1+type@cdn+block@robot_arms.mp4
            """



            # try:
            ''' MME 콘텐츠 삭제'''
            content = contentstore().find_cdn_uuid(asset_key)

            uuid = content['uuid']
            playtime = content['playtime']
            cdn_url = content['cdn_url']
            cdn_parse = urlparse.urlparse(cdn_url)

            # print content
            # print uuid
            mme_url = "http://%s" % cdn_parse.netloc

            if uuid is None or uuid == '':
                uuid = cdn_url.split("/")[-1].replace(".mp4", "")

            # print "mme delete"

            mme_delete(mme_url, uuid)
            # except Exception, e:
            #     print "MME Delete Exception: %s" % e

            # print "mme delete finish"

            # print "mongo delete"
            delete_asset(course_key, asset_key)
            # print "mongo delete finish"

            return JsonResponse()
        except AssetNotFoundException:
            return JsonResponse(status=404)

    elif request.method in ('PUT', 'POST'):

        if 'file' in request.FILES:
            return _upload_asset(request, course_key)
        elif 'cdn_url' in request.REQUEST:
            ''' kmooc MME'''
            return save_cdn(request, course_key)
        else:
            # Update existing asset
            try:
                modified_asset = json.loads(request.body)
            except ValueError:
                return HttpResponseBadRequest()
            contentstore().set_attr(asset_key, 'locked', modified_asset['locked'])
            # Delete the asset from the cache so we check the lock status the next time it is requested.
            del_cached_content(asset_key)
            return JsonResponse(modified_asset, status=201)


def delete_asset(course_key, asset_key):
    """
    Deletes asset represented by given 'asset_key' in the course represented by given course_key.
    """
    # Make sure the item to delete actually exists.
    try:
        content = contentstore().find(asset_key)
    except NotFoundError:
        raise AssetNotFoundException

    # ok, save the content into the trashcan
    contentstore('trashcan').save(content)

    # see if there is a thumbnail as well, if so move that as well
    if content.thumbnail_location is not None:
        # We are ignoring the value of the thumbnail_location-- we only care whether
        # or not a thumbnail has been stored, and we can now easily create the correct path.
        thumbnail_location = course_key.make_asset_key('thumbnail', asset_key.name)
        try:
            thumbnail_content = contentstore().find(thumbnail_location)
            contentstore('trashcan').save(thumbnail_content)
            # hard delete thumbnail from origin
            contentstore().delete(thumbnail_content.get_id())
            # remove from any caching
            del_cached_content(thumbnail_location)
        except Exception:  # pylint: disable=broad-except
            logging.warning('Could not delete thumbnail: %s', thumbnail_location)

    # delete the original
    contentstore().delete(content.get_id())
    # remove from cache
    del_cached_content(content.location)


def _get_asset_json(display_name, content_type, date, location, thumbnail_location, locked):
    """
    Helper method for formatting the asset information to send to client.
    """
    asset_url = StaticContent.serialize_asset_key_with_slash(location)
    external_url = settings.LMS_BASE + asset_url
    return {
        'display_name': display_name,
        'content_type': content_type,
        'date_added': get_default_time_display(date),
        'url': asset_url,
        'external_url': external_url,
        'portable_url': StaticContent.get_static_path_from_location(location),
        'thumbnail': StaticContent.serialize_asset_key_with_slash(thumbnail_location) if thumbnail_location else None,
        'locked': locked,
        # Needed for Backbone delete/update.
        'id': unicode(location)
    }

def _get_cdn_json(display_name, content_type, date, location, thumbnail_location, cdn_url='', uuid='', playtime='', state=''):
    '''
    kmooc MME
    '''
    asset_url = StaticContent.serialize_asset_key_with_slash(location)
    localtime = date.strftime("%Y-%m-%d")

    # external_url = settings.LMS_BASE + asset_url

    return {
        'display_name': display_name,
        'content_type': content_type,
        # 'date_added': get_default_time_display(date),
        'date_added': localtime,
        'url': uuid,
        # 'url': uuid,
        'external_url': cdn_url,
        # 'portable_url': StaticContent.get_static_path_from_location(location),
        'portable_url': state,
        'thumbnail': thumbnail_location,
        'uuid': uuid,
        'playtime': playtime,
        'state': state,
        # 'locked': locked,
        'id': unicode(location)
    }

def mme_delete(mme, uuid):
    '''
    MME 에 저장된 영상 삭제
    '''
    try:

        content_delete_host = "%s/mov_delete?uuid=%s" % (mme, uuid)
        # print content_delete_host
        header = {'User-Agent': 'MME/2.0', 'Content-Type': 'application/json'}
        req = urllib2.Request(content_delete_host)
        res = urllib2.urlopen(req, timeout=2).read()
        # print 'MME CDN DELETE: %s' % content_delete_host
        # print res
        return True
    except urllib2.HTTPError, e:
        print "HTTPError: %s" % e
        return False
    except urllib2.URLError, e:
        print "URLError: %s" % e
        return False
    except Exception, e:
        print "Exception: %s" %e
        return False

def status_check(mme_url, uuid, playtime):

    url = "%s/upload_mov?uuid=%s&playtime=%s" % (mme_url, uuid, playtime)
    req = urllib2.Request(url)
    res = urllib2.urlopen(req).read()


    j_data = json.loads(res)
    if j_data['data']['status'] == 'complete':
        state = 'E'
    elif j_data['data']['status'] == 'fail':
        state = 'F'

    return state

@csrf_exempt
def assets_callback(request, course_key_string=None, asset_key_string=None):

    try:
        course_key = CourseKey.from_string(course_key_string)
        asset_key = AssetKey.from_string(asset_key_string) if asset_key_string else None

        content = request.REQUEST
        content_keys = request.REQUEST.keys()

        content.name = request.REQUEST['file_name'] if 'file_name' in content_keys else ''
        content.cdn_url = request.REQUEST['cdn_url'] if 'cdn_url' in content_keys else ''
        content.content_type = request.REQUEST['file_type'] if 'file_type' in content_keys else ''
        content.thumbnail_location = request.REQUEST['thumbnail_url'] if 'thumbnail_url' in content_keys else ''
        content.thumbnail_url = request.REQUEST['thumbnail_url'] if 'thumbnail_url' in content_keys else ''
        content.location = StaticContent.compute_cdn_location(course_key, request.REQUEST['file_name']) if 'file_name' in content_keys else ''
        content.uuid = request.REQUEST['uuid'] if 'uuid' in content_keys else ''
        content.playtime = request.REQUEST['playtime'] if 'playtime' in content_keys else ''
        content.state = request.REQUEST['state'] if 'state' in content_keys else 'F'
        content.mme = 'mme'

        if content.name and content.cdn_url and content.content_type and content.thumbnail_url \
            and content.uuid and content.playtime and content.state:


            mongo = contentstore().find_cdn_uuid(content.location)
            if mongo['uuid'] == content.uuid:
            # print mongo
                contentstore().save_cdn(content)

                return JsonResponse({'status': 'ok'})
            else:
                return JsonResponse({'status': 'fail', 'msg': 'uuid not found'})
        else:
            return JsonResponse({'state': 'fail', 'msg': 'params'})
    except Exception as e:

        return JsonResponse({
            'status': 'fail',
            'msg': e
        })