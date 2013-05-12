from django.http import HttpResponse
from django.shortcuts import render
from calls.models import Call, MO
from django.contrib.auth.decorators import permission_required

#~ from django.contrib.admin import widgets 
from django.contrib.admin.widgets import AdminDateWidget
from django.utils import timezone
from datetime import date, datetime, timedelta

from django import forms

class PeriodForm(forms.Form):
	start_date = forms.DateField(label='с', widget = AdminDateWidget)
	end_date = forms.DateField(label='по', widget = AdminDateWidget)
	
@permission_required('reports.can_view', raise_exception=True)
def std(request):
	"Стандартный отчет"
	
	default_tz = timezone.get_default_timezone()
	
	period_form = PeriodForm(request.GET)
	
	if period_form.is_valid():
		_ = period_form.cleaned_data['start_date']
		sd = datetime(_.year, _.month, _.day, 0, 0, 0, tzinfo = default_tz).astimezone(timezone.utc)
		_ = period_form.cleaned_data['end_date']
		ed = datetime(_.year, _.month, _.day, 23, 59, 59, tzinfo = default_tz).astimezone(timezone.utc)
	else:
		now = date.today()
		start_month = date(now.year, now.month, 1)
		sd = datetime(start_month.year, start_month.month, start_month.day, 0, 0, 0, tzinfo = default_tz).astimezone(timezone.utc)
		ed = datetime(now.year, now.month, now.day, 23, 59, 59, tzinfo = default_tz).astimezone(timezone.utc)
		period_form = PeriodForm({'start_date': sd.astimezone(default_tz).strftime("%d.%m.%Y"), 'end_date': ed.astimezone(default_tz).strftime("%d.%m.%Y")})
		
	counters = {}
	
	from django.db import connection, transaction
	cursor = connection.cursor()
	
	query = "select count(*) as total from calls_call  where dt >= %s and dt <= %s"
	cursor.execute(query, [sd.strftime('%Y-%m-%d %H:%M:%S'), ed.strftime('%Y-%m-%d %H:%M:%S')])
	result = cursor.fetchall()
	counters['calls_total'] = result[0][0]
	
	query = "select  count(*)  from calls_call  where dt >= %s and dt <= %s and answer_created is not null"
	cursor.execute(query, [sd.strftime('%Y-%m-%d %H:%M:%S'), ed.strftime('%Y-%m-%d %H:%M:%S')])
	result = cursor.fetchall()
	counters['answers_total'] = result[0][0]
	counters['answers_total_percent'] = float(counters['answers_total']) / (counters['calls_total'] or 1) * 100
	
	query = "select count(*) from calls_call inner join answers_answer on call_id = id where calls_call.dt >=%s and calls_call.dt <=%s and validity=1"
	cursor.execute(query, [sd.strftime('%Y-%m-%d %H:%M:%S'), ed.strftime('%Y-%m-%d %H:%M:%S')])
	result = cursor.fetchall()
	counters['validity_calls'] = result[0][0]
	counters['validity_calls_percent'] = float(counters['validity_calls']) / (counters['answers_total'] or 1) * 100
	
	query = "select code, name, counter from answers_callprofile left join (select profile_id, count(*) as counter from calls_call inner join answers_answer on call_id = calls_call.id  where calls_call.dt >=%s and calls_call.dt <= %s group by profile_id) as r on answers_callprofile.id = r.profile_id order by code"
	cursor.execute(query, [sd.strftime('%Y-%m-%d %H:%M:%S'), ed.strftime('%Y-%m-%d %H:%M:%S')])
	result = cursor.fetchall()
	
	counters['calls_by_profile'] = []
	for l in result:
		counters['calls_by_profile'].append(
			{'code': l[0], 
			 'name': l[1], 
			 'counter': l[2] or 0, 
			 'percent_counter': float(l[2] or 0) / (counters['answers_total'] or 1) * 100
			}
		)
	
	query = "select code, name, counter from answers_action left join (select action_id, count(*) as counter from calls_call inner join answers_answer on call_id = id where calls_call.dt >=%s and calls_call.dt <=%s group by action_id) as r on answers_action.id = r.action_id order by code"
	cursor.execute(query, [sd.strftime('%Y-%m-%d %H:%M:%S'), ed.strftime('%Y-%m-%d %H:%M:%S')])
	result = cursor.fetchall()

	counters['answers_by_action'] = []
	for l in result:
		counters['answers_by_action'].append(
			{'code': l[0],
			 'name': l[1],
			 'counter': l[2] or 0,
			 'percent_counter': float(l[2] or 0) / (counters['answers_total'] or 1) * 100
			}
		)
		
	query = "select count(*) from calls_call  where calls_call.dt>=%s and calls_call.dt<=%s and deadline>=answer_created"
	cursor.execute(query, [sd.strftime('%Y-%m-%d %H:%M:%S'), ed.strftime('%Y-%m-%d %H:%M:%S')])
	result = cursor.fetchall()
	counters['answers_not_outdated'] = result[0][0]
	counters['answers_not_outdated_percent'] = float(counters['answers_not_outdated']) / (counters['answers_total'] or 1) * 100
	
	return render(request, 'reports/std.html', {'pf': period_form, 'start_date': sd, 'end_date': ed, 'counters': counters }, )
	
