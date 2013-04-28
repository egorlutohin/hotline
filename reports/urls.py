from django.conf.urls import patterns, url
from reports import views

urlpatterns = patterns('',
    url(r'^std/$', views.std, name='std'),
    url(r'^analysis/$', views.analysis, name='analysis'),
    url(r'^reportthree/$', views.reportthree, name='reportthree'),
    url(r'^answermans/$', views.answermans, name='answermans'),
)
