from django.db import models
from calls.models import Call

### Answer ###

class CallProfileGroup(models.Model):
	"Вид профиля обращения"
	code = models.PositiveIntegerField("Код", unique=True)
	name = models.CharField("Наименование", max_length=255)
	
	def __unicode__(self):
		return self.name
		
	class Meta:
		verbose_name = "вид профиля обращения"
		verbose_name_plural = "виды профилей обращения"
		ordering = ('code', )
		


class CallProfile(models.Model):
	"Профиль обращения"
	code = models.PositiveIntegerField("Код обращения", unique=True)
	name = models.CharField("Наименование", max_length=255)
	group = models.ForeignKey(CallProfileGroup, verbose_name="Вид профиля обращения")
	
	def __unicode__(self):
		return u"%d - %s" % (self.code, self.name)
		
	class Meta:
		verbose_name = "профиль обращения"
		verbose_name_plural = "профили обращения"
	
class Action(models.Model):
	"Меры, принятые по результатам рассмотрения"
	code = models.PositiveIntegerField("Код", unique=True)
	name = models.CharField("Наименование", max_length=255)
	
	def __unicode__(self):
		return u"%d - %s" % (self.code, self.name)
	
	class Meta:
		verbose_name = "меру, принятую по результатам рассмотрения"
		verbose_name_plural = "меры, принятые по результатам рассмотрения"



class Answer(models.Model):
	"Ответ на обращение по телефону"
	call = models.OneToOneField(Call, primary_key=True, verbose_name="Обращение")
	dt = models.DateTimeField("Дата и время направления ответа")
	contents = models.TextField("Содержание ответа")
	profile = models.ForeignKey(CallProfile, verbose_name="Профиль обращения")
	action = models.ForeignKey(Action, verbose_name="Меры принятые по результатам рассмотрения")
	validity = models.BooleanField("Претензия обоснована")
	
	def call_contents(self):
		return self.call.contents
	call_contents.short_description = "Содержание обращения"
	
	def call_id(self):
		return self.call.id
	call_id.short_description = "Номер обращения"
	
	def action_short_name(self):
		MAX_LEN = 25
		name = unicode(self.action)
		if len(name) > MAX_LEN:
			return name[:MAX_LEN] + u"..."
		else:
			return name
	action_short_name.short_description = "Меры"


	
	def __unicode__(self):
		return u"Ответ на обращение #%s" % (self.call.number(),)

	
	class Meta:
		verbose_name = "ответ на обращение по телефону"
		verbose_name_plural = "ответы на обращения по телефону"
		
	
	def delete(self, *args, **kwargs):
		try:
			self.call.call_received = None
			self.call.answer_created = None
			self.call.save()
		except:
			pass
		super(Answer, self).delete(*args, **kwargs)

	
	
	def save(self, *args, **kwargs):
		super(Answer, self).save(*args, **kwargs)
		
		self.call.answer_created = self.dt
		self.call.save()
		
class Reason(models.Model):
	"Причина ответа не в срок"
	call = models.OneToOneField(Call, primary_key=True, verbose_name="Обращение")
	text = models.TextField("Причина ответа не в срок")
	
	def __unicode__(self):
		return u"Причина ответа не в срок на обращение #%d" % self.call.id

