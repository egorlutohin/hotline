﻿from django.http import HttpResponse
from django.shortcuts import render
from calls.models import Call

from django.contrib.admin import widgets 
from django.utils import timezone
from datetime import date, datetime, timedelta

from django import forms

class PeriodForm(forms.Form):
	start_date = forms.DateField(label='с', help_text="01.03.2013")
	end_date = forms.DateField(label='по', help_text="31.03.2013")


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
	
	period_form = PeriodForm(request.GET)
	
	if period_form.is_valid():
		sd = period_form.cleaned_data['start_date']
		ed = period_form.cleaned_data['end_date']
	else:
		now = date.today()
		sd = date(now.year, now.month, 1)
		ed = date(now.year, now.month + 1, 1) - timedelta(days=1)
		period_form = PeriodForm({'start_date': sd.strftime("%d.%m.%Y"), 'end_date': ed.strftime("%d.%m.%Y")})
	
	from django.db import connection, transaction
	cursor = connection.cursor()
	
	query = "select mo_id, profile_id, count(*) as answers_count from answers_answer as t1 left join calls_call as t2 on t1.call_id=t2.id where t1.dt >= %s and t1.dt <= %s group by mo_id, profile_id order by mo_id, profile_id"
	
	cursor.execute(query, [sd.strftime("%Y-%m-%d"), ed.strftime("%Y-%m-%d")])
	
	result = cursor.fetchall()
	
	mo_dict = {}
	for l in cursor.execute("select id, name_short from calls_mo order by id"):
		mo_dict[l[0]] = l[1]
		
	profile_dict = {}
	for l in cursor.execute("select id, name, code from answers_callprofile order by code"):
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
		l.append(mo_dict[i])
		for j in profile_dict:
			l.append(td[i].get(j, ""))
			
	# TODO: maybe using regroup tag in template
	
	
	
	
	return render(request, 'reports/analysis.html', {'mo': mo_dict, 'profile': profile_dict, 'table': rt, 'pf': period_form})

	

