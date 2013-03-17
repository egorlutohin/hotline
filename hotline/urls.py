from django.conf.urls import patterns, include, url
from django.conf import settings

from django.contrib import admin
admin.autodiscover()

urlpatterns = patterns('',
    # Examples:
    # url(r'^hotline/', include('hotline.foo.urls')),

    #url(r'^admin/doc/', include('django.contrib.admindocs.urls')),
    url(r'^%s$' % settings.LOGIN_URL[1:], 'django.contrib.auth.views.login', name='login'),
    url(r'^%s$' % settings.LOGOUT_URL[1:], 'django.contrib.auth.views.logout', {'template_name': 'registration/logout.html'}, name='logout',),
    url(r'^operator/', include(admin.site.urls)),
    url(r'', include('calls.urls', namespace='calls')),
)
