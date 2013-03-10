from django.conf.urls import patterns, url
from calls import views

urlpatterns = patterns('',
    # Examples:
    # url(r'^hotline/', include('hotline.foo.urls')),
    url(r'^$', views.index, name='index'),
    url(r'^feed/$', views.feed, name='feed'),
    url(r'^answer/$', views.answer_index, name='answer' )
)
