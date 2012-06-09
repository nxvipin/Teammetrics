from django.conf.urls.defaults import patterns, include, url

urlpatterns = patterns('',
    url(r'^v(?P<api_version>\d+)/(?P<team>[a-zA-Z-]+)/(?P<metric>[a-z]+)/$', 'api.views.month')
)
