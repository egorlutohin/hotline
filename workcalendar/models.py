from django.db import models

class ExceptionalDays(models.Model):
	"Исключительные дни"
	
	date = models.DateField("Дата", primary_key=True, help_text="Праздничный будний день, либо рабочий день в субботу или воскресенье")
	
	def __unicode__(self):
		return unicode(self.date)
		
	def workday(self):
		if self.date.weekday() in (5,6):
			return True
		else:
			return False
		
	def week_day(self):
		WEEKDAYS = [
			"Понедельник",
			"Вторник",
			"Среда",
			"Четверг",
			"Пятница",
			"Суббота",
			"Воскресенье"
		]
		return WEEKDAYS[self.date.weekday()]
		
	def admin_week_day(self):
		wd = self.date.weekday()
		if wd in (5, 6): # если суббота или воскресенье
			return '<span style="color: red;">%s</span>' % self.week_day()
		return self.week_day()
	admin_week_day.short_description = "День недели"
	admin_week_day.allow_tags = True
	
	class Meta:
		ordering = ['-date']
		verbose_name = "праздничный или рабочий день"
		verbose_name_plural = "праздничные или рабочие дни"


