# -*- coding: utf-8 -*-
from django.shortcuts import render
from django.http import HttpResponse, Http404, HttpResponseRedirect
from django.contrib.syndication.views import Feed
from django.contrib.auth.decorators import login_required, user_passes_test

from hotline.basic_auth import basic_http_auth, _auth_required_response
from calls.models import Call, AnswerMan, MO
from calls.forms import CallModelForm, AnswerModelForm, ReasonModelForm
from django.core.urlresolvers import reverse

from django.views.decorators.csrf import ensure_csrf_cookie

from django.core.exceptions import PermissionDenied # HTTP 403 Exception
from django.conf import settings
from django.utils import timezone

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
	return answer_index(request)

from hashlib import md5
def _gen_secret(n):
	SK = settings.SECRET_KEY
	sk_half_size = len(SK) / 2
	return md5('%d%s%d' % (n, md5(SK[:sk_half_size]).hexdigest(), n)).hexdigest() 

@basic_http_auth
def feed(request):
	
	ITEMS_IN_FEED = settings.ITEMS_IN_FEED
	TTL = settings.RSS_FEED_TTL
	URL = settings.SERVER_URL

	try:
		answerman = AnswerMan.objects.get(user=request.user)
	except AnswerMan.DoesNotExist:
		return _auth_required_response()
		
	calls = Call.objects.select_related('citizen', 'mo').filter(answer_man=answerman)[:ITEMS_IN_FEED]
	
	for c in calls:
		c.dt_rfc = c.dt.strftime('%a, %d %b %Y %H:%M:%S %z')
		c.secret = _gen_secret(c.id)
	
	return render(request, 'calls/feed.xml', {'calls': calls, 'ttl': TTL, 'url': URL},  content_type='application/rss+xml')
	

def feed_read_confirmation(request, call_id, digest):
	try:
		call_id = int(call_id)
		if not (digest == _gen_secret(call_id)):
			raise
	except:
		raise PermissionDenied()
	
	try:
		call = Call.objects.get(pk=call_id)
	except Call.DoesNotExist:
		raise Http404()

	if not call.call_received:
		call.call_received = timezone.now()
		call.save()
		
	return HttpResponse(content_type="image/png")
	
	


@user_passes_test(user_is_active)
@login_required
def answer_index(request):
	try:
		answerman = AnswerMan.objects.get(user=request.user)
	except AnswerMan.DoesNotExist:
		return HttpResponseRedirect(settings.LOGIN_URL)
	
	calls = Call.objects.select_related('citizen', 'mo').filter(answer_man = answerman)
	
	return render(request, 'calls/answer_index.html', {'calls': calls})


@login_required
@user_passes_test(user_is_active)
@ensure_csrf_cookie
def answer_detail(request, call_id):
	
	try:
		answerman = AnswerMan.objects.get(user=request.user)
		call = Call.objects.select_related('citizen', 'mo').get(answer_man=answerman, pk=call_id)
	except (Call.DoesNotExist, AnswerMan.DoesNotExist):
		raise PermissionDenied('Вам не положено видеть эту страницу!')
		
	reason_form = None
	answer_form = None
		
	if request.method == "POST":
		#update or create
		answer_form = AnswerModelForm(request.POST, instance=call.get_answer())
		if answer_form.is_valid():
			answer = answer_form.save(commit=False)
			answer.call = call
			answer.dt = timezone.now()
			call.answer_created = answer.dt # hack
			
			if call.is_outdated(): # there must be a reason!
				reason_form = ReasonModelForm(request.POST, instance=call.get_reason())
				if reason_form.is_valid():
					reason = reason_form.save(commit=False)
					reason.call = call
					
					reason.save()
					answer.save()
					
					return HttpResponseRedirect(reverse('calls:answers'))
			else:
				answer.save()
				
				return HttpResponseRedirect(reverse('calls:answers'))
	
	if not answer_form:
		answer_form = AnswerModelForm(instance=call.get_answer())
	
	if not reason_form:
		reason_form = ReasonModelForm(instance=call.get_reason())
	
	call_form = CallModelForm(instance=call)	
	return render(request, 'calls/add_or_change_answer.html', {'call': call, 'call_form': call_form, 'answer_form': answer_form, 'reason_form': reason_form})
	


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

	
	
