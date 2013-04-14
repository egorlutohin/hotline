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


png_img_b64 = \
"""iVBORw0KGgoAAAANSUhEUgAAAKEAAAAiCAMAAAAAq0nyAAAAAXNSR0IArs4c6QAAAARnQU1BAACx
jwv8YQUAAAMAUExURQAGAAAJAAAMAAYsHQwoHREmHRUkHRQoHxglHiVMPCtKOypJPCpMPC5IOy1I
PTFGPTdDPzVEPjFIPjhDPzlGPzRHQTVIQjhHQEtrXkltXk5pXkxsXlJmXlNoX01tYG2Sg3GOgnWN
gnaOhHmLhHGQg2+3knC2kna5l3u9m33AnYy1oY26o4+8qJW3p5e2qZO5qZu0qZi4q6Ovq6CxqYDA
nYTGo4TKpY/GqYjIpo3IqI3TsY7ZspTErJPMrJTOsZ/BsJzOs5TTs5LeuJ/Utp7UuJjZu6TDtKjE
tavHuKrPvqDRtqHTuKTZu6vTvqjavbDMvbDTv57ow6fYwqvSwK/VwK3awbLTwrLVwbbXxLfXyLPY
xbPdxbHbyLbbyrTdyLnVx7rWyr3Xyrray7rdybvdzb3Zyr/azLzdzKTlxqTkyKHqxq3kzKrrzK/r
0Kvxz63z0a761rXizLrjzLTs07rj0bnm0bzi0L7l077n1bvq1b3t2bLy1rX22rD61rL42bvz27j4
3cHdzsTcz8Lf0sXf1MDjzsDg08Ph1cDm0sHl1cbh0sbj1cTk18Xm2cTo1cHq2MHt2sLt3MXq2cbq
3MXs2sXt3Mnh1Mnm1crm2s3m2s3m3Mnp2snp3Mvu2srs3czp2s3p3czs2szs3cDw3NLl2tDm3dfn
3dDo29Ho3tDt29Hu3dTp39Tv3tnm3tno3tXw38/q4c7u4c7w4tLn4NHr4NHt4dTp4NTt4dbt5djn
4Nnp4Njt4tnu5d7r4t3s4t3s5dDw4tLw5NTw4dXy5tb06Nrx5dj05t3y59vy6Nj06Nv17N3y6tz1
6t327d747t/58ODt5eDx5+Lz6uD06eD37uTx6efy7OX06uX27OD57urz7uj17ej47uT38eH58eL8
8+X58uf69Of89en38O738u739Or58Oj79ej88+n89e348u369O388u389uv7+Ov++O3++PH38/D6
8vH69fL89fT69vb99vL++ff7+vT++vb+/Pj9+vn9/Pz++/3+/gAAAPIpazwAAAAJcEhZcwAADsMA
AA7DAcdvqGQAAAAadEVYdFNvZnR3YXJlAFBhaW50Lk5FVCB2My41LjEwMPRyoQAACOtJREFUWEfN
WAt8W2UVv7e2Vaw2zvfCsE0bZaIsVRw+N53OoWzzXR+AYz5AQHCMyaTtSIYTHQLbTXIvuOSS3uYu
GjoHRu2mHWC7Lm6RJp20c5ubsYimNmlZIZk1TejP//m+vNpl7PH74Y+T+z3OOf/znf937pc+PmG6
RLKZbDaTb2lM2TxTtJX6zzxH6FnEpktyUgTWzWZLSAn5eTaTPnny+TiXJB/+OUPLW3MYDM/hk5fi
PFEE8MVyq9H8uWIA883Gku1fiWQynS6QzDPMpOLHDh18ovuRc5OdZeDd3XyVM64FAMfORP6++/GD
h47FkxlevBzDdPwvj+984tAz8VQilognxsbj49hfAn2M9hnDbsfITjb0NMYSY3GuAzVeqMd4AjJW
rE4MsbTWGI2xRGIcPrIRgqBURdLzI82PHz748+6n4idZHRnDzMnYH3b+tfTll57O089nnJezCDkz
niPoJD6zfc8RVkZimE0ee6R76twJngWn84Rks1MTTz6w/TBRJIbp4zu2lxKczTU7zS1l7EUTZoUS
kZUFUZePJS8a1YdLDpMrGsfyZwoEn+53Xe8/kmIM/xvf88On8N1hYVMQdDQpzKem0szMvacXhuKS
JuFhpE2ls9QVnTnQJIBTk1N4uBdaahIyPjIaDmqbVu+OZYhh8vCD1+2fBGRycmJi4sSJiXF86HkW
KuajTBun2YnR0RMwToyiPTtBKoRiYEdHn9HREWYke1GZgJHZR0dGsMy/6eEGbsUw/DT5xjEfHo4O
h/u7tJ98bdOfk1lhOhPfc+1djw2PjAyP/CM6HB34ezSKITr8N4w0BZ70o0fD0YEonshQNBKJDg1F
h7g+MDQUCcMcDQ9Ejg4MwBeNhgEBJhKNQB8g91D4aDiMBvvQUH8kQk/4T+EBGDGEw5FQZCDcHwmH
+6GEQqG+vV71vm9/eUc8LUynj2z77F27Hgse6A+F/hgK7evr60MLBl/55idDfaEDb6k+ENrX2wd7
CHaE7oMVD+kQ1pEDHYXyHnrvvr5efIrSAwjpaGwAoKgzIMP3UuvqCXi96v3rP33v4KQwnRz86aeu
f8D/266ugLenpyfAW9fuqjf9LtDbs/uNr9rdE+iC9PIhL4FAAOtwU6CH9dD6uB6A6dcB+pBwk5dH
5kIwenLBOTODclE9qsfjVh0/+OJ3gikhmwped8U3fvQzFeLJizeg+asM/oDHo82p1jzeTv8uv+b1
an7ILo0Eitbl9ZLhV94AG8nk37HD7/f54S+s5WFhmur1+yBw5UYPOX5T1Fl6dyFMdji23nHNVXvH
hEz80a9ece2me+93qE4S2SPLsuJUtSqDT1Xd2uuqVXf7a0VRaIAiCoIgiiafWK+q9aJJVY1QawGr
hd2kqTUEEMRfwE/LyIqiyLJqEkXRqKrAULRGPdBuHm1sr+WrqqrTQTFIjjinLElbW9au7IyBYedX
lq3edN8Wh4MDOAoM5/h8msv3BjA0GFRtntCkbiNmqtBIDF1VQqPLKDa53aJRq63V2o0AyE543W4X
/MjAxdEg1GNvtZpb3SaYVBkIbAloilYXCPMY3k3JCU6dYrezeevtKzuI4cOfW7b6x/dsadm6Nb+o
JNmdWhX2hdIJ1aoDudXLBLAS653EgRiaDDQaVdRI1cQmrb1JaHRKdlUwuR0ayuvmCSXJXTUPtOrF
Jgfs9U7JAYZOdzuihXkut9ooqGBoLmyIQux2HtrashwMX4h7Vy775vp7ZhDEVtRKg4b07jnVqqL5
fI0CGGqiWbE7iZlZrQQjsHbStnEmXACAoSSLJlkCQ58Lb42luZTZLxVMDpniiaHL5ZsnNjUKl/lc
vvcK9Q4wdBSrU5jptgLDj359/R0trVul1taCFwxrVexCNlQ7FSNqSTXUxDrFrrAa1tdoxHCBQhHO
C1HtJqEBCjGUVao+ThYrjEUAZ0lGD3udghl7OSbaNL0ksc5J60p6PjcmNkmH2DhDnMOVllXfb2lp
BcFWG4neqtsktfLVsqTbZEOVasFLcDcJZlrJbrOLYNhYaUEtm6gmNpuEUZaJoU1nNXSLZqciG0WL
hLzE0CZZxAay19kl7NApKRdSDRfgJIC9AuZ2rMOT40Hjsi7H8EuXXHM7GOb4cZ/krKxh2Q1VnjpR
k+WGPENJbPSLhloJoya+1Ul1axDdsmIWGhWbTRFNig6GqJVPrKN0SqURPMxikyQRExviPJLipmjs
i/bA7WVkw7rlXqrh3qsuaV5LDEsxOjGkBK+vUixYDT8jjPSWdZtODMX36LrY4JmLrwiOA2qo4SfR
RYxhg66rYoOmaheJFlYUM/O+BgX2EBNdaITTLC5g0VqtaLGfhuEG6w0rwTD7fPBb7/rC2nUtMwgi
1SsuoGLrNZW6zo5ZTYXFU0EMK8yeiguQr8Jst79NrKio8TjnEsAgvhv4CrNuUypE2EULf1tKHbxz
sV1dYfHQ4K9TdJ3CRI/O7bNl40ar9ZPN+Ik9ndp/90eWfnfdunJlJoqMJ5P8SSlMisdmBiAXVTxO
7HQVhFbK+UpWLcewbckq/Nab/s+RB69cDIZtGwqgDcVpWd4v6i8Te6b1yiTZuMFqtX5v8Wb6yyET
/2Xz+2+8hTGk52UgIAF+VuuSFd4Y/vqaTg3e/bHFN9/S1gZuLwuCOX7WGxfdFqS/YKmIVy9acvMa
YvjSi5VSsG6mwJR/WP2s1ps+0NxxPM3+k0odbm/+4MIb1rS1EYY3gvBSnyIv5isfcT7WNR9auGLL
YPIFxjCTGmy/etH7Fn7482tuvfPW/5PcWchUnBVS3/Txy+cvat6yP5H7b3Q6kzzSedtnllw+f/7F
7zhF3n6q6aW2XPzOhYtWrO0YJIK5WxHc2uzv3Ly2eTmXpUsLbWnJnNln+D+x/EoA8hg2mY0/V50l
aF612Rs8zm9uCjdLydhgcHdnB5eHZrVSWzl/Dv/Q7Liz1XNpWd6Ojoc7Hw0OxpLpF9g9QuF2Dpc3
ydztTgy3O7Mb3f6QLT+Ww8BGckrs2djY7VK+xeOpVCZ/nVFkSF+ZM99anu9t5znGldz3/A+hxm45
LDjz2AAAAABJRU5ErkJggg=="""

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
		
	return HttpResponse(png_img_b64.decode('base-64'), content_type="image/png")
	
	


@user_passes_test(user_is_active)
@login_required
def answer_index(request):
	try:
		answerman = AnswerMan.objects.get(user=request.user)
	except AnswerMan.DoesNotExist:
		return HttpResponseRedirect(settings.LOGIN_URL)
	
	show_mode = request.GET.get('show')
	calls_all = Call.objects.select_related('citizen', 'mo').filter(answer_man = answerman)
	calls_wo_answer = calls_all.filter(answer_created__isnull=True)
	calls_wo_answer_outdated = calls_all.filter(answer_created__isnull=True).filter(deadline__lte=timezone.now())
	
	counters = {}
	counters['all'] = calls_all.count()
	counters['wo_answer'] = calls_wo_answer.count()
	counters['wo_answer_outdated'] = calls_wo_answer_outdated.count()
	
	if show_mode =='wo_answer':
		calls = calls_wo_answer
	elif show_mode == 'wo_answer_outdated':
		calls = calls_wo_answer_outdated
	else:
		show_mode = 'all'
		calls = calls_all
		
	
	return render(request, 'calls/answer_index.html', {'calls': calls, 'counters': counters, 'show_mode': show_mode})


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
			return JsonResponse({'success': False, 'message': "Медицинская организация не выбрана"})
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

	
	
