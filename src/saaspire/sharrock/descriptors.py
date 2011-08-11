"""
Descriptors are definitions for functions.
"""
import markdown
from django.template.defaultfilters import slugify

class MalformedDescriptor(Exception):
	"""
	A programming error indicating a function descriptor that has been improperly
	formatted.
	"""
	pass

class ParamRequired(Exception):
	"""
	An exception indicating that a required param has not been supplied.
	"""
	def __init__(self,param_name):
		self.param = param_name
	
	def __unicode__(self):
		return u'%s is a required parameter and has not been specified.' % unicode(self.param)
	
	def __str__(self):
		return unicode(self)	

class Param(object):
	"""
	A parameter for a function.
	"""
	def __init__(self,name,required=False,default=None,description=None):
		self.name = name
		self.required = required
		self.default = default
		self.description = description
	
	def get_from_dict(self,raw_dict):
		"""
		Gets param from raw dict.  If param is missing and required, raises
		ParamRequired, otherwise returns None.
		"""
		raw_value = raw_dict.get(self.name,self.default)
		if raw_value is None and self.required:
			raise ParamRequired(self.name)
		elif raw_value is None:
			return None
		else:
			return self.process(raw_value)
	
	def process(self,raw):
		"""
		Processes the raw value, returning the new value.
		"""
		raise NotImplemented

#######################################################
### Below are Parameters to be used in Descriptors. ###
#######################################################

class UnicodeParam(Param):
	"""
	A parameter with a unicode payload.
	"""
	def process(self,raw):
		return unicode(raw)
	
	@property
	def type(self):
		return 'Unicode'

class IntegerParam(Param):
	"""
	A param with an integer value.
	"""
	def process(self,raw):
		return int(raw)
	
	@property
	def type(self):
		return 'Integer'

class FloatParam(Param):
	"""
	A param with a float value.
	"""
	def process(self,raw):
		return float(raw)
	
	@property
	def type(self):
		return 'Float'

class ListParam(Param):
	"""
	A param with a list of values.
	"""
	def __init__(self,item_param,**kwargs):
		super(ListParam,self).__init__(**kwargs)
		self.item_param = item_param
	
	def process(self,raw):
		return [self.item_param.get(None,raw_item) for raw_item in raw]
	
	@property
	def type(self):
		return 'List'

class DictParam(Param):
	"""
	A param with a dictionary of values.
	"""
	def __init__(self,param_dict,**kwargs):
		super(DictParam,self).__init__(**kwargs)
		self.param_dict = param_dict
	
	def process(self,raw):
		return_dict = {}
		for param_key, param in self.param_dict.items():
			raw_value = None
			try:
				raw_value = raw[param_key]
			except KeyError:
				pass
			return_dict[param_key] = param.get(param_key,raw_value)
		
		return return_dict
	
	@property
	def type(self):
		return 'Dictionary'

###################
### Serializers ###
###################
class UnsupportedSerializationFormat(Exception):
	"""
	Indicates an unsupported serialization format.
	"""
	pass

class Serializer(object):
	"""
	Base class for serializers.
	"""
	def serialize(self,python_object):
		"""
		Serializes the object.  Returns the serialized form of the object.
		"""
		raise NotImplemented
	
	def deserialize(self,serialized_object):
		"""
		Deserialized the object.  Returns python object.
		"""
		raise NotImplemented

import json

class JSONSerializer(Serializer):
	"""
	JSON Serializer.
	"""
	name = 'json'
	
	def serialize(self,python_object):
		if python_object:
			return json.dumps(python_object)
		else:
			return python_object
	
	def deserialize(self,serialized_object):
		if serialized_object:
			return json.loads(serialized_object)
		else:
			return serialized_object

################
### Security ###
################
class AccessDenied(Exception):
	"""
	Indicates the user does not have permission to perform the task.
	"""
	pass

class SecurityCheck(object):
	"""
	Base class for security check.  This base class will allow any user, essentially
	making a public API.
	"""
	def __init__(self,*permissions):
		self.permissions = permissions

	def check(self,request):
		"""
		Checks the request for permission to access the function.  No return value.
		Raises an AccessDenied exception if the request fails the permission check.
		"""
		pass # anyone allowed in base class.

