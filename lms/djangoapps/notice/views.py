#!/usr/bin/env python
# -*- coding: utf-8 -*-

import logging

from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.http import HttpResponse, HttpResponseRedirect, Http404
from django.shortcuts import get_object_or_404
from edxmako.shortcuts import render_to_response, render_to_string

from notice.forms import NoticeForm
from notice.models import Notice

import json

from django.http import HttpResponse, JsonResponse
from django.core import serializers
from django.forms.models import model_to_dict

log = logging.getLogger(__name__)

# notice list select with pagging.
def list(request, initial_mode="login"):
    #log.info("request user info [{0}]".format(request.user.is_active))
    #log.info("request header [{0}]".format(request.META["HTTP_USER_AGENT"]))
    
    #if not request.user.is_active:
    #    return HttpResponseRedirect('/')
        
    pageRowCount = 10
    pageDisplayCount = 10
    startPage = 1
    endPage = 1
    
    searchData = request.GET.get('searchData', '')
    page = request.GET.get('page')
	
    noticeList = Notice.objects.order_by('-id')
    
    if searchData:
        noticeList = noticeList.filter(title__icontains=searchData, is_popup=0)
        
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
def detail(request):
    #log.info("request user info [{0}]".format(request.user.is_active))
    
    #if not request.user.is_active:
    #    return HttpResponseRedirect('/')
        
    page = request.GET.get('page')
    noticeId = request.GET.get('noticeId')
    searchData = request.GET.get('searchData', '')
    
    log.info('detail method >>> page [%s] | notice id [%s]', page, noticeId)
    
    #notice = Notice.objects.get(id=noticeId)
    notice = get_object_or_404(Notice, id=noticeId)
    
    #log.info('detail method >>> get_object_or_404 after notice title [%s]', notice.title)
    #log.info('detail method >>> get_object_or_404 after notice contents [%s]', notice.contents)
    
    context = {
        'noticeDetail':notice,
        'page':page,
        'searchData':searchData
	}
    
    return render_to_response('notice/detail.html', context)
    
# creating notice info.
def create(request):
    if not request.user.is_staff or not request.user.is_superuser:
        raise Http404
        
    form = NoticeForm(request.POST or None)
    
    log.info('create method >>> is_valid [%s] | user id [%s]', form.is_valid(), request.user)
    
    if form.is_valid():
        instance = form.save(commit=False)
        instance.writer = request.user
        instance.save()
        return HttpResponseRedirect('/notice_list')
    
    context = {
        'form':form
	}
    
    return render_to_response('notice/form.html', context)
    
def update(request):
    if not request.user.is_staff or not request.user.is_superuser:
        raise Http404
        
    mode = ""
    page = ""
    noticeId = ""
    
    if request.method == "GET":
        mode = request.GET.get('mode')
        page = request.GET.get('page')
        noticeId = request.GET.get('noticeId')
    elif request.method == "POST":
        mode = ""
        page = request.POST.get('page')
        noticeId = request.POST.get('noticeId')    

    log.info('update method >>> mode [%s] | page [%s] | notice id [%s]', mode, page, noticeId)
    
    notice = get_object_or_404(Notice, id=noticeId)
    
    if mode != 'update':
        #log.info('update method >>> POST get_object_or_404 after notice title [%s]', notice.title)
        form = NoticeForm(request.POST or None, instance=notice)
    else:
        log.info('update method >>> GET')
        form = NoticeForm(request.GET or None, instance=notice)
        
    if form.is_valid():
        instance = form.save(commit=False)
        """
        log.info('update method >>> form data id [%s]', instance.id)
        log.info('update method >>> form data title [%s]', instance.title)
        log.info('update method >>> form data contents [%s]', instance.contents)
        """
        instance.save()
        redirectUrl = "notice_detail?noticeId=%s&page=%s" %(instance.id, page)
        return HttpResponseRedirect(redirectUrl)
    
        
    context = {
        'page':page,
        'noticeId':noticeId,
        'notice':notice,
        'mode':'update',
        'form':form
    }
    
    return render_to_response('notice/form.html', context)
    
def delete(request):
    if not request.user.is_staff or not request.user.is_superuser:
        raise Http404
        
    noticeId = request.GET.get('noticeId')
    
    notice = get_object_or_404(Notice, id=noticeId)
    notice.delete()

    return HttpResponseRedirect('/notice_list')

def checkPopup(request):
    #if not request.user.is_staff or not request.user.is_superuser:
    #    raise Http404
        
    #noticeList = Notice.objects.filter(is_display=1)
    from datetime import datetime
    now = datetime.now()
    noticeList = Notice.objects.filter(end_date__gte=now).filter(is_display=1)

    log.info(noticeList.count())
    
    if noticeList.count() > 0 :
    
        notice = noticeList[0]

        context = {
            'detail_url':notice.detail_url,
            'contents':notice.contents,
            'id':notice.id,
            'title':notice.title
        }

    else :
       context = {'id': ''}

    return JsonResponse(context, safe=False)
    #return HttpResponseRedirect('/notice_list')

