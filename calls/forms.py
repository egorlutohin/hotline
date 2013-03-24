from django import forms
#~ from django.forms import ModelForm, Form
from calls.models import Call
from answers.models import Answer, Reason

class CallModelForm(forms.ModelForm):
	class Meta:
		model = Call
		fields = ('mo', 'contents')

class AnswerModelForm(forms.ModelForm):
	class Meta:
		model = Answer
		exclude = ('call', 'dt')
		
class ReasonModelForm(forms.ModelForm):
	class Meta:
		model = Reason
		exclude = ('call', )
		

# чуть-чуть криво, но как бы пойдет :(

#~ class AnswerReasonForm(Form):
	#~ contents = forms.CharField()
	