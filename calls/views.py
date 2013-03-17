# -*- coding: utf-8 -*-
from django.shortcuts import render
from django.http import HttpResponse, Http404, HttpResponseRedirect
from django.contrib.syndication.views import Feed
from django.contrib.auth.decorators import login_required, user_passes_test

from hotline.basic_auth import basic_http_auth
from calls.models import Call, AnswerMan, MO
from calls.forms import CallModelForm, AnswerModelForm
from django.core.urlresolvers import reverse

from django.views.decorators.csrf import ensure_csrf_cookie


########## UTILS

from django.utils import simplejson

class JsonResponse(HttpResponse):
    """
        JSON response
    """
    def __init__(self, content, mimetype='application/json', status=None, content_type=None):
        super(JsonResponse, self).__init__(
            content=simplejson.dumps(content),
            mimetype=mimetype,
            status=status,
            content_type=content_type,
        )


def user_is_active(user):
	return user.is_active


@login_required
def index(request):
	try:
		answerman = AnswerMan.objects.get(user=request.user)
	except AnswerMan.DoesNotExist:
		raise HttpResponseRedirect('/operator/') # TODO: raise Http403 and may be more informative message...
	
	return HttpResponseRedirect('/answer/') #TODO: CLEAR HARDCODE!!!


from django.utils import feedgenerator

@user_passes_test(user_is_active)
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



@user_passes_test(user_is_active)
@login_required
def answer_index(request):
	try:
		answerman = AnswerMan.objects.get(user=request.user)
	except AnswerMan.DoesNotExist:
		raise Http404() # TODO: raise Http403 and may be more informative message...
	
	calls = Call.objects.select_related('citizen', 'mo').filter(answer_man = answerman)
	
	return render(request, 'calls/answer_index.html', {'calls': calls})


@login_required
@user_passes_test(user_is_active)
@ensure_csrf_cookie
def answer_detail(request, call_id):
	
	try:
		answerman = AnswerMan.objects.get(user=request.user)
	except AnswerMan.DoesNotExist:
		raise Http404() # TODO: raise Http403 and may be more informative message...
		
	try:
		call = Call.objects.select_related('citizen', 'mo').get(answer_man=answerman, pk=call_id)
	except Call.DoesNotExist:
		raise Http404() # TODO: raise may be more informative message...
		
	if request.method == "POST":
		
		answer = call.get_answer()
		
		if answer:
			#update
			answer_form = AnswerModelForm(request.POST, instance=answer)
			if answer_form.is_valid():
				answer = answer_form.save(commit=False)
				answer.save()
				return HttpResponseRedirect(reverse('calls:answers'))

		else:
			#create
			answer_form = AnswerModelForm(request.POST)
			if answer_form.is_valid():
				answer = answer_form.save(commit=False)
				answer.call = call
				answer.save()
				return HttpResponseRedirect(reverse('calls:answers'))
	else:
		try:
			call.answer
			answer_form = AnswerModelForm(instance=call.answer)
		except:
			answer_form = AnswerModelForm()
	
	call_form = CallModelForm(instance=call)	
	return render(request, 'calls/add_or_change_answer.html', {'call': call, 'form': call_form, 'answer_form': answer_form})

@user_passes_test(user_is_active)
@login_required
def ajax_mo(request):
	
	#TODO: error messages!!!!
	
	try:
		call_id = int(request.POST['call_id'])
		if request.POST['mo_id']:
			mo_id = int(request.POST['mo_id'])
		else:
			mo_id = None
	except:
		raise Http404(1) # TODO: raise more informative message...
	
	try:
		answerman = AnswerMan.objects.get(user=request.user)
	except AnswerMan.DoesNotExist:
		raise Http404(2) # TODO: raise Http403 and may be more informative message...
		
	try:
		call = Call.objects.get(answer_man=answerman, pk=call_id)
	except Call.DoesNotExist:
		raise Http404(3) # TODO: raise may be more informative message...
		
	if not mo_id:
		mo = None
	else:
		try:
			mo = MO.objects.get(pk=mo_id)
		except MO.DoesNotExist:
			raise Http404(4) # TODO: raise may be more informative message...
	call.mo = mo
	call.save()
	
	return JsonResponse({'success': True})

@user_passes_test(user_is_active)
@login_required
def ajax_contents(request):
	#TODO: error messages!!!!
	try:
		call_id = int(request.POST['call_id'])
		contents = request.POST['contents']
	except e:
		raise Http404(e) # TODO: raise more informative message...


	try:
		answerman = AnswerMan.objects.get(user=request.user)
	except AnswerMan.DoesNotExist:
		raise Http404(2) # TODO: raise Http403 and may be more informative message...

	try:
		call = Call.objects.get(answer_man=answerman, pk=call_id)
	except Call.DoesNotExist:
		raise Http404(3) # TODO: raise may be more informative message...
		
	call.contents = contents
	call.save()
	
	return JsonResponse({'success': True})

	
	