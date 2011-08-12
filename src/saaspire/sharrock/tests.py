"""
Unit tests for Sharrock
"""
import unittest
from saaspire.sharrock.client import HttpClient

class ClientTests(unittest.TestCase):
	"""
	Client tests using example.
	"""
	def setUp(self):
		"""
		Runs before each test.
		"""
		self.c = HttpClient('http://localhost:8000/api')
	
	def tearDown(self):
		"""
		Runs after each test.
		"""
		self.c = None
	
	def test_hello_world(self):
		"""
		Tests the hello world app.
		"""
		result = self.c.helloworld()
		self.assertEquals(result,'Hello world!')

		new_result = self.c.helloworld(name='Loren')
		self.assertEquals(new_result,'Hello Loren!')
	
	def test_post_data(self):
		"""
		Tests the post data service.
		"""
		result = self.c.postdata(data={'foo':'bar'})
		self.assertEquals(result['grommit'],'bar')
