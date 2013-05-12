from django.db import models

# Dummy model, only for permissions purpose
class Report(models.Model):
	class Meta:
		verbose_name = "отчет"
		verbose_name_plural = "отчеты"
		permissions = (("can_view", "Can view"),)
