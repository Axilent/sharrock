"""
URLs for Sharrock resource layer.
"""
from django.conf.urls.defaults import *

urlpatterns = patterns('sharrock.views',
    (r'^describe/(?P<app>[\w\.]+)/(?P<version>[\w\.]+)/(?P<service_name>[\w-]+)\.(?P<extension>\w+)$','describe_service',{'service_type':'resource'}),
    (r'^describe/(?P<app>[\w\.]+)/(?P<version>[\w\.]+)/(?P<service_name>[\w-]+)/$','describe_service',{'extension':'html','service_type':'resource'}),
    (r'^(?P<app>[\w\.]+)/(?P<version>[\w\.]+)/(?P<resource_name>[\w-]+)/$','execute_resource',{'extension':'json'}),
    (r'^(?P<app>[\w\.]+)/(?P<version>[\w\.]+)/(?P<resource_name>[\w-]+)\.(?P<extension>\w+)$','execute_resource'),
    (r'^(?P<app>[\w\.]+)/(?P<version>[\w\.]+)/(?P<resource_name>[\w-]+)/list/$','execute_resource',{'extension':'json'}), # model resource url
    (r'^(?P<app>[\w\.]+)/(?P<version>[\w\.]+)/(?P<resource_name>[\w-]+)/list\.(?P<extension>\w+)$','execute_resource'),  # model resource url
    (r'^(?P<app>[\w\.]+)/(?P<version>[\w\.]+)/(?P<resource_name>[\w-]+)/create/$','execute_resource',{'extension':'json'}), # model resource url
    (r'^(?P<app>[\w\.]+)/(?P<version>[\w\.]+)/(?P<resource_name>[\w-]+)/create\.(?P<extension>\w+)$','execute_resource'),  # model resource url
    (r'^(?P<app>[\w\.]+)/(?P<version>[\w\.]+)/(?P<resource_name>[\w-]+)/(?P<model_id>\d+)/$','execute_resource',{'extension':'json'}), # model resource url
    (r'^(?P<app>[\w\.]+)/(?P<version>[\w\.]+)/(?P<resource_name>[\w-]+)/(?P<model_id>\d+)\.(?P<extension>\w+)$','execute_resource'), # model resource url
)