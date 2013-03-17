from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone

### Question ###

class Citizen(models.Model):
	SNP = models.CharField("ФИО",max_length=200)
	birthyear = models.PositiveIntegerField("Год рождения")
	address = models.TextField("Адрес", blank=True, null=True)
	phone = models.CharField("Телефон(ы)", max_length=200, blank=True, null=True)
	
	last_appeal = models.DateTimeField("Дата последнего обращения", blank=True, null=True)
	
	def add_call_link(self):
		return '<a href="/operator/calls/call/add/?citizen=%d">+ обращение</a>' % self.id
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
	name_full = models.CharField("Полное название", max_length=200, null=True, blank=True)
	type = models.PositiveIntegerField("Тип организации", choices=TYPE.choices())
	info = models.TextField("Дополнительная информация", help_text="Например: адрес, телефон, контактное лицо", null=True, blank=True)
	
	def __unicode__(self):
		return self.name_short
		
	class Meta:
		verbose_name = "медицинскую организацию"
		verbose_name_plural = "Медицинские организации"
		
class Call(models.Model):
	"Обращение по телефону"
	dt = models.DateTimeField("Дата и время получения")
	operator = models.ForeignKey(User, verbose_name="Оператор")
	citizen = models.ForeignKey(Citizen, verbose_name="Гражданин")
	mo = models.ForeignKey(MO, verbose_name="Медицинская организация", null=True, blank=True)
	contents = models.TextField("Содержание сообщения")
	answer_man = models.ForeignKey(AnswerMan, verbose_name="Ответственный за подготовку ответа")
	
	call_received = models.DateTimeField("Дата и время получения обращения", null=True, blank=True)
	answer_created = models.DateTimeField("Дата и время получения ответа", null=True, blank=True)
	
	
	
	def __unicode__(self):
		return u"Обращение #%d" % (self.number())
		
	def number(self):
		"Номер обращения"
		return self.id
		
	number.admin_order_field = 'id'
	number.short_description = '#'	

	def print_operator_name(self):
		return u"%s %s" % (self.operator.last_name, self.operator.first_name)

	print_operator_name.admin_order_field = 'op'
	print_operator_name.short_description = 'Оператор'	
	
	def add_or_change_answer_link(self):
		try:
			self.answer
			#изменить ответ
			return '<a href="/operator/answers/answer/%d/">изменить ответ</a>' % self.id
		except:
			# добавить ответ
			return '<a href="/operator/answers/answer/add/?call=%d">добавить ответ</a>' % self.id
	add_or_change_answer_link.short_description = "Добавить/изменить ответ"
	add_or_change_answer_link.allow_tags = True
	
	def get_answer(self):
		try:
			return self.answer
		except:
			return None

	
	def got_answer(self):
		if self.answer_created:
			return True
		else:
			return False
	got_answer.short_description = "Ответ получен"
	got_answer.boolean = True

		
	class Meta:
		ordering = ['-id']
		verbose_name = "обращение по телефону"
		verbose_name_plural = "обращения по телефону"
