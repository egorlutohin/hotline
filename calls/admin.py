from models import Citizen, Call, MO, AnswerMan
from django.contrib import admin

admin.site.disable_action('delete_selected')

class CitizenAdmin(admin.ModelAdmin):
	list_display = ('number','SNP', 'birthyear', 'phone', 'address', 'add_call_link')
	list_display_links = ('SNP',)
	search_fields = ['SNP', 'birthyear', 'phone', 'address']
	exclude = ('last_appeal',)

class MOAdmin(admin.ModelAdmin):
	list_display = ('name_short', 'name_full')
	search_fields = ['name_short', 'name_full']
	
class CallAdmin(admin.ModelAdmin):
	exclude = ('op',)
	list_display = ('number', 'citizen', 'medorg', 'contents','dt', 'answer_man', 'print_operator_name')
	list_display_links = ('citizen',)
	
	def save_model(self, request, obj, form, change):
		if not change:
			obj.op = request.user
		obj.save()

class AnswerManAdmin(admin.ModelAdmin):
	list_display = ('print_answerman_name', 'department')
	
	fieldsets = (
		(None, {
			'fields': ('username', 'password', 'department', 'last_name', 'first_name',)
		}),
	)

admin.site.register(Citizen, CitizenAdmin)
admin.site.register(MO,MOAdmin)
admin.site.register(Call, CallAdmin)
admin.site.register(AnswerMan, AnswerManAdmin)