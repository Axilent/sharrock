"""
URLs for Sharrock resource layer.
"""
from django.conf.urls.defaults import *

urlpatterns = patterns('sharrock.views',
	(r'^(?P<app>[\w\.]+)/(?P<version>[\w\.]+)/(?P<resource_name>[\w-]+)/$','execute_resource',{'extension':'json'}),
	(r'^(?P<app>[\w\.]+)/(?P<version>[\w\.]+)/(?P<resource_name>[\w-]+)\.(?P<extension>\w+)$','execute_resource'),
)