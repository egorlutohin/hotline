from models import ExceptionalDays
from datetime import datetime, date, timedelta

def _clean_dt(dt):
	if type(dt) == datetime:
		d =  dt.date()
	else: 
		d = dt
	
	return d

def next_workday_inclusive(dt, offset):
	"Вернет следующий рабочий день через `offset` рабочих дней от переданной даты, включая переданную"
	
	d = _clean_dt(dt)

	if offset < 2:
		return d

	oneday = timedelta(days=1)
	
	excdays = [e.date for e in ExceptionalDays.objects.filter(pk__gte=d)] # исключения: праздничные дни, рабочие выходные

	o = offset
	while True:
		wd = d.weekday()
		
		if wd in (5, 6): # суббота, воскресенье
			if d in excdays:
				o-=1
		else: #будни
			if d not in excdays:
				o-=1
		
		if o == 0:
			break
		
		d+= oneday
		
	return d
