
from rest_framework import viewsets, mixins, status

from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import IsAuthenticated

from rest_framework.decorators import action
from rest_framework.response import Response

from core.models import Tag, Ingredient, Recipe
from recipe.serializers import (TagSerializer, 
                                IngredientSerializer, 
                                RecipeSerializer, 
                                RecipeDetailSerializer, 
                                RecipeImageSerializer)


class BaseRecipeAttViewSet(viewsets.GenericViewSet, mixins.ListModelMixin, mixins.CreateModelMixin):
    """ ViewSet base for recipe elements """
    authentication_classes = (TokenAuthentication, )
    permission_classes = (IsAuthenticated, )

    def get_queryset(self):
        """ Return a queryset to authenticated user """
        return self.queryset.filter(user=self.request.user).order_by('-name')

    def perform_create(self, serializer):
        """ Create a new Recipe Element """
        serializer.save(user=self.request.user)


class TagViewSet(BaseRecipeAttViewSet):
    """ Manage Tags in the data base """
    serializer_class = TagSerializer
    queryset = Tag.objects.all()


class IngredientViewSet(BaseRecipeAttViewSet):
    """ Manage Ingredients in the data base """
    serializer_class = IngredientSerializer
    queryset = Ingredient.objects.all()


class RecipeViewSet(viewsets.ModelViewSet):
    """ Manage Recipe in the data base """
    serializer_class = RecipeSerializer
    queryset = Recipe.objects.all()
    authentication_classes = (TokenAuthentication, )
    permission_classes = (IsAuthenticated, )

    def _params_to_int(self, qs):
        """ Cast IDs string list to integer list """
        return [int(str_id) for str_id in qs.split(',')]

    def get_queryset(self):
        """ Return a recipes to authenticated user """
        tags = self.request.query_params.get('tags')
        ingredients = self.request.query_params.get('ingredients')
        queryset = self.queryset

        if tags:
            tags_ids = self._params_to_int(tags)
            queryset = queryset.filter(tags__id__in=tags_ids)
        if ingredients:
            ingredients_ids = self._params_to_int(ingredients)
            queryset = queryset.filter(ingredients__id__in=ingredients_ids)

        return queryset.filter(user=self.request.user)

    def get_serializer_class(self):
        """ Return a serializer_class """
        if self.action == 'retrieve':
            return RecipeDetailSerializer  
        elif self.action == 'upload_image':
            return RecipeImageSerializer
        return self.serializer_class
    
    def perform_create(self, serializer):
        """ Create a new Recipe """
        serializer.save(user=self.request.user)

    @action(methods=['POST'], detail=True, url_path='upload-image')
    def upload_image(self, request, pk=None):
        """ Upload image to Recipe """
        recipe = self.get_object()
        serializer = self.get_serializer(
            recipe,
            data=request.data
        )

        if serializer.is_valid():
            serializer.save()
            return Response(
                serializer.data,
                status=status.HTTP_200_OK
            )

        return Response(
            serializer.errors,
            status=status.HTTP_400_BAD_REQUEST
        )






for row in reader:
    print(f'Id to be imported:{row["id"]}')
    coord = maps.get_coords(row['city'])
    customers.append(
        Customer(
            first_name=row['first_name'],
            last_name=row['last_name'],
            email=row['email'],
            gender=row['gender'],
            company=row['company'],
            city=row['city'],
            title=row['title'],
            latitude= coord['Latitude'],
            longitude=coord['Longitude'])
    )