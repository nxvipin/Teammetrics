from django.conf.urls.defaults import patterns, include, url

urlpatterns = patterns('',
    url(r'^v(?P<api_version>\d+)/a/(?P<team>[a-zA-Z-]+)/$', 'api.views.annualAll'),
    url(r'^v(?P<api_version>\d+)/a/(?P<team>[a-zA-Z-]+)/(?P<metric>[a-z]+)/$', 'api.views.annual'),
    url(r'^v(?P<api_version>\d+)/a/(?P<team>[a-zA-Z-]+)/(?P<metric>[a-z]+)/(?P<n>\d+)/$', 'api.views.annualTopN'),
    url(r'^v(?P<api_version>\d+)/(?P<team>[a-zA-Z-]+)/$', 'api.views.monthAll'),
    url(r'^v(?P<api_version>\d+)/(?P<team>[a-zA-Z-]+)/(?P<metric>[a-z]+)/$', 'api.views.month'),
    url(r'^v(?P<api_version>\d+)/(?P<team>[a-zA-Z-]+)/(?P<metric>[a-z]+)/(?P<n>\d+)/$', 'api.views.monthTopN'),
)