class AnalysisForm(PeriodForm):
	type = forms.TypedChoiceField(choices=[('', 'Любой'),]+MO.TYPE.choices(), required=False, label='тип МО', coerce=int)

@permission_required('reports.can_view', raise_exception=True)	
def analysis(request):
	"Анализ"
	
	default_tz = timezone.get_default_timezone()
	
	params_form = AnalysisForm(request.GET)
	
	if params_form.is_valid():
		_ = params_form.cleaned_data['start_date']
		sd = datetime(_.year, _.month, _.day, 0, 0, 0, tzinfo = default_tz).astimezone(timezone.utc)
		_ = params_form.cleaned_data['end_date']
		ed = datetime(_.year, _.month, _.day, 23, 59, 59, tzinfo = default_tz).astimezone(timezone.utc)
	else:
		now = date.today()
		start_month = date(now.year, now.month, 1)
		sd = datetime(start_month.year, start_month.month, start_month.day, 0, 0, 0, tzinfo = default_tz).astimezone(timezone.utc)
		ed = datetime(now.year, now.month, now.day, 23, 59, 59, tzinfo = default_tz).astimezone(timezone.utc)
		params_form = AnalysisForm({'start_date': sd.astimezone(default_tz).strftime("%d.%m.%Y"), 'end_date': ed.astimezone(default_tz).strftime("%d.%m.%Y")})
	
	from django.db import connection, transaction
	cursor = connection.cursor()
	
	
	if params_form.is_valid() and params_form.cleaned_data['type']:
		query = "select mo_id,  profile_id, count(*) as answers_count from answers_answer as t1 left join calls_call as t2 on t1.call_id=t2.id left join calls_mo as t3 on t2.mo_id = t3.id  where t1.dt >= %s and t1.dt <= %s and t3.type=%s group by mo_id, profile_id order by mo_id, profile_id"
		cursor.execute(query, [sd.strftime('%Y-%m-%d %H:%M:%S'), ed.strftime('%Y-%m-%d %H:%M:%S'), params_form.cleaned_data['type']])
	else:
		query = "select mo_id, profile_id, count(*) as answers_count from answers_answer as t1 left join calls_call as t2 on t1.call_id=t2.id where t1.dt >= %s and t1.dt <= %s group by mo_id, profile_id order by mo_id, profile_id"
		cursor.execute(query, [sd.strftime('%Y-%m-%d %H:%M:%S'), ed.strftime('%Y-%m-%d %H:%M:%S')])
	
	result = cursor.fetchall()
	
	mo_dict = {}
	cursor.execute("select id, name_short from calls_mo order by id")
	for l in cursor.fetchall():
		mo_dict[l[0]] = l[1]
		
	profile_dict = {}
	cursor.execute("select t1.id, t1.name, t1.code, t2.code from answers_callprofile as t1 left join answers_callprofilegroup as t2 on t1.group_id = t2.id order by t1.code")
	color = ['#fcd5b4', '#d99795', '#e5e0ec', '#b6dde8', '#93cddd'] # TODO: move to template tag
	cl = len(color)
	for l in cursor.fetchall():
		profile_dict[l[0]] = {'code': l[2], 'name': l[1], 'color': color[(l[3] - 1) % cl ]}

	td = {} # table dictionary
	for mo_id, profile_id, ac in result:
		if not td.has_key(mo_id):
			td[mo_id] = {}
		td[mo_id][profile_id] =  ac
		
	rt = [] # result table
	k = {}
	ss = 0 # super sum
	for i in td:
		l = []
		rt.append(l)
		l.append(mo_dict.get(i, ""))
		s = 0;
		for j in profile_dict:
			s+=td[i].get(j, 0)
			l.append(td[i].get(j, ""))
		#~ l.append(s)
		ss+=s
		k[repr(l)] = s
		
	rt.sort(key=lambda i: k[repr(i)], reverse=True)
	
	
	le = len(profile_dict)
	t = [0] * le
	for l in rt:
		for i in xrange(1, le + 1):
			if l[i]:
				t[i-1]+= l[i]
			
	
			
	# TODO: maybe using regroup tag in template
	return render(request, 'reports/analysis.html', {'mo': mo_dict, 'profile': profile_dict, 'table': rt, 'pf': params_form, 'start_date': sd, 'end_date': ed, 'total': t, 'total_sum': ss})
	

class R3Form(PeriodForm):
	mo = forms.ModelChoiceField(label="МО" ,queryset=MO.objects.all(), empty_label="Все", required=False)
	validity = forms.TypedChoiceField(label="обоснованность", required=False, choices=(("", "Не важно"),(1, "Да"),(0, "Нет")), coerce=int, empty_value=None)

from answers.models import Answer

