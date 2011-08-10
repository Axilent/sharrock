"""
URLs to mount Sharrock functions.
"""
from django.conf.urls.defaults import *

urlpatterns = patterns('saaspire.sharrock.views',
	(r'^dir\.(?P<extension>\w+)$','directory'),
	(r'^dir/$','directory',{'extension':'html'}),
	(r'^describe/(?P<service_name>[\w-]+)\.(?P<extension>\w+)$','describe_service'),
	(r'^describe/(?P<service_name>[\w-]+)/$','describe_service',{'extension':'html'}),
)