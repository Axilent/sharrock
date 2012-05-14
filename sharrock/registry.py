"""
Main function registry for Sharrock.
"""
from django.conf import settings
from django.template.defaultfilters import slugify
import inspect
import os.path

descriptor_registry = {}
resource_registry = {}

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
        if app_path != 'sharrock': # don't load yourself
            try:
                module = get_module('%s.descriptors' % app_path)
                if is_package(module):
                    load_multiple_versions(app_path,module)
                else:
                    load_descriptors(app_path,module)
            except ImportError:
                pass # no descriptors in that module

def load_multiple_versions(app_path,package):
    """
    Loads multiple versions of an app's API.  Multiple versions are stored in submodules of
    a 'descriptors' package within the app.  (When there is only one version of an API,
    'descriptors' is a simple module).
    """
    for sublabel in package.__all__:
        submodule = get_module('%s.%s' % (package.__name__,sublabel))
        load_descriptors(app_path,submodule)

def load_descriptors(app_path,descriptor_module):
    """
    Loads descriptors in the module into the directory.
    """
    from sharrock.descriptors import Descriptor, Resource
    from sharrock.modelresource import ModelResource

    version = '0.1dev' # default version
    if hasattr(descriptor_module,'version'):
        version = getattr(descriptor_module,'version')
    
    module_deprecated = None
    if hasattr(descriptor_module,'deprecated'):
        # entire module is deprecated
        module_deprecated = descriptor_module.deprecated

    for name,attribute in inspect.getmembers(descriptor_module):
        if inspect.isclass(attribute) and issubclass(attribute,Descriptor) and not attribute is Descriptor:
            if not hasattr(attribute,'visible') or attribute.visible: # skip over descriptors with visible=False set
                descriptor_registry[(app_path,version,slugify(name))] = attribute(is_deprecated=module_deprecated) # put instance of the descriptor into the registry
        elif inspect.isclass(attribute) and issubclass(attribute,Resource) and not attribute is Resource and not attribute is ModelResource:
            descriptor_registry[(app_path,version,slugify(name))] = attribute(is_deprecated=module_deprecated) # put instance of resource into registry
    

def get_descriptor(app_label,version,descriptor_slug):
    """
    Gets the matching descriptor.
    """
    return descriptor_registry[(app_label,version,descriptor_slug)]

def is_package(module):
    """
    Checks if the specified module is a package.
    """
    return module.__file__.endswith('__init__.py') or module.__file__.endswith('__init__.pyc')

def directory(app_label=None,specified_version=None):
    """
    Creates a directory of service descriptors.
    """
    ensure_registry()
    
    from sharrock.descriptors import Resource
    d = {}
    for key, value in descriptor_registry.items():
        app,version,name = key
        if not app_label or app_label == app:
            app_dict = d.get(app,{})
            if not specified_version or specified_version == version:
                descriptors = app_dict.get(version,{'resources':[],'functions':[]})
                if issubclass(value.__class__,Resource):
                    descriptors['resources'].append(value)
                else:
                    descriptors['functions'].append(value)
                app_dict[version] = descriptors
            d[app] = app_dict
    
    return d

def resource_directory(app_label=None,specified_version=None):
    """
    Creates a directory for resources.
    """
    d = {}
    for key, value in resource_registry.items():
        app,version,name = key
        if not app_label or app_label == app:
            app_dict = d.get(app,{})
            if not specified_version or specified_version == version:
                resources = app_dict.get(version,[])
                resources.append(value)
                app_dict[version] = resources
            d[app] = app_dict
    
    return d

def ensure_registry():
    """
    Loads descriptors if the repository is unpopulated.
    """
    if not descriptor_registry:
        build_registry()

