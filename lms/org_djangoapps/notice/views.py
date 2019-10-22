import logging
import mimetypes
import os
import urllib

from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.http import HttpResponse, HttpResponseRedirect, Http404
from django.shortcuts import get_object_or_404
from django.conf import settings
from django.utils import timezone
from edxmako.shortcuts import render_to_response, render_to_string

from notice.models import Notice, Attachments

log = logging.getLogger(__name__)

# notice list select with pagging.
def list(request, initial_mode="login"):
    pageRowCount = 10
    pageDisplayCount = 10
    startPage = 1
    endPage = 1

    searchData = request.GET.get('searchData', '')
    page = request.GET.get('page')

    noticeList = Notice.objects.prefetch_related('attachments_set').order_by('-id')

    if searchData:
        noticeList = noticeList.filter(title__icontains=searchData)

    paginator = Paginator(noticeList, pageRowCount)

    totalPageCount = paginator.num_pages

    try:
        pageObjects = paginator.page(page)
    except PageNotAnInteger:
        # If page is not an integer, deliver first page.
        pageObjects = paginator.page(1)
        page = 1
    except EmptyPage:
        # If page is out of range (e.g. 9999), deliver last page of results.
        pageObjects = paginator.page(paginator.num_pages)
        page = paginator.num_pages

    page = int(page)
    startPage = 1 + ((page - 1) / pageDisplayCount) * pageDisplayCount
    endPage = startPage + pageDisplayCount - 1

    if totalPageCount < endPage:
        endPage = totalPageCount

    bottomPages = range(startPage, endPage + 1)

    log.info('list method >>> searchData [%s] | page [%d] | startPage [%d] | endPage [%d]', searchData, page, startPage, endPage)

    context = {
        'noticeList':pageObjects,
        'page':page,
        'bottomPages':bottomPages,
        'totalPageCount':totalPageCount,
        'startPage':startPage,
        'endPage':endPage,
        'searchData':searchData
        }

    return render_to_response('notice/list.html', context)

# show notice detail info.
def detail(request, initial_mode="login"):
    page = request.GET.get('page')
    noticeId = request.GET.get('noticeId')
    searchData = request.GET.get('searchData', '')

    log.info('detail method >>> page [%s] | notice id [%s]', page, noticeId)

    notice = Notice.objects.prefetch_related('attachments_set').get(id=noticeId)

    context = {
        'noticeDetail':notice,
        'page':page,
        'searchData':searchData
        }

    return render_to_response('notice/detail.html', context)

