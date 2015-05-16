"""
URLs to mount Sharrock functions.
"""
try:
    from django.conf.urls import include, url, patterns
except ImportError:
    # old import pattern
    from django.conf.urls.defaults import *

urlpatterns = patterns('sharrock.views',
    url(r'^dir\.(?P<extension>\w+)$','directory'),
    url(r'^dir/$','directory',{'extension':'html'}),
    url(r'^dir/(?P<app>[\w\.-]+)/(?P<version>[\w\.-]+)/$','directory',{'extension':'html'}),
    url(r'^dir/(?P<app>[\w\.-]+)/(?P<version>[\w\.-]+)\.(?P<extension>\w+)$','directory'),
    url(r'^describe/(?P<app>[\w\.-]+)/(?P<version>[\w\.-]+)/(?P<service_name>[\w-]+)\.(?P<extension>\w+)$','describe_service'),
    url(r'^describe/(?P<app>[\w\.-]+)/(?P<version>[\w\.-]+)/(?P<service_name>[\w-]+)/$','describe_service',{'extension':'html'}),
    url(r'^(?P<app>[\w\.-]+)/(?P<version>[\w\.-]+)/(?P<service_name>[\w-]+)/$','execute_service',{'extension':'json'}),
    url(r'^(?P<app>[\w\.-]+)/(?P<version>[\w\.-]+)/(?P<service_name>[\w-]+)\.(?P<extension>\w+)$','execute_service'),
)