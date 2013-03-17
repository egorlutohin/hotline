from django.forms import ModelForm
from calls.models import Call
from answers.models import Answer

class CallModelForm(ModelForm):
	class Meta:
		model = Call
		fields = ('mo', 'contents')

class AnswerModelForm(ModelForm):
	class Meta:
		model = Answer
		#~ fields = ('mo', 'contents')
		exclude = ('call',)