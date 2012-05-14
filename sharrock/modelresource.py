"""
This module provides a shortcut to creating resources that are wrapped around
CRUD functionality for a Django model.
"""
from sharrock.descriptors import Resource, Descriptor
from django.conf import settings
import re
import traceback
from datetime import datetime

model_resource_urls = {
                        'list':r'(?P<slug>[\w-]+)/list\.(?P<format>\w+)$',
                        'get':r'(?P<slug>[\w-]+)/(?P<model_id>\d+)\.(?P<format>\w+)$',
                        'update':r'(?P<slug>[\w-]+)/(?P<model_id>\d+)\.(?P<format>\w+)$',
                        'delete':r'(?P<slug>[\w-]+)/(?P<model_id>\d+)\.(?P<format>\w+)$',
                        'create':r'(?P<slug>[\w-]+)/create\.(?P<format>\w+)$',
}

if hasattr(settings,'SHARROCK_MODELRESOURCE_URLS'):
    model_resource_urls = settings.SHARROCK_MODELRESOURCE_URLS

model_patterns = dict((key,re.compile(value)) for key,value in model_resource_urls.items())

class ModelResourceAction(Descriptor):
    """
    Special descriptor subclass that wraps the model manipulation methods.
    """
    def __init__(self,action_label,manipulator,*args,**kwargs):
        super(ModelResourceAction,self).__init__(*args,**kwargs)
        self.manipulator = manipulator
        self.__doc__ = '%s the model.' % action_label

    def execute(self,request,data,params):
        return self.manipulator(request,data,params)


class ModelResource(Resource):
    """
    A resource tied to a Django model.
    """
    def __init__(self,is_deprecated=None):
        self.get = ModelResourceAction('Retrieves or lists',self.do_get)
        self.post = ModelResourceAction('Creates',self.do_post)
        self.put = ModelResourceAction('Updates',self.do_put)
        self.delete = ModelResourceAction('Deletes',self.do_delete)
        super(ModelResource,self).__init__(is_deprecated=is_deprecated)

    ##################################
    ### Model manipulation methods ###
    ##################################
    def _serialize_model(self,model):
        """
        Transforms the model to dictionary format in preparation for serialization.
        """
        raw_dict = dict([(field_name,field_value) for field_name, field_value in model.__dict__.items() if not field_name.startswith('_')])

        # convert date objects
        for key, value in raw_dict.items():
            if isinstance(value,datetime):
                raw_dict[key] = str(value)
        
        return raw_dict
    
    def _get_id(self,op,request):
        """
        Extracts the model id from the request.
        """
        m = model_patterns[op].search(request.path)
        if m:
            return m.groupdict()['model_id']
        else:
            raise KeyError

    def get_model(self,request,data,param_data):
        """
        Accessor for a single model instance.
        """
        model_id = self._get_id('get',request)
        return self._serialize_model(self.model.objects.get(pk=model_id))
    
    def create_model(self,request,data,param_data):
        """
        Creator for a model.
        """
        model_instance = self.model.objects.create(**data)
        return {'id':model_instance.pk}
    
    def update_model(self,request,data,param_data):
        """
        Updator for a model.
        """
        model_instance = self.model.objects.get(pk=self._get_id('update',request))
        for field_name, field_value in data.items():
            setattr(model_instance,field_name,field_value)
        model_instance.save()
        return 'OK'
    
    def delete_model(self,request,data,param_data):
        """
        Deletor for a model.
        """
        model_instance = self.model.objects.get(pk=self._get_id('delete',request))
        model_instance.delete()
        return 'OK'
    
    def list_models(self,request,data,param_data):
        """
        Lists all instances for the model.
        """
        serialized_models = [self._serialize_model(model) for model in self.model.objects.all()]
        if not serialized_models:
            serialized_models = []
        return serialized_models
    
    ##########################
    ### Request Processing ###
    ##########################
    def do_get(self,request,data,param_data):
        """
        GET request handler.
        """
        # This will either be a get or a list
        if self._is_list_request(request):
            return self.list_models(request,data,param_data)
        else:
            return self.get_model(request,data,param_data)
    
    def do_post(self,request,data,param_data):
        """
        POST handler.
        """
        # This should be a create
        return self.create_model(request,data,param_data)
    
    def do_put(self,request,data,param_data):
        """
        PUT handler.
        """
        # This should be an update
        return self.update_model(request,data,param_data)
    
    def do_delete(self,request,data,param_data):
        """
        DELETE handler.
        """
        # This should be a delete
        return self.delete_model(request,data,param_data)
    
    def _is_list_request(self,request):
        m = model_patterns['list'].search(request.path)
        return True if m else False
    
