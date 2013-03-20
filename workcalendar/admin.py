from models import ExceptionalDays
from django.contrib import admin

class ExceptionalDaysAdmin(admin.ModelAdmin):
	list_display = ('date', 'admin_week_day')
	date_hierarchy = 'date'
	list_filter = ('date',)
	
admin.site.register(ExceptionalDays, ExceptionalDaysAdmin)

	