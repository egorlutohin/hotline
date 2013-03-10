# -*- coding: utf-8 -*-
from django.shortcuts import render
from django.http import HttpResponse, Http404
from django.contrib.syndication.views import Feed
from django.contrib.auth.decorators import login_required, user_passes_test

from hotline.basic_auth import basic_http_auth
from calls.models import Call, AnswerMan

def index(request):
	return HttpResponse('Hello index!')


from django.utils import feedgenerator

@basic_http_auth
def feed(request):
	
	user = request.user
	
	try:
		answerman = AnswerMan.objects.get(user=user)
	except AnswerMan.DoesNotExist:
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


def allowed_to_answer(user):
	# TODO!
	return user.is_active # and user in answer_list

@user_passes_test(allowed_to_answer)
@login_required
def answer_index(request):
	return render(request, 'calls/answer_index.html')