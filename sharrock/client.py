"""
Automatic client for Sharrock.
"""
import json
import urllib
import base64
import requests
from sys import flags
import logging

log = logging.getLogger('sharrock')

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
        if not value is None:
            int(value)
    
    def float_check(self,value):
        if not value is None:
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
    def __init__(self,service_url,app,version,descriptor,auth_user='',auth_password=''):
        self.service_url = '%s/%s/%s' % (service_url,app,version)
        self.descriptor = descriptor
        self.params = {}
        for param in self.descriptor['params']:
            required = True if param['required'] == 'True' else False
            self.params[param['name']] = ParamValidator(param['name'],param['type'],required)
        
        self.user = auth_user
        self.password = auth_password
    
    def check_params(self,params):
        """
        Checks the parameters.
        """
        [validator.check(params) for validator in self.params.values()]
    
    def process_response(self,response):
        """
        Processes response from the server.
        """
        if response.status_code >= 400:
            # error
            raise ServiceException(response.status_code,response.text)
        else:
            log.debug('Processing response text: %s' % response.text)
            return response.json(strict=False)
    
    def do_get(self,params):
        """
        Makes a get request.
        """
        response = requests.get('%s/%s.json' % (self.service_url,self.descriptor['slug']),
                                params=params,
                                auth=(self.user,self.password))
        
        return self.process_response(response)
    
    def do_post(self,data=None,params={}):
        """
        Makes a post request.  If data is present it will be presented as the body,
        otherwise params will be presented.  If both are defined an exception will
        be thrown.
        """
        if data and params:
            raise ValueError('Either data or params can be submitted to be the POST body, but not both.')
        
        post_data = json.dumps(data) if data else params
        
        response = requests.post('%s/%s.json' % (self.service_url,self.descriptor['slug']),
                                 data=post_data,
                                 auth=(self.user,self.password))
        
        return self.process_response(response)
    
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
    def __init__(self,service_url,app,version,auth_user='',auth_password=''):
        """
        Constructor.
        """
        self._service_url = service_url
        self._app = app
        self._version = version
        self._services = {}
        self.user = auth_user
        self.password = auth_password
    
    def _cache_descriptor(self,descriptor_name,force=False):
        """
        Caches the specified descriptor locally.
        """
        if not descriptor_name in self._services or force:
            response = requests.get('%s/describe/%s/%s/%s.json' % (self._service_url,self._app,self._version,descriptor_name))
            self._services[descriptor_name] = HttpService(self._service_url,
                                                          self._app,
                                                          self._version,
                                                          response.json(strict=False),
                                                          auth_user=self.user,
                                                          auth_password=self.password)
    
    def call(self,service_name,data=None,params={},force_descriptor_update=False,local_param_check=True,method=None):
        """
        Calls the specified service.  Will build the service locally if it has not been cached.
        """
        self._cache_descriptor(service_name,force=force_descriptor_update)
        service = self._services[service_name]
        if local_param_check:
            if data:
                service.check_params(data)
            else:
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
        
        def __call__(self,data=None,local_param_check=True,**kwargs):
            """
            Call hook for the service method.
            """
            return self.parent.call(self.service_name,data=data,params=kwargs,local_param_check=local_param_check)

######################
### RESTful Client ###
######################

class ResourceOperation(object):
    """
    Represents a method call (GET, POST, PUT or DELETE) on a resource.
    """
    def __init__(self,service_url,app,version,resource_slug,descriptor,http_method,auth_user='',auth_password=''):
        self.service_url = service_url
        self.app = app
        self.version = version
        self.resource_slug = resource_slug
        self.descriptor = descriptor
        self.http_method = http_method
        self.params = {}
        for param in self.descriptor['params']:
            required = True if param['required'] == 'True' else False
            self.params[param['name']] = ParamValidator(param['name'],param['type'],required)
        
        self.user = auth_user
        self.password = auth_password
    
    def check_params(self,params):
        """
        Checks the parameters.
        """
        [validator.check(params) for validator in self.params.values()]
    
    def process_response(self,response):
        """
        Processes response from the server.
        """
        if response.status_code >= 400:
            # error
            raise ServiceException(response.status_code,response.text)
        else:
            return response.json(strict=False)
    
    def _url(self):
        """
        Constructs the resource url.
        """
        return '%s/%s/%s/%s.json' % (self.service_url,self.app,self.version,self.resource_slug)
    
    def __call__(self,data=None,params=None,local_params_check=True):
        """
        Calls the http method.
        """
        # sanity check
        if data and params:
            raise ValueError('Either data or params can be submitted, but not both.')
        
        if local_params_check:
            if data:
                self.check_params(data)
            else:
                self.check_params(params)
        
        response = None
        
        if self.http_method == 'GET':
            response = requests.get(self._url(),params=params,auth=(self.user,self.password))
        elif self.http_method == 'DELETE':
            response = requests.delete(self._url(),params=params,auth=(self.user,self.password))
        elif self.http_method == 'POST':
            if data:
                response = requests.post(self._url(),data=json.dumps(data),auth=(self.user,self.password))
            else:
                response = requests.post(self._url(),params=params,auth=(self.user,self.password))
        else:
            if data:
                response = requests.put(self._url(),data=json.dumps(data),auth=(self.user,self.password))
            else:
                response = requests.put(self._url(),params=params,auth=(self.user,self.password))
        
        return self.process_response(response)

