from datetime import date
from django.test import TestCase

#from workcalendar.models import ExceptionalDays
import workcalendar

class CalendarTest(TestCase):
	def test_next_workdays_inclusive(self):
		"Проверка правильности работы функции workcalendar.next_workdays_inclusive"
		
		date21 = date(2013, 03, 21) # четверг
		date22 = date(2013, 03, 22) # пятница
		date23 = date(2013, 03, 23) # суббота
		date24 = date(2013, 03, 24) # воскресенье
		date25 = date(2013, 03, 25) # понедельник
		date26 = date(2013, 03, 26) # вторник
		
		f = workcalendar.next_workday_inclusive
		
		self.assertEquals(f(date21, 2), date22)
		self.assertEquals(f(date22, 2), date25)
		self.assertEquals(f(date23, 2), date26)
		self.assertEquals(f(date24, 2), date26)
		
		self.assertEquals(f(date21, 3), date25)
		
		
		#side effects
		self.assertEquals(date21, date(2013, 03, 21))
		
	def test_next_workdays_inclusive_with_holidays(self):
		"Проверка правильности работы функции workcalendar.next_workdays_inclusive с учетом праздников"
		
		april30 = date(2013, 04, 30)
		may1 = date(2013, 05, 1)
		may2 = date(2013, 05, 2)
		may3 = date(2013, 05, 3)
		may4 = date(2013, 05, 4)
		may5 = date(2013, 05, 5)
		may6 = date(2013, 05, 6)
		may7 = date(2013, 05, 7)
		
		# для теста: 1,2,3 - выходные; 4 - рабочий, 5 - выходной
		ed = workcalendar.models.ExceptionalDays
		f = workcalendar.next_workday_inclusive
		
		# добавляем 1, 2, 3, 4 в исключения
		e = ed()
		e.date = may1
		e.save()
		
		e = ed()
		e.date = may2
		e.save()
		
		e = ed()
		e.date = may3
		e.save()
		
		e = ed()
		e.date = may4
		e.save()
		#-------
		
		self.assertEquals(f(april30, 2), may4)
		self.assertEquals(f(may1, 2), may6)
		self.assertEquals(f(may3, 2), may6)
		self.assertEquals(f(may4, 2), may6)
		self.assertEquals(f(may4, 3), may7)
		self.assertEquals(f(may6, 2), may7)
		
		