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

	#~ excdays = ExceptionalDays.objects.filter(pk_gte=d) # праздничные дни
	# TODO: переписать функцию с учетом праздничных дней
	
	for i in xrange(0, offset - 1):
		wd = d.weekday()
		if  wd == 4: # пятница
			d = d + oneday + oneday + oneday # добавить 2 выходных и один рабочий
		elif  wd == 5: # суббота
			d = d + oneday + oneday + oneday # добавить 1 выходной и один рабочий
		elif wd == 6: # воскресенье
			d = d + oneday + oneday # добавить 2 рабочих
		else: # понедельник, вторинк, среда, четверг
			d = d + oneday # добавить 1 рабочий
		
	return d
