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
	"""
	version = "1.0"

	foo = UnicodeParam('foo')
	bar = IntegerParam('bar')
