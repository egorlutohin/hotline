from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone

class Citizen(models.Model):
	SNP = models.CharField("ФИО",max_length=200)
	birthyear = models.PositiveIntegerField("Год рождения")
	address = models.TextField("Адрес", blank=True, null=True)
	phone = models.CharField("Телефон(ы)", max_length=200, blank=True, null=True)
	
	last_appeal = models.DateTimeField("Дата последнего обращения", blank=True, null=True)
	
	
	def __unicode__(self):
		return u"%s, %d г.р." % (self.SNP, self.birthyear)
		
	def number(self):
		return self.id
	number.admin_order_field = 'id'
	number.short_description = '#'	
		
		
	class Meta:
		verbose_name = "гражданина"
		verbose_name_plural = "граждане"

class AnswerMan(User):
	"Ответственный за подготовку ответа"
	department = models.CharField("Отдел", max_length=200)
	
	def print_answerman_name(self):
		return unicode(self)
	print_answerman_name.admin_order_field = 'id'
	print_answerman_name.short_description = 'Имя оператора'	
	
	
	def __unicode__(self):
		return u"%s %s" % (self.last_name, self.first_name)

	
	class Meta:
		verbose_name = "ответственного за подготовку ответа"
		verbose_name_plural = "Ответственные за подготовку ответа"
	
class MO(models.Model):
	name_short = models.CharField("Короткое название", max_length=200)
	name_full = models.CharField("Полное название", max_length=200, null=True, blank=True)
	
	def __unicode__(self):
		return self.name_short
		
	class Meta:
		verbose_name = "медицинскую организацию"
		verbose_name_plural = "Медицинские организации"
		
class Call(models.Model):
	"Обращение по телефону"
	
	dt = models.DateTimeField("Дата и время получения")
	op = models.ForeignKey(User, verbose_name="Оператор")
	citizen = models.ForeignKey(Citizen, verbose_name="Гражданин")
	medorg = models.ForeignKey(MO, verbose_name="Медицинская организация", null=True, blank=True)
	contents = models.TextField("Содержание сообщения")
	answer_man = models.ForeignKey(AnswerMan, verbose_name="Ответственный за подготовку ответа", related_name = 'answer_man')
	
	def __unicode__(self):
		return u"Обращение #%d" % (self.number())
		
	def number(self):
		"Номер обращения"
		return self.id
		
	number.admin_order_field = 'id'
	number.short_description = '#'	

	def print_operator_name(self):
		return u"%s %s" % (self.op.last_name, self.op.first_name)
		
	print_operator_name.admin_order_field = 'op'
	print_operator_name.short_description = 'Оператор'	
		
		
	class Meta:
		ordering = ['-id']
		verbose_name = "обращение по телефону"
		verbose_name_plural = "обращения по телефону"