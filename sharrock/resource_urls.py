"""
URLs for Sharrock resource layer.
"""
try:
    from django.conf.urls import include, url, patterns
except ImportError:
    # old import pattern
    from django.conf.urls.defaults import *

urlpatterns = patterns('sharrock.views',
    url(r'^describe/(?P<app>[\w\.-]+)/(?P<version>[\w\.-]+)/(?P<service_name>[\w-]+)\.(?P<extension>\w+)$','describe_service',{'service_type':'resource'}),
    url(r'^describe/(?P<app>[\w\.-]+)/(?P<version>[\w\.-]+)/(?P<service_name>[\w-]+)/$','describe_service',{'extension':'html','service_type':'resource'}),
    url(r'^(?P<app>[\w\.-]+)/(?P<version>[\w\.-]+)/(?P<resource_name>[\w-]+)/$','execute_resource',{'extension':'json'}),
    url(r'^(?P<app>[\w\.-]+)/(?P<version>[\w\.-]+)/(?P<resource_name>[\w-]+)\.(?P<extension>\w+)$','execute_resource'),
    url(r'^(?P<app>[\w\.-]+)/(?P<version>[\w\.-]+)/(?P<resource_name>[\w-]+)/list/$','execute_resource',{'extension':'json'}), # model resource url
    url(r'^(?P<app>[\w\.-]+)/(?P<version>[\w\.-]+)/(?P<resource_name>[\w-]+)/list\.(?P<extension>\w+)$','execute_resource'),  # model resource url
    url(r'^(?P<app>[\w\.-]+)/(?P<version>[\w\.-]+)/(?P<resource_name>[\w-]+)/create/$','execute_resource',{'extension':'json'}), # model resource url
    url(r'^(?P<app>[\w\.-]+)/(?P<version>[\w\.-]+)/(?P<resource_name>[\w-]+)/create\.(?P<extension>\w+)$','execute_resource'),  # model resource url
    url(r'^(?P<app>[\w\.-]+)/(?P<version>[\w\.-]+)/(?P<resource_name>[\w-]+)/(?P<model_id>\d+)/$','execute_resource',{'extension':'json'}), # model resource url
    url(r'^(?P<app>[\w\.-]+)/(?P<version>[\w\.-]+)/(?P<resource_name>[\w-]+)/(?P<model_id>\d+)\.(?P<extension>\w+)$','execute_resource'), # model resource url
)