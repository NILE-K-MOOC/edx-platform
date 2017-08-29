from django.shortcuts import render_to_response


def test2(request):
    print 'TEST DEF CALLED.'
    return render_to_response('community/comm_faqrequest.html')
