from django.db import models

class Citizen(models.Model):
	SNP = models.CharField('ФИО',max_length=200)
	birthday = models.DateField('Дата рождения')
	address = models.CharField('Адрес', max_length=200, blank=True, null=True)
	phone = models.CharField('Телефон(ы)', max_length=200, blank=True, null=True)
	
	#def __unicode__(self):
		
	
	
	

class Call(models.Model):
	citizen = models.ForeignKey(Citizen)
	
	#~ def __unicode__(self):
		#~ pass
