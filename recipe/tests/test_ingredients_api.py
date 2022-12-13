from django.test import TestCase
from django.contrib.auth import get_user_model
from django.urls import reverse

from rest_framework import status
from rest_framework.test import APIClient

from core.models import Ingredient
from recipe.serializers import IngredientSerializer

INGREDIENTS_URL = reverse('recipe:ingredient-list')

class PublicIngredientsApiTests(TestCase):
    """ Test to ingredients public access """
    def setUp(self):
        self.client = APIClient()

    def test_login_required(self):
        """ Test that login is required to access to endpoint """
        res = self.client.get(INGREDIENTS_URL)
        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)

class PrivateIngredientsApiTests(TestCase):
    """ Test to ingredients private access """
    def setUp(self):
        self.client = APIClient()
        self.user = get_user_model().objects.create_user(
            email='test@example.com',
            password='testpassword123',
            name='Test user'
        )
        self.client.force_authenticate(self.user)

    def test_retrieve_ingredient_list(self):
        """ Test to retrieve a list of ingredient """
        Ingredient.objects.create(user=self.user, name='milk')
        Ingredient.objects.create(user=self.user, name='cheese')
        
        res = self.client.get(INGREDIENTS_URL)

        ingredients = Ingredient.objects.all().order_by('-name')
        serializer = IngredientSerializer(ingredients, many=True)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, serializer.data)

    def test_ingredient_limited_to_user(self):
        """ Test that the returned ingredients are from the user """
        user2 = get_user_model().objects.create_user(
            email='user2@example.com',
            password='testpassword123',
            name='user2'
        )
        Ingredient.objects.create(user=user2, name='vinagre')
        ingredient = Ingredient.objects.create(user=self.user, name='water')
        
        res = self.client.get(INGREDIENTS_URL)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(len(res.data), 1)
        self.assertEqual(res.data[0]['name'], ingredient.name)

    def test_create_ingredient_success(self):
        """ Test that creating a valid Ingredient """
        payload = {'name': 'chocolate'}
        self.client.post(INGREDIENTS_URL, payload)
        
        exists = Ingredient.objects.filter(
            user=self.user,
            name=payload['name']
        ).exists()

        self.assertTrue(exists)

    def test_create_ingredient_invalid(self):
        """ Test that creating a invalid Ingredient """
        payload = {'name': ''}
        res = self.client.post(INGREDIENTS_URL, payload)
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)





