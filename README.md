Sharrock
========

Sharrock is a Python-based RPC framework design for easy integration into Django.  It was created because of my frustrations with the way that many existing REST-based RPC frameworks work.  Sharrock is based on the idea that while sometimes it is a good idea to represent RPC as resources (the REST model), other times plain old function calls are what you want.

The central idea of Sharrock is the *descriptor*, a declarative model that both represents the function call at the code level, and additionally provides automatically generated API documentation.

Following the tradition of naming Django projects after Jazz musicians, Sharrock is named after [Sonny Sharrock](http://en.wikipedia.org/wiki/Sonny_Sharrock "Sonny Sharrock Wikipedia page").


Basic Parts
-----------
*	A *function descriptor* syntax that provides information in both a machine and human readable format about the available functions a service provides, including details of acceptable parameters and return values.  The function descriptor also provides the basis for *automated API documentation*.
*	A *transport layer* that handles function calls and their return values.  Initially Sharrock uses HTTP as a transport layer, but later on I'd like to add a ProtocolBuffer transport.
*	*Serialization* of objects in both JSON and XML.  In addition serialization of function descriptors as human-readable HTML.
*	A *handler* framework for Django, providing hooks to integrate Sharrock into a django app.
*	A Python *RPC Client* for Sharrock, making it easy to build client code against a Sharrock service by using the function descriptors.
*   An optional *REST* layer that allows functions to be rolled up into resources, and a ResourceClient in Python that allows for RESTful interaction.
*   An even more optional ResourceModel layer that binds the Resource functionality to a Django model.  See "Model Resources" below for more info.

Requirements
------------

Sharrock requires the following libraries:

*   *[Django](http://www.djangoproject.com)* 1.2 or above
*   *[httplib2](http://code.google.com/p/httplib2/)* For the client libs.
*   *[Markdown](http://www.freewisdom.org/projects/python-markdown/) for docstring parsing.

Installation
------------

*   Use pip to install Sharrock:

    pip install -e git://github.com/Saaspire/sharrock.git#egg=Sharrock

*   Add "sharrock" to your INSTALLED_APPS.
*   In each of your apps that you with to use Sharrock, create a *descriptors.py* module.
*   In your root urls, add the following line to your urlpatterns:

    (r'^api/',include('sharrock.urls')), # The initial context "api" can be whatever you want.

*   Optional: if using the resource layer, mount the resource urls.

    (r'^resources/',include('sharrock.resource_urls')),


Descriptors
===========

Remote procedures are created by defining *descriptors*.  A descriptor is a declarative model of a remote procedure call (in the way that a Django model is a declarative model of a database table).

    from sharrock.descriptors import Descriptor, UnicodeParam

    class HelloWorld(Descriptor):
        """
        Hello world!
        ============
        """
        name = UnicodeParam('name',default=None,description='The name to address.')

        def execute(self,request,data,params):
            name = params['name']
            if name:
                return 'Hello %s!' % name
            else:
                return 'Hello world!'

A simple function descriptor consists of a subclass of Descriptor.  At minimum it must contain a docstring for the class, and an "execute" method.  The execute method is called when the function is called remotely.

Descriptor.execute
------------------

The execute method should contain the business logic of the remote procedure.  It will be passed 3 significant arguments:

*   *request*: The Django request object.
*   *data*: A deserialized data object (usually desesrialized from json).  If there is a data object, there will be no params.
*   *params*: A dictionary of key/value params.  If there are params there will be no data object.

Any value the execute method returns should be something that can be serialized back into a response for the client.

Parameters
----------
All parameters can be imported from *sharrock.descriptors*.  There are several types of parameters available, each parameter type will attempt to cast incoming values to whatever is its preferred data type.  Incoming values that cannot be cast to the data type will raise an exception.  Parameter types include:

*   UnicodeParam
*   IntegerParam
*   FloatParam
*   ListParam
*   DictParam

Parameters must be instantiated with the first argument being the name of the parameter, and then with the following optional keyword arguments:

*   *required*: If True, this parameter is required.  False by default.  If a call is made on the function and a required parameter is missing, a ParamRequired exception will be raised.
*   *default*: The default value for the parameter, if it is not specified.  Only makes sense for non-required parameters.
*   *description*: The description of the parameter, to be used in the automatically generated documentation.

Descriptor Docstrings
---------------------
The documentation system will automatically create documentation based on the descriptor docstring.  It will read documentation in Markdown format and format it appropriately from that.

API Versions
============

The version of your API can simply be defined by setting the following variable in your descriptors.py file:

version = "1.0"

If you do not define the version for your API, Sharrock will automatically define it as "0.1dev".

Maintaining Multiple Versions of an API
---------------------------------------

Sometimes it makes sense to maintain multiple versions of the same app's API.  In this case, make descriptors a package (a folder with an __init__.py file).  Within the package, create individual modules (files) for each version of the API you want to maintain.  In each version module, make sure you define the *"version"* variable.

In the package's __init__.py file, make sure you include each version module in the __all__ variable.

Executing Functions
===================

Functions may be executed with the following url pattern:

    (api mount point)/(app)/(version)/(function slug)

So for example, if you had an app called "MyApp", the version "1.0" and the function "MyFunction", and the mountpoint for Sharrock was "/api/" then the call would be:

    /api/myapp/1.0/myfunction/

Functions don't inheirantly expect any particular http method, although if they are expecting a data upload they'll only be able to get that through POST and PUT methods.

API Documentation
=================

API documentation can be found at the "/dir/" context.  For example:

    /api/dir/

Specific app and version documentation can be found by appending the app and version to the context:

    /api/dir/myapp/1.0/

Specific descriptors can be retrieved through the 'describe' context, in various formats (with HTML as default).  For example:

    /api/describe/myapp/1.0/myfunction/

or

    /api/describe/myapp/1.0/myfunction.json
    /api/describe/myapp/1.0/myfunction.xml

HttpClient
==========

*sharrock.client.HttpClient* is a simple RPC client class designed to consume Sharrock function descriptors and execute remote Sharrock procedure calls.  It is inspired by the Python XML-RPC client.

The HttpClient will locally cache descriptors and, by default, perform local param checking on function calls.  It uses JSON serialization to communicate with the server.

HttpClient.__init__
-------------------

*   *service_url*: The full URL to the server, including the API mount context. For example "http://example.com/api".
*   *app*: The app to address, for example "myapp".
*   *version*: The version of the API to use, for example "1.0".
*	*auth_user=USERNAME*: Optional.  Will pass the username to basic auth.
*	*auth_password=PASSWORD*: Optional. Will pass the password to basic auth.

To use the HttpClient, simply execute method calls on it, with the slugified name of the function as the method name.  All methods take the optional keyword argument "data" for data objects to be serialized and uploaded, and treat other keyword arguments as params.

For example, taking the "HelloWorld" descriptor from above:

    from sharrock.client import HttpClient

    c = HttpClient('http://example.com/api','myapp','1.0')
    c.helloworld(name='Loren')

A Note About Basic Auth and the HttpClient
------------------------------------------

The HttpClient (and ResourceClient) will accept the keyword args `auth_user` and `auth_password` which they'll use in Basic Auth: concatenating them together, base64 encoding them and appending them to an `Authorization: Basic` header.

When working with the Axilent platform, the API token is used as the `auth_user`, with no password being set.

The same client example as above, but using basic auth:

	from sharrock.client import HttpClient
	
	c = HttpClient('http://example.com/api','myapp','1.0',auth_user='Loren',auth_password='MYSEKRIT')
	c.helloworld(name='Fred')

Creating RESTful Services
=========================

In Sharrock, REST is implemented as an optional layer on top of the basic function layer.  This is based on the concept that while sometimes functionality is appropriately modeled as resources, sometimes its better to represent it as plain old procedure calls.

Resources are also defined in your descriptors.py file.  Resources simply reference Descriptor objects and assign them to appropriate HTTP methods.

    from sharrock.descriptors import Descriptor, Resource

    class GetHello(Descriptor):
        """
        Gets a big hello.
        """
        def execute(self,request,data,params):
            return 'Why hello!'
    
    class Greeting(Resource):
        """
        A resource for a greeting.
        """
        get = GetHello()

In the above example, the GetHello function has been assigned to the "get" method of the Greeting resource.  Resources may assign Descriptors to "get", "post", "put" and "delete" attributes.

Hiding Descriptors
------------------

When using Descriptors as resource methods, often its desirable to prevent the descriptors from being individually accessible as functions in the API.  This can be done by setting their "visible" attribute as False.

    class MyGetter(Descriptor):
        """
        Gets stuff.
        """
        visible = False

        def execute(self,request,data,params):
            pass
    
    class MyResource(Resource):
        get = MyGetter()

Now the MyGetter function will be available via the MyResource resource, but not as an individual function.

Executing Resources
-------------------

Resources are executed via the following URL pattern:

    (resource mount point)/(app)/(version)/(resource slug)

for example:

    /resources/myapp/1.0/myresource

Sharrock will route the request to the appropriate descriptor, based on the http method of the request.  If the incoming request uses a method that has not been defined in the resource the Sharrock will return a 403 (Method Not Allowed) error code.

Resource Client
---------------
Sharrock supplies *sharrock.client.ResourceClient*, an HTTP client for REST-style operations.  An instance of a ResourceClient represents a single resource, with the various HTTP method operations available for it.

*   `ResourceClient.__init__(service_url,app,version,resource_slug,auth_user='',auth_password='')`: Instantiates the client towards a single resource.

*   `ResourceClient.get(data=None,params=None,local_params_check=True)`
*   `ResourceClient.post(data=None,params=None,local_params_check=True)`
*   `ResourceClient.put(data=None,params=None,local_params_check=True)`
*   `ResourceClient.delete(data=None,params=None,local_params_check=True)`

The HTTP methods all have the same signature: Either a JSON object may be posted as data, or key/value params (but not both) and a flag that indicates params should be checked on the client (setting it to False supresses this function).  If the resource descriptor does not define a method, the corresponding attribute will be None instead of a method.  All of the HTTP methods will return a deserialized response from the server.

Exactly like the HttpClient, the ResourceClient will append an `Authorization: Basic` header to requests if the `auth_user` or `auth_password` keyword args are set.

Model Resources
===============
A common case is to use the REST layer to directly manipulate Django models.  While many REST frameworks assume this is the center case, I have purposefully packaged it as an add-on to the core REST functionality, which is itself an add-on to the basic RPC functionality.  One could accomplish the same thing with a Resource implementation, so just think of this as a shortcut.

Model Resources are easy to define:

    from sharrock.modelresource import ModelResource
    from myapp.models import MyModel

    class MyModelResource(ModelResource):
        """Resource for my model."""
        model = MyModel

That's about it.  Your model resources are defined in the same descriptors.py file where you would put any other descriptors or ressource definitions.  Model resources are mounted under the resource URL mount-point, the same as other resources.

Model Resource Client
---------------------
Sharrock provides a special client for model resources,  sharrock.client.ModelResourceClient, to provide convenience methods for model CRUD operations.  Usage is very similar to the ResourceClient.

*   ModelResourceClient.__init__(service_url,app,version,resource_slug)

*   ModelResourceClient.list(): Lists all of the models
*   ModelResourceClient.get(model_pk): Retrieves the model with the specified key.
*   ModelResourceClient.create(**attrs): Creates a new model with the specified attributes.
*   ModelResourceClient.update(model_pk,**attrs): Updates an existing model.
*   ModelResourceClient.delete(model_pk): Deletes the specified model resource client.


