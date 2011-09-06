"""
Unit tests for Sharrock
"""
import unittest
from sharrock.client import HttpClient, ResourceClient, ModelResourceClient
from django.contrib.auth.models import User

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

class ModelResourceClientTests(unittest.TestCase):
    """
    Tests a model resource.
    """
    def setUp(self):
        """
        Runs before each test.
        """
        self.c = ModelResourceClient('http://localhost:8000/resources','sharrock_modelresource_example','1.0','userresource')
        self.tom = User.objects.create(username='Tom')
        self.dick = User.objects.create(username='Dick')
        self.harry = User.objects.create(username='Harry')
    
    def tearDown(self):
        """
        Runs after each test.
        """
        self.harry.delete()
        self.dick.delete()
        self.tom.delete()
        self.c = None
    
    def test_list(self):
        """
        Tests the listing of a resource.
        """
        results = self.c.list()
        usernames = [result['username'] for result in results]
        self.assertTrue('Tom' in usernames)
        self.assertTrue('Dick' in usernames)
        self.assertTrue('Harry' in usernames)
    
    def test_get(self):
        """
        Tests the get function.
        """
        tom_dict = self.c.get(self.tom.pk)
        self.assertEquals(tom_dict['username'],self.tom.username)
    
    def test_create(self):
        """
        Tests create function.
        """
        zelda_dict = self.c.create(username='Zelda')
        zelda_model = User.objects.get(pk=zelda_dict['id'])
        self.assertEquals('Zelda',zelda_model.username)
    
    def test_update(self):
        """
        Tests the update function.
        """
        self.c.update(self.tom.pk,first_name='Thomas',last_name='Wayne')
        tom = User.objects.get(pk=self.tom.pk)
        self.assertEquals(tom.first_name,'Thomas')
        self.assertEquals(tom.last_name,'Wayne')
    
    def test_delete(self):
        """
        Tests the delete function.
        """
        tom_pk = self.tom.pk
        self.c.delete(tom_pk)
        self.assertRaises(User.DoesNotExist,User.objects.get,pk=tom_pk)




