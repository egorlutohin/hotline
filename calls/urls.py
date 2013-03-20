from django.conf.urls import patterns, url
from calls import views

urlpatterns = patterns('',
    # Examples:
    # url(r'^hotline/', include('hotline.foo.urls')),
    url(r'^$', views.index, name='index'),
    url(r'^feed/$', views.feed, name='feed'),
    url(r'^feed/confirm/(?P<call_id>\d)/(?P<digest>[0-9a-f]{32}).png$', views.feed_read_confirmation, name='feed_read_confirmation'),
    url(r'^answer/$', views.answer_index, name='answers'),
    url(r'^answer/(?P<call_id>\d)/$', views.answer_detail, name='answer_detail'),
    url(r'^answer/ajax/mo/$', views.ajax_mo, name="ajax_mo"),
    url(r'^answer/ajax/contents/$', views.ajax_contents, name="ajax_contents"),
)
