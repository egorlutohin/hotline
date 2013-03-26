from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone

import workcalendar

### Question ###

class Citizen(models.Model):
	SNP = models.CharField("ФИО",max_length=200)
	birthyear = models.PositiveIntegerField("Год рождения")
	address = models.TextField("Адрес", blank=True, null=True)
	phone = models.CharField("Телефон(ы)", max_length=200, blank=True, null=True)
	
	first_appeal = models.DateTimeField("Дата первого обращения", blank=True, null=True)
	last_appeal = models.DateTimeField("Дата последнего обращения", blank=True, null=True)
	
	def add_call_link(self):
		return '<a class="addlink" href="/operator/calls/call/add/?citizen=%d" target="call">Обращение</a>' % self.id
	add_call_link.short_description = "Добавить обращение"
	add_call_link.allow_tags = True
	
	
	def __unicode__(self):
		return u"%s, %d г.р." % (self.SNP, self.birthyear)
		
	def number(self):
		return self.id
	number.admin_order_field = 'id'
	number.short_description = '#'	
	
	class Meta:
		verbose_name = "гражданина"
		verbose_name_plural = "граждане"
		unique_together = ('SNP', 'birthyear', 'phone')

class Department(models.Model):
	"Отдел"
	name = models.CharField("Отдел", max_length=200)
	comment = models.TextField("Комментарий", help_text = "Любая дополнительная информация", blank=True, null=True)
	
	def __unicode__(self):
		return self.name

	class Meta:
		verbose_name = "отдела"
		verbose_name_plural = "отделы"
	
class AnswerMan(models.Model):
	"Ответственный за подготовку ответа (отвечающий человек)"
	department = models.ForeignKey(Department, verbose_name = "Отдел")
	user = models.ForeignKey(User, verbose_name = "Пользователь в системе")
	comment = models.CharField("Комментарий", max_length=200, blank=True, null=True, help_text="Например фамилия")
	
	
	def print_answerman_name(self):
		return u"%s %s" % (self.user.last_name, self.user.first_name)
	print_answerman_name.admin_order_field = 'id'
	print_answerman_name.short_description = 'Имя оператора'	
	
	
	def __unicode__(self):
		return u"%s / %s" % (self.department.name, self.user.last_name,)

	
	class Meta:
		verbose_name = "ответственного за подготовку ответа"
		verbose_name_plural = "Ответственные за подготовку ответа"
		unique_together = ('department', 'user')
	
class MO(models.Model):
	"Медицинская организация"
	
	class TYPE:
		"Тип медицинской организации"
		CITY = 1 # Город
		PROVINCE = 2 # Область
		
		# Description
		D = { 
			CITY: "Городская организация",
			PROVINCE: "Областная организация"
		
		}
		
		@classmethod
		def choices(cls):
			c = []
			for k, v in cls.D.items():
				c.append((k, v))
			return c
	
	name_short = models.CharField("Короткое название", max_length=200)
	name_full = models.TextField("Полное название", null=True, blank=True)
	type = models.PositiveIntegerField("Тип организации", choices=TYPE.choices())
	info = models.TextField("Дополнительная информация", help_text="Например: адрес, телефон, контактное лицо", null=True, blank=True)
	
	def id_admin(self):
		return self.id
	id_admin.admin_order_field = 'id'
	id_admin.short_description = '#'	
	
	def __unicode__(self):
		return self.name_short
		
	class Meta:
		verbose_name = "медицинскую организацию"
		verbose_name_plural = "Медицинские организации"
		ordering = ['id',]
		
class Call(models.Model):
	"Обращение по телефону"
	dt = models.DateTimeField("Дата и время получения")
	operator = models.ForeignKey(User, verbose_name="Оператор")
	citizen = models.ForeignKey(Citizen, verbose_name="Гражданин")
	mo = models.ForeignKey(MO, verbose_name="Медицинская организация", null=True, blank=True)
	contents = models.TextField("Содержание сообщения")
	answer_man = models.ForeignKey(AnswerMan, verbose_name="Ответственный за подготовку ответа")
	
	deadline = models.DateTimeField("Крайний срок ответа", blank=True)
	call_received = models.DateTimeField("Дата и время получения обращения", null=True, blank=True)
	answer_created = models.DateTimeField("Дата и время получения ответа", null=True, blank=True)
	
	def is_outdated(self):
		now = timezone.now()
		deadline = self.deadline
		answer_created = self.answer_created

		if ((answer_created is None) and (now > deadline)) or ((answer_created is not None) and (answer_created > deadline)):
			return True
		else:
			return False
	
	def __unicode__(self):
		return u"Обращение #%d" % (self.number())
		
	def number(self):
		"Номер обращения"
		return self.id
		
	number.admin_order_field = 'id'
	number.short_description = '#'	

	def answer_man_admin(self):
		return self.answer_man.user.last_name
	answer_man_admin.short_description="Ответственный"

	def print_operator_name(self):
		return u"%s %s" % (self.operator.last_name, self.operator.first_name)

	print_operator_name.admin_order_field = 'op'
	print_operator_name.short_description = 'Оператор'	
	
	def add_or_change_answer_link(self):
		try:
			self.answer
			#изменить ответ
			return '<a class="changelink" href="/operator/answers/answer/%d/" target="answer">Изменить</a>' % self.id
		except:
			# добавить ответ
			return '<a class="addlink" href="/operator/answers/answer/add/?call=%d" target="answer">Добавить</a>' % self.id
	add_or_change_answer_link.short_description = "Ответ"
	add_or_change_answer_link.allow_tags = True

	
	def get_answer(self):
		try:
			return self.answer
		except:
			return None
			
	def get_reason(self):
		try:
			return self.reason
		except:
			return None

	
	def got_answer(self):
		if self.answer_created:
			return True
		else:
			return False
	got_answer.short_description = "Ответ"
	got_answer.boolean = True
	got_answer.admin_order_field = 'answer_created'
	
	def got_read_confirmation(self):
		if self.call_received:
			return True
		else:
			return False
	got_read_confirmation.short_description = "Прочитано"
	got_read_confirmation.boolean = True
	got_read_confirmation.admin_order_field = 'call_received'
	
	def save(self, *args, **kwargs):
		if self.deadline == None:
			if workcalendar.is_workday(self.dt):
				d = workcalendar.next_workday(self.dt)
			else:
				d = workcalendar.next_workday(workcalendar.next_workday(self.dt))
				
			deadline = timezone.datetime(year = d.year, month = d.month, day = d.day, hour = 23, minute = 59, second = 59)
			self.deadline = deadline
		
		if self.answer_created and not(self.call_received):
			self.call_received = self.answer_created
			
		if self.citizen.first_appeal == None:
			self.citizen.first_appeal = self.dt
			
		self.citizen.last_appeal = self.dt
		self.citizen.save()
		
		super(Call, self).save(*args, **kwargs)


		
	class Meta:
		ordering = ['-id']
		verbose_name = "обращение по телефону"
		verbose_name_plural = "обращения по телефону"
		
	
