from django.conf.urls import patterns, url

from api import views

urlpatterns = patterns('',
    url(r'start', views.start, name='start'),
    url(r'status', views.status, name='status'),
    url(r'stop', views.stop, name='stop'),
    url(r'diff', views.diff, name='diff'),
    url(r'^$', views.index, name='index'),
)
