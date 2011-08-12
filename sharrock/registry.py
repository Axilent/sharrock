"""
Main function registry for Sharrock.
"""
from django.conf import settings
from django.template.defaultfilters import slugify
import inspect

descriptor_registry = {}

def get_module(module_name):
    """
    Imports and returns the named module.
    """
    module = __import__(module_name)
    components = module_name.split('.')
    for comp in components[1:]:
        module = getattr(module,comp)
    return module

def build_registry():
	"""
	Builds the function descriptor registry.
	"""
	for app_path in settings.INSTALLED_APPS:
		print 'Sharrock examinging app',app_path
		if app_path != 'sharrock': # don't load yourself
			try:
				module = get_module('%s.descriptors' % app_path)
				print 'app',app_path,'has descriptors to register...'
				load_descriptors(module)
			except AttributeError:
				print app_path,'has no descriptors module'

def load_descriptors(descriptor_module):
	"""
	Loads descriptors in the module into the directory.
	"""
	from sharrock.descriptors import Descriptor

	for name,attribute in inspect.getmembers(descriptor_module):
		print 'examinging attribute',name
		if inspect.isclass(attribute) and issubclass(attribute,Descriptor) and not attribute is Descriptor:
			print 'registering descriptor',name
			descriptor_registry[slugify(name)] = attribute() # put instance of the descriptor into the registry
	
	print 'Sharrock registered descriptors:',descriptor_registry.keys()

