from django.test import TestCase
from django.contrib.auth import get_user_model
from django.urls import reverse

from rest_framework.test import APIClient
from rest_framework import status

from core.models import Tag, Recipe
from recipe.serializers import TagSerializer

TAGS_URL = reverse('recipe:tag-list')

class PublicTagsApiTest(TestCase):
    """ Test to public tags """
    def setUp(self):
        self.client = APIClient()

    def test_login_required(self):
        """ Test that login is required to get tags """
        res = self.client.get(TAGS_URL)
        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)

class PrivateTagsApiTest(TestCase):
    """ Test to private tags """
    def setUp(self):
        self.user = get_user_model().objects.create_user(
            email='test@example.com',
            password='testpassword123',
            name='Test User'
        )
        self.client = APIClient()
        self.client.force_authenticate(user=self.user)

    def test_retrieve_tags(self):
        """ Test that get tags """
        Tag.objects.create(user=self.user, name='Meat')
        Tag.objects.create(user=self.user, name='Banana')

        res = self.client.get(TAGS_URL)
        tags = Tag.objects.all().order_by('-name')
        serializer = TagSerializer(tags, many=True)

        self.assertEqual(res.status_code,status.HTTP_200_OK)
        self.assertEqual(res.data, serializer.data)
        
    def test_tags_limited_to_user(self):
        """ Test that tags returns are of the user """
        user2 = get_user_model().objects.create_user(
            email='user2@example.com',
            password='testpassword2',
        )

        Tag.objects.create(user=user2, name='Raspberry')
        tag = Tag.objects.create(user=self.user, name='Comfort Food')

        res = self.client.get(TAGS_URL)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(len(res.data),1)
        self.assertEqual(res.data[0]['name'], tag.name)

    def test_create_tag_succefully(self):
        """ Test that creating a valid tag """
        payload = {'name': 'Simple'}
        self.client.post(TAGS_URL, payload)

        exists = Tag.objects.filter(
            user=self.user,
            name=payload['name']
        ).exists()
        self.assertTrue(exists)

    def test_create_tag_invalid(self):
        """ Test that creating a invalid tag """
        payload = {'name': ''}
        res = self.client.post(TAGS_URL, payload)

        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

    def test_retrieve_tags_assigned_to_recipes(self):
        """ Test that fitter tags are assigned to a recipe """
        tags1 = Tag.objects.create(user=self.user, name='Breakfast')
        tags2 = Tag.objects.create(user=self.user, name='Lunch')
        recipe = Recipe.objects.create(
            title='Coriander eggs on toast',
            time_minutes=10,
            price=5.00,
            user=self.user
        )
        recipe.tags.add(tags1)

        res = self.client.get(TAGS_URL, {'assigned_only': 1})

        serializer1 = TagSerializer(tags1)
        serializer2 = TagSerializer(tags2)

        self.assertIn(serializer1.data, res.data)
        self.assertNotIn(serializer2.data, res.data)



