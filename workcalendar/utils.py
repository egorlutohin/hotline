from models import ExceptionalDays
from datetime import datetime, date, timedelta

def _clean_dt(dt):
	if type(dt) == datetime:
		d =  dt.date()
	else: 
		d = dt
	
	return d

def is_work_day(dt):
	d = _clean_dt(dt)	

	try:
		day = ExceptionalDays.objects.get(pk=d)
	except ExceptionalDays.DoesNotExist:
		day = None
	
	if day:
		return day.is_workday()
	else:
		if d.weekday() in (5,6):
			return False
		else:
			return True

def next_work_day(dt):
	d = _clean_dt(dt)
	one_day = timedelta(days=1)
	
	next_day = d + one_day
	while not is_work_day(next_day):
		next_day = next_day + one_day
	
	return next_day
	