class ResourceClient(object):
    """
    A client for the Sharrock REST api.  An instance of the RestfulClient
    represents a single resource.
    """
    def __init__(self,service_url,app,version,resource_slug,auth_user='',auth_password=''):
        self._service_url = service_url
        self._app = app
        self._version = version
        self._resource_slug = resource_slug
        self._descriptor = None
        self.get = None
        self.post = None
        self.put = None
        self.delete = None
        self.user = auth_user
        self.password = auth_password
        self._cache_descriptor()
    
    def _cache_descriptor(self,force=False):
        """
        Locally caches the resource descriptor.
        """
        if not self._descriptor or force:
            response = requests.get('%s/describe/%s/%s/%s.json' % (self._service_url,self._app,self._version,self._resource_slug))
            self._descriptor = response.json(strict=False)

            if 'get' in self._descriptor:
                self.get = ResourceOperation(self._service_url,self._app,self._version,self._resource_slug,self._descriptor['get'],'GET',auth_user=self.user,auth_password=self.password)
            if 'post' in self._descriptor:
                self.post = ResourceOperation(self._service_url,self._app,self._version,self._resource_slug,self._descriptor['post'],'POST',auth_user=self.user,auth_password=self.password)
            if 'put' in self._descriptor:
                self.put = ResourceOperation(self._service_url,self._app,self._version,self._resource_slug,self._descriptor['put'],'PUT',auth_user=self.user,auth_password=self.password)
            if 'delete' in self._descriptor:
                self.delete = ResourceOperation(self._service_url,self._app,self._version,self._resource_slug,self._descriptor['delete'],'DELETE',auth_user=self.user,auth_password=self.password)

class ModelResourceClient(object):
    """
    A client for a model resource.
    """
    def __init__(self,service_url,app,version,model_resource_slug,auth_user='',auth_password=''):
        self._service_url = service_url
        self._app = app
        self._version = version
        self._model_resource_slug = model_resource_slug
        self.user = auth_user
        self.password = auth_password
    
    def _process_response(self,response):
        """
        Processes response from the server.
        """
        if response.status_code >= 400:
            # error
            raise ServiceException(response.status,response.text)
        else:
            return response.json(strict=False)
    
    def _service(self,method,context,**attrs):
        """
        Http service implementation
        """
        response = None
        url = '%s/%s/%s/%s/%s.json' % (self._service_url,self._app,self._version,self._model_resource_slug,context)
        
        if method == 'GET':
            response = requests.get(url,auth=(self.user,self.password))
        elif method == 'DELETE':
            response = requests.delete(url,auth=(self.user,self.password))
        elif method == 'POST':
            response = requests.post(url,data=attrs,auth=(self.user,self.password))
        else:
            response = requests.put(url,data=attrs,auth=(self.user,self.password))
        
        return self._process_response(response)
    
    def list(self):
        """
        Lists the model resources.
        """
        return self._service('GET','list')
    
    def get(self,pk):
        """
        Gets the model specified by the id.
        """
        return self._service('GET',pk)
    
    def create(self,**attrs):
        """
        Creates a new model with the specified data.
        """
        return self._service('POST','create',**attrs)
    
    def update(self,pk,**attrs):
        """
        Updates an existing model.
        """
        return self._service('PUT',pk,**attrs)
    
    def delete(self,pk):
        """
        Deletes an existing model.
        """
        return self._service('DELETE',pk)

