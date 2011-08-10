"""
View functions for Sharrock.
"""
from saaspire.sharrock import registry
from django.shortcuts import render_to_response
from django.http import Http404

def directory(request,extension='html'):
	"""
	Gets a complete directory of the function descriptors.
	"""
	descriptors = [descriptor.to_dict() for descriptor in registry.descriptor_registry.values()]
	return render_to_response('sharrock/directory.%s' % extension,{'descriptors':descriptors})


def describe_service(request,service_name,extension='html'):
	"""
	Gets a function descriptor.
	"""
	try:
		return render_to_response('sharrock/descriptor.%s' % extension,
								  {'descriptor':registry.descriptor_registry[service_name]})
	except KeyError:
		raise Http404