###################
### Descriptors ###
###################

import re

def space_out_camel_case(stringAsCamelCase):
    """
    By Simon Hartley, posted on http://refactormycode.com/codes/675-camelcase-to-camel-case-python-newbie

    Adds spaces to a camel case string.  Failure to space out string returns the original string.
    >>> space_out_camel_case('DMLSServicesOtherBSTextLLC')
    'DMLS Services Other BS Text LLC'
    """
    
    if stringAsCamelCase is None:
        return None

    pattern = re.compile('([A-Z][A-Z][a-z])|([a-z][A-Z])')
    return pattern.sub(lambda m: m.group()[:1] + " " + m.group()[1:], stringAsCamelCase)

class DescriptorMetaclass(type):
	"""
	Metaclass for descriptors.
	"""
	def __new__(cls,name,bases,attrs):
		"""
		Constructs a new descriptor class.
		"""
		if name != 'Descriptor': # don't operate on the base class
			# New attribute dictionary
			new_attrs = {'serializer_dict':{},'params':[]}

			# Name
			if 'verbose_name' in attrs:
				new_attrs['service_name'] = attrs['verbose_name']
			else:
				new_attrs['service_name'] = space_out_camel_case(name)

			# Params group params
			for attribute_name, attribute_value in attrs.items():
				if isinstance(attribute_value,Param):
					new_attrs['params'].append(attribute_value)
				elif isinstance(attribute_value,Serializer):
					new_attrs['serializer_dict'][attribute_value.name] = attribute_value
			
			# If no serializers has been set, set default
			if not new_attrs['serializer_dict']:
				new_attrs['serializer_dict']['json'] = JSONSerializer()
			

			# If no security has been set, set default
			if not 'security' in attrs:
				new_attrs['security'] = SecurityCheck()
			
			# Insist on version
			if not 'version' in attrs:
				raise MalformedDescriptor
			
			attrs.update(new_attrs)
		
		return type.__new__(cls,name,bases,attrs)

class Descriptor(object):
	"""
	Base class for function descriptors.

	Specific descriptor classes should subclass this base class.  They can then
	define the following
	"""
	# Based on metaclass activity - add:
	# serializer/deserializers
	# params, required and optional, default values
	# security hooks
	# API version

	__metaclass__ = DescriptorMetaclass # class factory mounts here

	def serialize(self,python_object,format):
		"""
		Serializes the object.
		"""
		try:
			serializer = self.serializer_dict[format]
			return serializer.serialize(python_object)
		except KeyError:
			raise UnsupportedSerializationFormat
	
	def deserialize(self,serialized_object,format):
		"""
		Deserializes the object.
		"""
		try:
			serializer = self.serializer_dict[format]
			return serializer.deserialize(serialized_object)
		except KeyError:
			raise UnsupportedSerializationFormat

	def execute(self,request,data,params):
		"""
		Executes the function.
		"""
		raise NotImplemented # Subclasses implement
	
	def http_service(self,request,format='json'):
		"""
		Services the request.
		"""
		# 1. Check security
		self.security.check(request)
		print 'performed security check'

		# 2. Deserialize incoming data
		data = self.deserialize(request.raw_post_data,format)
		print 'incoming data deserialized'

		# 3. Get kwargs
		kwargs = None
		if request.method == 'POST':
			kwargs = request.POST.copy()
		else:
			kwargs = request.GET.copy()
		print 'raw kwargs processed'

		# 4. Process params
		param_data = {}
		for param in self.params:
			param_data[param.name] = param.get_from_dict(kwargs)
		print 'params constructed',param_data

		# 5. Execute service
		result = self.execute(request,data,param_data)
		print 'service executed'

		# 6. Serialize result
		return self.serialize(result,format)

	
	@property
	def name(self):
		return self.__class__.__name__
	
	@property
	def slug(self):
		return slugify(self.__class__.__name__)
	
	@property
	def docs(self):
		lines = self.__doc__.splitlines(True)
		docstring = ''
		for line in lines:
			if line.isspace():
				docstring += line
			else:
				docstring += line.lstrip()

		return markdown.markdown(docstring)
	
	@property
	def docs_plain(self):
		return self.__doc__
