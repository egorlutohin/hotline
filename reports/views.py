from django.http import HttpResponse
from django.shortcuts import render
from calls.models import Call

#~ from django.contrib.admin import widgets 
from django.contrib.admin.widgets import AdminDateWidget
from django.utils import timezone
from datetime import date, datetime, timedelta

from django import forms

class PeriodForm(forms.Form):
	start_date = forms.DateField(label='с', help_text="01.03.2013", widget = AdminDateWidget)
	end_date = forms.DateField(label='по', help_text="31.03.2013", widget = AdminDateWidget)


def std(request):
	"Стандартный отчет"
	
	period_form = PeriodForm()
	now = date.today()
	start_date = date(now.year, now.month, 1)
	end_date = date(now.year, now.month + 1, 1) - timedelta(days=1)
	
	total = Call.objects.filter(dt__gte=start_date, dt__lte=end_date).count()
	
	return render(request, 'reports/std.html', {'form': period_form },)
	
def analysis(request):
	"Анализ"
	
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
	
	query = "select mo_id, profile_id, count(*) as answers_count from answers_answer as t1 left join calls_call as t2 on t1.call_id=t2.id where t1.dt >= %s and t1.dt <= %s group by mo_id, profile_id order by mo_id, profile_id"
	
	cursor.execute(query, [sd.strftime('%Y-%m-%d %H:%M:%S'), ed.strftime('%Y-%m-%d %H:%M:%S')])
	
	result = cursor.fetchall()
	
	mo_dict = {}
	cursor.execute("select id, name_short from calls_mo order by id")
	for l in cursor.fetchall():
		mo_dict[l[0]] = l[1]
		
	profile_dict = {}
	cursor.execute("select id, name, code from answers_callprofile order by code")
	for l in cursor.fetchall():
		profile_dict[l[0]] = "%s - %s" % (l[2], l[1])

	td = {} # table dictionary
	for mo_id, profile_id, ac in result:
		if not td.has_key(mo_id):
			td[mo_id] = {}
		td[mo_id][profile_id] =  ac
		
	rt = [] # result table
	for i in td:
		l = []
		rt.append(l)
		l.append(mo_dict.get(i, ""))
		for j in profile_dict:
			l.append(td[i].get(j, ""))
			
	
			
	# TODO: maybe using regroup tag in template
	return render(request, 'reports/analysis.html', {'mo': mo_dict, 'profile': profile_dict, 'table': rt, 'pf': period_form, 'start_date': sd, 'end_date': ed})

from answers.models import Answer
def reportthree(request):
	
	answers = Answer.objects.select_related('call', 'call__citizen', 'call__mo', 'call__answer_man', 'call__answer_man__department', 'call__answer_man__user', 'profile', 'action').all().order_by('profile__code')
	
	return render(request, 'reports/reportthree.html', {'answers': answers})
	
	
	

	

