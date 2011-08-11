"""
View functions for Sharrock.
"""
from saaspire.sharrock import registry
from django.shortcuts import render_to_response
from django.http import Http404

def check_extension(extension):
	if not extension in ['html','xml','json']:
		raise Http404

def directory(request,extension='html'):
	"""
	Gets a complete directory of the function descriptors.
	"""
	check_extension(extension)

	descriptors = [descriptor for descriptor in registry.descriptor_registry.values()]
	return render_to_response('sharrock/directory.%s' % extension,{'descriptors':descriptors})


def describe_service(request,service_name,extension='html'):
	"""
	Gets a function descriptor.
	"""
	check_extension(extension)

	try:
		return render_to_response('sharrock/descriptor.%s' % extension,
								  {'descriptor':registry.descriptor_registry[service_name]})
	except KeyError:
		raise Http404

def execute_service(request,service_name,extension='json'):
	"""
	Executes the named service.
	"""
	check_extension(extension)

	try:
		service = registry.descriptor_registry[service_name]
	except KeyError:
		raise Http404
