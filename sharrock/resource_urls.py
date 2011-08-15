"""
URLs for Sharrock resource layer.
"""
from django.conf.urls.defaults import *

urlpatterns = patterns('sharrock.views',
    (r'^dir\.(?P<extension>\w+)$','resource_directory'),
    (r'^dir/$','resource_directory',{'extension':'html'}),
    (r'^dir/(?P<app>\w+)/(?P<version>[\w\.]+)/$','resource_directory',{'extension':'html'}),
    (r'^dir/(?P<app>\w+)/(?P<version>[\w\.]+)\.(?P<extension>\w+)$','resource_directory'),
    (r'^(?P<app>[\w\.]+)/(?P<version>[\w\.]+)/(?P<resource_name>[\w-]+)/$','execute_resource',{'extension':'json'}),
    (r'^(?P<app>[\w\.]+)/(?P<version>[\w\.]+)/(?P<resource_name>[\w-]+)\.(?P<extension>\w+)$','execute_resource'),
)