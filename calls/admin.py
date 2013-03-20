from models import Citizen, Call, MO, AnswerMan, Department
from django.contrib import admin

admin.site.disable_action('delete_selected')

class CitizenAdmin(admin.ModelAdmin):
	list_display = ('number','SNP', 'birthyear', 'phone', 'address', 'add_call_link')
	list_display_links = ('SNP',)
	search_fields = ['SNP', 'birthyear', 'phone', 'address']
	exclude = ('last_appeal',)

class MOAdmin(admin.ModelAdmin):
	list_display = ('name_short', 'name_full', 'info', 'type')
	search_fields = ('name_short', 'name_full', 'info')
	
class CallAdmin(admin.ModelAdmin):
	fieldsets = (
		(None, {
			'fields': ('dt', 'citizen', 'mo', 'contents', 'answer_man',)
		}),
		('Контрольные даты', {
			'classes': ('collapse',),		
			'fields':  ('deadline', 'call_received', 'answer_created'),
		}),
	)
	
	list_display = ('number', 'citizen', 'mo', 'dt', 'answer_man', 'print_operator_name', 
	                    'got_read_confirmation',  'got_answer' , 'add_or_change_answer_link')
	list_display_links = ('citizen',)
	raw_id_fields = ('citizen', 'mo')
	
	date_hierarchy = 'dt'
	list_filter = ('dt',)
	
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