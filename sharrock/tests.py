"""
Unit tests for Sharrock
"""
import unittest
from sharrock.client import HttpClient, ResourceClient

class ClientTests(unittest.TestCase):
    """
    Client tests using example.
    """
    def setUp(self):
        """
        Runs before each test.
        """
        self.c = HttpClient('http://localhost:8000/api','sharrock_example','1.0')
    
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

class ResourceClientTests(unittest.TestCase):
    """
    Tests for resource client.
    """
    def setUp(self):
        """
        Runs before each test.
        """
        self.c = ResourceClient('http://localhost:8000/resources','sharrock_resource_example','1.0','meresource')
    
    def tearDown(self):
        """
        Runs after each test.
        """
        self.c = None
    
    def test_get(self):
        """
        Tests the GET op.
        """
        response = self.c.get()
        self.assertEquals('Get Method executed!',response)
    
    def test_post(self):
        """
        Tests the POST op.
        """
        response = self.c.post(params={'name':'posttest'})
        self.assertEquals('Posted posttest',response)
    
    def test_put(self):
        """
        Tests the PUT op.
        """
        response = self.c.put(params={'name':'puttest'})
        self.assertEquals('Put this:puttest',response)
    
    def test_delete(self):
        """
        Tests the delete op.
        """
        response = self.c.delete()
        self.assertEquals('Aaaarrrggghhhh!  I\'m meeelllltttiiinnnngggg!',response)
