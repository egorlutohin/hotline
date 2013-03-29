from models import Citizen, Call, MO, AnswerMan, Department
from django.contrib import admin
from django.utils import timezone
import workcalendar

admin.site.disable_action('delete_selected')


class CitizenAdmin(admin.ModelAdmin):
	list_display = ('number','SNP', 'birthyear', 'phone', 'address', 'last_appeal', 'add_call_link')
	list_display_links = ('SNP',)
	search_fields = ['SNP', 'birthyear', 'phone', 'address']
	exclude = ('last_appeal', 'first_appeal')

class MOAdmin(admin.ModelAdmin):
	list_display = ('id_admin', 'name_short', 'name_full', 'info', 'type')
	list_display_links = ('name_short', 'name_full')
	search_fields = ('name_short', 'name_full', 'info')
	
from django.contrib.admin import SimpleListFilter

class CallsFilter(SimpleListFilter):
	title = ''
	parameter_name = 'notifications'
	
	def lookups(self, request, model_admin):
		return (
			('1', 'Обращение не прочитано'),		
			('2', 'Обращение не прочитано более 3 часов'),
			('3', 'Обращение прочитано'),
			('4', 'Ответ не получен'),
			('5', 'Ответ не получен, время вышло'),
			('6', 'Ответ получен'),
		)
	def queryset(self, request, queryset):
		if self.value() == '1':
			return queryset.filter(call_received__isnull=True)
		elif self.value() == '2':
			offset_3hours = timezone.now() - timezone.timedelta(hours=3)
			return queryset.filter(call_received__isnull=True, dt__lt=offset_3hours)
		elif self.value() == '3':
			return queryset.filter(call_received__isnull=False)
		elif self.value() == '4':
			return queryset.filter(answer_created__isnull=True)
		elif self.value() == '5':
			now = timezone.now()
			return queryset.filter(answer_created__isnull=True, deadline__lt=now)
		elif self.value() == '6':
			return queryset.filter(answer_created__isnull=False)
	
class CallAdmin(admin.ModelAdmin):
	fieldsets = (
		(None, {
			'fields': ('dt', 'citizen', 'mo', 'contents', 'answer_man',)
		}),
		('Контрольные даты', {
			# 'classes': ('collapse',),		
			'fields':  ('deadline', 'call_received',),
		}),
	)
	
	list_display = ('number', 'citizen', 'mo_admin', 'dt', 'deadline', 'answer_man_admin', 'print_operator_name', 
	                    'got_read_confirmation',  'got_answer' , 'add_or_change_answer_link')
	list_display_links = ('citizen',)
	raw_id_fields = ('citizen', 'mo')
	
	date_hierarchy = 'dt'
	list_filter = (CallsFilter, )
	
	def save_model(self, request, obj, form, change):
		if not change:
			obj.operator = request.user
		obj.save()

class AnswerManAdmin(admin.ModelAdmin):
	list_display = ('print_answerman_name', 'department')
		
class DepartmentAdmin(admin.ModelAdmin):
	list_display = ('name', 'comment')


admin.site.register(Citizen, CitizenAdmin)
admin.site.register(MO,MOAdmin)
admin.site.register(Call, CallAdmin)
admin.site.register(Department, DepartmentAdmin)
admin.site.register(AnswerMan, AnswerManAdmin)
