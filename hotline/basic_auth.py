"""
Code stole from http://djangosnippets.org/snippets/243/
"""
import base64

from django.http import HttpResponse
from django.contrib.auth import authenticate, login
def _auth_required_response():
	r = HttpResponse("Auth Required", status = 401)
	r['WWW-Authenticate'] = 'Basic realm=""'
	return r
	
	
def basic_http_auth(f):
	def wrap(request, *args, **kwargs):
		if request.META.get('HTTP_AUTHORIZATION', False):
			authtype, auth = request.META['HTTP_AUTHORIZATION'].split(' ')
			auth = base64.b64decode(auth)
			username, password = auth.split(':')
			user = authenticate(username=username, password=password)
			if user is not None and user.is_active:
				#~ login(request, user)
				request.user = user
				return f(request, *args, **kwargs)
			else:
				return _auth_required_response()
		return _auth_required_response()

	return wrap