from django.contrib import admin
from models import CallProfile, Action, Answer, CallProfileGroup

class AnswerAdmin(admin.ModelAdmin):
	list_display = ('call_id', 'dt', 'call_contents', 'contents', 'profile', 'action_short_name', 'validity')
	list_display_links = ('call_id', 'dt',)
	
	raw_id_fields = ('call', )

class CallProfileGroupAdmin(admin.ModelAdmin):
	list_display = ('code', 'name')
	list_display_links = ('name', )

admin.site.register(Answer, AnswerAdmin)
admin.site.register(CallProfile)
admin.site.register(CallProfileGroup, CallProfileGroupAdmin)
admin.site.register(Action)