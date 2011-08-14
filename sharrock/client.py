"""
Automatic client for Sharrock.
"""
import json
import httplib2
import urllib


class ParamException(Exception):
	"""
	Parameter exception base class.
	"""
	def __str__(self):
		return unicode(self)
	
	def __repr__(self):
		return unicode(self)

class MissingParam(ParamException):
	"""
	Indicates a required param is missing.
	"""
	def __init__(self,param_name):
		self.param_name = param_name
	
	def __unicode__(self):
		return u'Missing parameter %s is required.' % self.param_name

class BadParamType(ParamException):
	"""
	Indicates a specified parameter was the wrong data type.
	"""
	def __init__(self,param_name,supplied_param_value,required_data_type):
		self.param_name = param_name
		self.supplied_param_value = supplied_param_value
		self.required_data_type = required_data_type
	
	def __unicode__(self):
		return u'Parameter %s must be of type %s.  Supplied value was:%s' % (self.param_name,self.required_data_type,self.supplied_param_value)

class ParamValidator(object):
	"""
	Validates a parameter.
	"""
	def __init__(self,name,param_type,required=False):
		self.name = name
		self.param_type = param_type
		self.required = required

		# setup checker
		if self.param_type == 'Unicode':
			self.checker = self.unicode_check
		elif self.param_type == 'Integer':
			self.checker = self.integer_check
		elif self.param_type == 'Float':
			self.checker = self.float_check
		elif self.param_type == 'List':
			self.checker = self.list_check
		elif self.param_type == 'Dictionary':
			self.checker = self.dict_check
	
	def unicode_check(self,value):
		unicode(value)
	
	def integer_check(self,value):
		int(value)
	
	def float_check(self,value):
		float(value)
	
	def list_check(self,value):
		if not hasattr(value,'__iter__'):
			raise ValueError
	
	def dict_check(self,value):
		if not hasattr(value,'keys'):
			raise ValueError
	
	def check(self,params):
		"""
		Checks if the param is present (if required) and is of the correct data type.
		"""
		value = params.get(self.name,None)

		# missing check
		if self.required and not value:
			raise MissingParam(self.name)
		
		# type check
		try:
			self.checker(value)
		except ValueError:
			raise BadParamType(self.name,value,self.param_type)

class ServiceException(Exception):
	"""
	Indicates an exception in the remote service.
	"""
	def __init__(self,status_code,content):
		self.status_code = status_code
		self.content = content
	
	def __repr__(self):
		return '%d: %s' % (self.status_code,self.content)
	
	def __str__(self):
		return '%d: %s' % (self.status_code,self.content)

class HttpService(object):
	"""
	Represents a described service.
	"""
	def __init__(self,service_url,app,version,descriptor):
		self.service_url = '%s/%s/%s' % (service_url,app,version)
		self.descriptor = descriptor
		self.params = {}
		for param in self.descriptor['params']:
			required = True if param['required'] == 'True' else False
			self.params[param['name']] = ParamValidator(param['name'],param['type'],required)
		
		self.http = httplib2.Http()
	
	def check_params(self,params):
		"""
		Checks the parameters.
		"""
		[validator.check(params) for validator in self.params.values()]
	
	def process_response(self,response,content):
		"""
		Processes response from the server.
		"""
		if response.status >= 400:
			# error
			raise ServiceException(response.status,content)
		else:
			if content:
				return json.loads(content,strict=False)
			else:
				return None
	
	def do_get(self,params):
		"""
		Makes a get request.
		"""
		response, content = None, None
		if params:
			response, content = self.http.request('%s/%s?%s' % (self.service_url,
															    self.descriptor['slug'],
															    urllib.urlencode(params)),method='GET')
		else:
			response, content = self.http.request('%s/%s' % (self.service_url,
															 self.descriptor['slug']),method='GET')
		
		return self.process_response(response,content)
	
	def do_post(self,data=None,params={}):
		"""
		Makes a post request.  If data is present it will be presented as the body,
		otherwise params will be presented.  If both are defined an exception will
		be throwsn.
		"""
		response, content = None, None
		body = None

		if data and params:
			raise ValueError('Either data or params can be submitted to be the POST body, but not both.')
		
		if data:
			body = json.dumps(data)
		elif params:
			body = urllib.urlencode(params)
		
		if body:
			response, content = self.http.request('%s/%s/' % (self.service_url,
															 self.descriptor['slug']),
												  method='POST',
												  body=body)
		else:
			response, content = self.http.request('%s/%s/' % (self.service_url,
															 self.descriptor['slug']),
												  method='POST')
		
		return self.process_response(response,content)
	
	def call(self,data=None,params={},method='GET'):
		"""
		Calls the service.
		"""
		if method == 'GET':
			return self.do_get(params)
		else:
			return self.do_post(data=data,params=params)

class HttpClient(object):
	"""
	Client for Sharrock.
	"""
	def __init__(self,service_url,app,version):
		"""
		Constructor.
		"""
		self._service_url = service_url
		self._app = app
		self._version = version
		self._services = {}
	
	def _cache_descriptor(self,descriptor_name,force=False):
		"""
		Caches the specified descriptor locally.
		"""
		if not descriptor_name in self._services or force:
			http = httplib2.Http()
			response, content = http.request('%s/describe/%s/%s/%s.json' % (self._service_url,self._app,self._version,descriptor_name),'GET')
			self._services[descriptor_name] = HttpService(self._service_url,self._app,self._version,json.loads(content,strict=False))
	
	def call(self,service_name,data=None,params={},force_descriptor_update=False,local_param_check=True,method=None):
		"""
		Calls the specified service.  Will build the service locally if it has not been cached.
		"""
		self._cache_descriptor(service_name,force=force_descriptor_update)
		service = self._services[service_name]
		if local_param_check:
			service.check_params(params) # local param check
		
		if not method:
			if data:
				method = 'POST'
			else:
				method = 'GET'

		return service.call(data=data,params=params,method=method)
	
	def __getattr__(self,name):
		"""
		Accessor hook for named services.
		"""
		return HttpClient.ServiceMethod(self,name)
	
	class ServiceMethod(object):
		"""
		Wrapper for a service method.
		"""
		def __init__(self,parent,service_name):
			self.parent = parent
			self.service_name = service_name
		
		def __call__(self,data=None,**kwargs):
			"""
			Call hook for the service method.
			"""
			return self.parent.call(self.service_name,data=data,params=kwargs)

		