@permission_required('reports.can_view', raise_exception=True)
def reportthree(request):
	
	default_tz = timezone.get_default_timezone()
	params_form = R3Form(request.GET)
	
	answers = Answer.objects.select_related('call', 'call__citizen', 'call__mo', 'call__answer_man', 'call__answer_man__department', 'call__answer_man__user', 'profile', 'action').all().order_by('profile__code')
	if params_form.is_valid():
		_ = params_form.cleaned_data['start_date']
		sd = datetime(_.year, _.month, _.day, 0, 0, 0, tzinfo = default_tz).astimezone(timezone.utc)
		_ = params_form.cleaned_data['end_date']
		ed = datetime(_.year, _.month, _.day, 23, 59, 59, tzinfo = default_tz).astimezone(timezone.utc)
		
		answers = answers.filter(call__dt__gte=sd, call__dt__lte=ed)
		
		if params_form.cleaned_data['mo']:
			answers = answers.filter(call__mo=params_form.cleaned_data['mo'])
		#~ print params_form.cleaned_data['validity']
		if params_form.cleaned_data['validity'] is not None:
			answers = answers.filter(validity=bool(params_form.cleaned_data['validity']))
	else:
		now = date.today()
		start_month = date(now.year, now.month, 1)
		sd = datetime(start_month.year, start_month.month, start_month.day, 0, 0, 0, tzinfo = default_tz).astimezone(timezone.utc)
		ed = datetime(now.year, now.month, now.day, 23, 59, 59, tzinfo = default_tz).astimezone(timezone.utc)
		params_form = R3Form({'start_date': sd.astimezone(default_tz).strftime("%d.%m.%Y"), 'end_date': ed.astimezone(default_tz).strftime("%d.%m.%Y")})
		answers = answers.filter(call__dt__gte=sd, call__dt__lte=ed)
	
	return render(request, 'reports/reportthree.html', {'answers': answers, 'pf': params_form, 'start_date': sd, 'end_date': ed})

@permission_required('reports.can_view', raise_exception=True)
def answermans(request):
	"Отчет по исполнителям"
	
	default_tz = timezone.get_default_timezone()
	
	period_form = PeriodForm(request.GET)
	
	if period_form.is_valid():
		_ = period_form.cleaned_data['start_date']
		sd = datetime(_.year, _.month, _.day, 0, 0, 0, tzinfo = default_tz).astimezone(timezone.utc)
		_ = period_form.cleaned_data['end_date']
		ed = datetime(_.year, _.month, _.day, 23, 59, 59, tzinfo = default_tz).astimezone(timezone.utc)
	else:
		now = date.today()
		start_month = date(now.year, now.month, 1)
		sd = datetime(start_month.year, start_month.month, start_month.day, 0, 0, 0, tzinfo = default_tz).astimezone(timezone.utc)
		ed = datetime(now.year, now.month, now.day, 23, 59, 59, tzinfo = default_tz).astimezone(timezone.utc)
		period_form = PeriodForm({'start_date': sd.astimezone(default_tz).strftime("%d.%m.%Y"), 'end_date': ed.astimezone(default_tz).strftime("%d.%m.%Y")})
	
	from django.db import connection, transaction
	cursor = connection.cursor()
	
	query = "select last_name, first_name, name, calls_count, answers_count, outdated_count from calls_answerman  left join auth_user on calls_answerman.user_id = auth_user.id left join calls_department on calls_answerman.department_id = calls_department.id \
                 left join (select answer_man_id, count(*) as calls_count from calls_call where dt >= %s and dt <= %s group by answer_man_id) as calls_count_t on calls_answerman.id = calls_count_t.answer_man_id \
                 left join (select answer_man_id, count(*) as answers_count from calls_call where dt >= %s and dt <= %s and answer_created is not null group by answer_man_id) as answers_count_t on calls_answerman.id = answers_count_t.answer_man_id \
                 left join (select answer_man_id, count(*) as outdated_count from calls_call where dt >= %s and dt <= %s and answer_created >=deadline group by answer_man_id) as outdated_count_t on calls_answerman.id = outdated_count_t.answer_man_id \
                 order by department_id, last_name"

	cursor.execute(query, [sd.strftime('%Y-%m-%d %H:%M:%S'), ed.strftime('%Y-%m-%d %H:%M:%S')] * 3)
	
	#~ result = 
	rt = []
	total_counters = {}
	c = total_counters
	c['total_calls'] = 0
	c['total_answers'] = 0
	c['total_outdated'] = 0
	for l in cursor.fetchall():
		c['total_calls']+=l[3] or 0
		c['total_answers']+=l[4] or 0
		c['total_outdated']+=l[5] or 0
		rt.append({'last_name': l[0], 'first_name': l[1], 'department': l[2], 'calls_count': l[3] or 0, 'answers_count': l[4] or 0, 'outdated_count': l[5] or 0})
	
	return render(request, 'reports/answermans.html', {'rt': rt, 'start_date': sd, 'end_date': ed, 'pf': period_form, 'total_counters': total_counters})
	
	
	

	

