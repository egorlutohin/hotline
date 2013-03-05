# -*- coding: utf-8 -*-
from django.shortcuts import render
from django.http import HttpResponse, Http404

from django.contrib.syndication.views import Feed

from hotline.basic_auth import basic_http_auth
from calls.models import Call

def index(request):
	return HttpResponse('Hello index!')


from django.utils import feedgenerator

@basic_http_auth
def feed(request):
	
	user = request.user
	
	try:
		answerman = user.answerman
	except:
		raise Http404()
		
	calls = Call.objects.filter(answer_man=answerman)
	
	f = feedgenerator.Atom1Feed(
		title=u"%s: обращения на горячую линию МЗ НСО" % answerman.print_answerman_name(),
		link=u"",
		description=u"",
		language=u"ru",
		author_name=u"",
		feed_url=u""
	)
	
	
	for call in calls:
		f.add_item(title=u"Обращение #%d от %s" % (call.number(), call.citizen),
			link=u"request #%d" %  call.number(),
			pubdate=call.dt,
			description=call.contents
		)	
	
	return HttpResponse(f.writeString('UTF-8'))
