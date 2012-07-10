from django.conf.urls.defaults import patterns, include, url

urlpatterns = patterns('',
    url(r'^teams/data/$', 'ui.views.getData'),
    url(r'^$', 'ui.views.index'),
    url(r'^(?P<team>[a-zA-Z-]+)/(?P<metric>[a-zA-Z-]+)/$', 'ui.views.teamdata')
)
