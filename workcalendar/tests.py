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