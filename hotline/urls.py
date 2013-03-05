from django.conf.urls import patterns, include, url

from django.contrib import admin
admin.autodiscover()

urlpatterns = patterns('',
    # Examples:
    # url(r'^hotline/', include('hotline.foo.urls')),

    #url(r'^admin/doc/', include('django.contrib.admindocs.urls')),
    url(r'^operator/', include(admin.site.urls)),
    url(r'', include('calls.urls')),
)
