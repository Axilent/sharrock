"""
URLs for Sharrock Example.
"""
from django.conf.urls.defaults import *

urlpatterns = patterns('',
	(r'^api/',include('saaspire.sharrock.urls')),
)