"""
Descriptors are definitions for functions.
"""
import markdown

class MalformedDescriptor(Exception):
	"""
	A programming error indicating a function descriptor that has been improperly
	formatted.
	"""
	pass

class DescriptorMetaclass(type):
	"""
	Metaclass for descriptors.
	"""
	def __new__(cls,name,bases,attrs):
		"""
		Constructs a new descriptor class.
		"""
		# New attribute dictionary
		new_attrs = {'serializer_dict':{},'params':{}}

		# Params - make accessor methods
		def make_accessor_method(name,param_instance):
			def _accessor(self,param_name,raw):
				return param_instance.get(param_name,raw)
			
			return _accessor

		for attribute_name, attribute_value in attrs.items():
			if isinstance(Param,attribute_value):
				accessor = make_accessor_method(attribute_value)
				new_attrs['get_%s' % attribute_name] = accessor
				new_attrs['params'][attribute_name] = attribute_value
			elif isinstance(Serializer,attribute_value):
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

	def execute(self,request,**kwargs):
		"""
		Executes the function.
		"""
		# TODO
	
	@property
	def name(self):
		return self.__class__.__name__
	
	@property
	def docs(self):
		return markdown.markdown(self.__doc__)
	
	@property
	def docs_plain(self):
		return self.__doc__ 

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
	
	def get(self,raw):
		"""
		Accessor for param value.  Wraps requirements.
		"""
		if raw is None and self.required:
			raise ParamRequired(self.name)
		elif raw is None and self.default is None:
			return None
		elif raw is None:
			return self.process(self.default)
		else:
			return self.process(raw)
	
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
		return json.dumps(python_object)
	
	def deserialize(self,serialized_object):
		return json.loads(serialized_object)

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
