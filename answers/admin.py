from django.contrib import admin
from models import CallProfile, Action, Answer, CallProfileGroup

class AnswerAdmin(admin.ModelAdmin):
	list_display = ('call_id', 'dt', 'mo_admin', 'call_contents', 'contents', 'profile_admin', 'action_short_name', 'validity')
	list_display_links = ('call_id', 'dt',)
	
	raw_id_fields = ('call', )
	
	def queryset(self, request):
		return super(AnswerAdmin, self).queryset(request).select_related(
				'call', 'call__mo', 'profile', 'action')


class CallProfileGroupAdmin(admin.ModelAdmin):
	list_display = ('code', 'name')
	list_display_links = ('name', )

admin.site.register(Answer, AnswerAdmin)
admin.site.register(CallProfile)
admin.site.register(CallProfileGroup, CallProfileGroupAdmin)
admin.site.register(Action)
