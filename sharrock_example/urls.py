"""
URLs for Sharrock Example.
"""
from django.conf.urls.defaults import *

urlpatterns = patterns('',
    (r'^api/',include('sharrock.urls')),
    (r'^resources/',include('sharrock.resource_urls')),
)