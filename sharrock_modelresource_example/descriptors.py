from sharrock.modelresource import ModelResource
from django.contrib.auth.models import User

version = '1.0'

class UserResource(ModelResource):
    """
    ModelResource for a User.
    """
    model = User
