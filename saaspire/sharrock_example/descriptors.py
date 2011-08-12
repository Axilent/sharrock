"""
Sharrock descriptors for example.
"""
from saaspire.sharrock.descriptors import Descriptor, UnicodeParam, IntegerParam, FloatParam, ListParam, DictParam

class SimpleService(Descriptor):
	"""
	This Is A Simple Service
	------------------------

	This is a simple service, without any params.  It is *double plus* good.

	*	Yo
	*	Dawg

	Some more info.

	1.  What
	2.  Up
	"""
	version = "1.0"

class ParameterizedService(Descriptor):
	"""
	This service has parameters.
	----------------------------

	It is the *dogs bollocks*.
	"""
	version = "1.0"

	foo = UnicodeParam('foo',required=True,description='This is the foo.  It has no spleem.')
	bar = IntegerParam('bar')

class HelloWorld(Descriptor):
	"""
	This simple service simply says *hello* back to whichever name is supplied, or to *world* if
	no name is supplied.
	"""
	version = "1.0"

	name = UnicodeParam('name',required=False,default='world',description='The name to address.  Will address world if no name specified.')

	def execute(self,request,data,params):
		"""
		Executes service.
		"""
		name = params['name']
		return 'Hello %s!' % name

class PostData(Descriptor):
	"""
	A service to which a json data object is posted.
	"""
	version = "1.0"

	def execute(self,request,data,params):
		"""
		Executes the service.
		"""
		bar = data['foo']
		return {'grommit':bar}
