"""
Main function registry for Sharrock.
"""
from django.conf import settings
from django.template.defaultfilters import slugify
import inspect
from saaspire.sharrock.descriptors import Descriptor

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
		module = get_module(app_path)
		if hasattr(module,'descriptors'):
			descriptor_module = getattr(module,'descriptors')
			load_descriptors(descriptor_module)

def load_descriptors(descriptor_module):
	"""
	Loads descriptors in the module into the directory.
	"""
	for cls in inspect.getmembers(descriptor_module):
		if inspect.isclass(cls) and issubclass(cls,Descriptor):
			descriptor_registry[slugify(cls.__name__)] = cls() # put instance of the descriptor into the registry

