from django.conf.urls.defaults import patterns, include, url

urlpatterns = patterns('',
    url(r'^getdata$', 'ui.views.getData'),
    url(r'^$', 'ui.views.index'),
    url(r'^(?P<team>[a-zA-Z-]+)/(?P<metric>[a-zA-Z-]+)/$', 'ui.views.teamdata'),
    url(r'^js/(?P<team>[a-zA-Z-]+)/(?P<metric>[a-zA-Z-]+)/$', 'ui.views.teamdatajs')
)
