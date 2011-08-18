"""
URLs to mount Sharrock functions.
"""
from django.conf.urls.defaults import *

urlpatterns = patterns('sharrock.views',
    (r'^dir\.(?P<extension>\w+)$','directory'),
    (r'^dir/$','directory',{'extension':'html'}),
    (r'^dir/(?P<app>[\w\.]+)/(?P<version>[\w\.]+)/$','directory',{'extension':'html'}),
    (r'^dir/(?P<app>[\w\.]+)/(?P<version>[\w\.]+)\.(?P<extension>\w+)$','directory'),
    (r'^describe/(?P<app>[\w\.]+)/(?P<version>[\w\.]+)/(?P<service_name>[\w-]+)\.(?P<extension>\w+)$','describe_service'),
    (r'^describe/(?P<app>[\w\.]+)/(?P<version>[\w\.]+)/(?P<service_name>[\w-]+)/$','describe_service',{'extension':'html'}),
    (r'^(?P<app>[\w\.]+)/(?P<version>[\w\.]+)/(?P<service_name>[\w-]+)/$','execute_service',{'extension':'json'}),
    (r'^(?P<app>[\w\.]+)/(?P<version>[\w\.]+)/(?P<service_name>[\w-]+)\.(?P<extension>\w+)$','execute_service'),
)