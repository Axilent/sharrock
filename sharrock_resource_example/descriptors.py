from sharrock.descriptors import Descriptor, UnicodeParam, Resource

version = '1.0'

class GetMe(Descriptor):
    """
    Gets a hello world message.
    """
    visible = False

    def execute(self,request,data,params):
        return 'Get Method executed!'
    

class PostMe(Descriptor):
    """
    Posts a hello world message.
    """
    visible = False

    name = UnicodeParam('name',required=True,description='The name to post.')

    def execute(self,request,data,params):
        posted_name = params['name']
        return 'Posted %s' % posted_name

class PutMe(Descriptor):
    """
    Puts a hello world message.
    """
    visible = False

    name = UnicodeParam('name',required=True,description='The name to put.')

    def execute(self,request,data,params):
        put_name = params['name']
        return 'Put this:%s' % put_name

class DeleteMe(Descriptor):
    """
    Deletes it.
    """
    visible = False

    def execute(self,request,data,params):
        return 'Aaaarrrggghhhh!  I\'m meeelllltttiiinnnngggg!'


class MeResource(Resource):
    """
    A resource that you can get,post,put and delete.
    """
    get = GetMe()
    post = PostMe()
    put = PutMe()
    delete = DeleteMe()

class PartialResource(Resource):
    """
    A resource with only one method implemented.
    """
    get = GetMe()
