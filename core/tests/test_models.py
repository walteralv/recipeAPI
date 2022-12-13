from django.test import TestCase
from django.contrib.auth import get_user_model

from unittest.mock import patch

from core.models import User, Tag, Ingredient, Recipe, recipe_image_file_path

def sample_user(email='test@example.com', password='testpassword123'):
    """ Create a sample user """
    return get_user_model().objects.create_user(email, password)

class ModelTest(TestCase):

    def test_create_user_with_email_succeful(self):
        """ Test to create a new user, successfuly """

        email = 'test@example.com'
        password = 'testpassword123'

        user = get_user_model().objects.create_user(
            email=email,
            password=password,
        )

        self.assertEqual(user.email, email)
        self.assertTrue(user.check_password(password)) 

    def test_new_user_email_normalized(self):
        """ Test to check if email is normalized """
        
        email = 'test@EXAMPLE.COM'
        password = 'testpassword123'

        user = get_user_model().objects.create_user(
            email=email,
            password=password,
        )

        self.assertEqual(user.email, email.lower())
    
    def test_new_user_email_invalid(self):
        """ Test to check if email is invalid """
        with self.assertRaises(ValueError):
            get_user_model().objects.create_user(None, 'Tpassword123')

    def test_create_new_superuser(self):
        """ Test to create a new super user, successfuly """
        email = 'test@example.com'
        password = 'testpassword123'

        user = get_user_model().objects.create_superuser(
            email=email, 
            password=password
        )

        self.assertTrue(user.is_superuser)
        self.assertTrue(user.is_staff)

    def test_tag_str(self):
        """ Test that reprecente a Tag as a string"""
        tag = Tag.objects.create(
            user=sample_user(),
            name='Meat'
        )
        self.assertEqual(str(tag), tag.name)
    
    def test_ingredient_str(self):
        """ Test that reprecente an Ingredient as a string """
        ingredient = Ingredient.objects.create(
            user=sample_user(),
            name='Banana',
        )
        self.assertEqual(str(ingredient), ingredient.name)

    def test_recipe_str(self):
        """ Test that reprecente an Ingredient as a string """
        recipe = Recipe.objects.create(
            user=sample_user(),
            title='Steak and mushrooms sauce',
            time_minutes=5,
            price=5.00,
        )
        self.assertEqual(str(recipe), recipe.title)

    @patch('uuid.uuid4')
    def test_recipe_file_name_uuid(self,mock_uuid):
        """ Tets that an image has been saved in the correct place """
        uuid = 'test-uuid'
        mock_uuid.return_value = uuid
        file_path = recipe_image_file_path(None, 'myimage.jpg')
        exp_path = f'uploads/recipe/{uuid}.jpg'

        self.assertEqual(file_path, exp_path)
