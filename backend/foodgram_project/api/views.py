from django.db.models import Sum
from django.http import HttpResponse
from django.shortcuts import get_object_or_404
from django_filters import rest_framework as filters
from rest_framework import status, viewsets
from rest_framework.decorators import api_view, permission_classes
from rest_framework.generics import ListAPIView
from rest_framework.pagination import PageNumberPagination
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from recipes.models import (FavoriteRecipes, Ingredient, Recipe, ShoppingCart,
                            Tag)
from users.models import Subscription, User

from .filters import IngredientNameFilter, RecipeFilter
from .permissions import IsAdminOrAuthorOrReadonly
from .serializers import (FavoriteRecipesSerializer, IngredientSerializer,
                          RecipeCreateUpdateSerializer, RecipeIngredient,
                          RecipeListSerializer, ShoppingCartSerializer,
                          SubscriptionSerializer, TagSerializer,
                          UserSubscrptionSerializer)


class RecipeViewSet(viewsets.ModelViewSet):
    queryset = Recipe.objects.all()
    pagination_class = PageNumberPagination
    permission_classes = (IsAdminOrAuthorOrReadonly,)
    filter_backends = (filters.DjangoFilterBackend,)
    filterset_class = RecipeFilter

    def get_serializer_class(self):
        if self.request.method == 'GET':
            return RecipeListSerializer
        return RecipeCreateUpdateSerializer


class IngredientViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer
    permission_classes = (AllowAny,)
    pagination_class = None
    filter_backends = (IngredientNameFilter, )
    search_fields = ('^name', )


class TagViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Tag.objects.all()
    serializer_class = TagSerializer
    permission_classes = (AllowAny,)
    pagination_class = None


class ShoppingCartView(APIView):

    permission_classes = (IsAuthenticated,)

    def post(self, request, id):
        data = {
            'user': request.user.id,
            'recipe': id
        }
        recipe = get_object_or_404(Recipe, id=id)
        if not ShoppingCart.objects.filter(
           user=request.user, recipe=recipe).exists():
            serializer = ShoppingCartSerializer(
                data=data, context={'request': request}
            )
            if serializer.is_valid():
                serializer.save()
                return Response(
                    serializer.data, status=status.HTTP_201_CREATED)
        return Response(status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, id):
        recipe = get_object_or_404(Recipe, id=id)
        if ShoppingCart.objects.filter(
           user=request.user, recipe=recipe).exists():
            ShoppingCart.objects.filter(
                user=request.user, recipe=recipe
            ).delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        return Response(status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET'])
@permission_classes([IsAdminOrAuthorOrReadonly])
def download_shopping_list(request):
    ingredients = RecipeIngredient.objects.filter(
        recipe__shopping_cart__user=request.user
    ).values(
        'ingredients__name', 'ingredients__measurement_unit'
    ).annotate(amount=Sum('amount'))
    shopping_list = []
    for index in range(len(ingredients)):
        shopping_list.append(
            f"{ingredients[index]['ingredients__name']} - "
            f"{ingredients[index]['amount']} "
            f"{ingredients[index]['ingredients__measurement_unit']}\n"
        )
    filename = 'shopping_list'
    response = HttpResponse(shopping_list, 'Content-Type: application/pdf')
    response['Content-Disposition'] = f'attachment; filename="{filename}.pdf"'
    return response


class FavoriteRecipesView(APIView):
    permission_classes = (IsAuthenticated,)
    pagination_class = PageNumberPagination

    def post(self, request, id):
        data = {
            'user': request.user.id,
            'recipe': id
        }
        if not FavoriteRecipes.objects.filter(
           user=request.user, recipe__id=id).exists():
            serializer = FavoriteRecipesSerializer(
                data=data, context={'request': request}
            )
            if serializer.is_valid():
                serializer.save()
                return Response(
                    serializer.data, status=status.HTTP_201_CREATED)
        return Response(status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, id):
        recipe = get_object_or_404(Recipe, id=id)
        if FavoriteRecipes.objects.filter(
           user=request.user, recipe=recipe).exists():
            FavoriteRecipes.objects.filter(
                user=request.user, recipe=recipe
            ).delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        return Response(status=status.HTTP_400_BAD_REQUEST)


class SubscriptionView(APIView):

    permission_classes = (IsAuthenticated,)
    pagination_class = PageNumberPagination

    def post(self, request, id):
        data = {'user': request.user.id, 'author': id}
        serializer = SubscriptionSerializer(
            data=data,
            context={'request': request}
        )

        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, id):
        author = get_object_or_404(User, id=id)

        if Subscription.objects.filter(
            user=request.user,
            author=author
        ).exists():
            subscription = get_object_or_404(
                Subscription,
                user=request.user,
                author=author
            )
            subscription.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        return Response(status=status.HTTP_400_BAD_REQUEST)


class UserSubscriptionsView(ListAPIView):

    permission_classes = (IsAuthenticated,)
    pagination_class = PageNumberPagination

    def get(self, request):
        user = request.user
        queryset = User.objects.filter(author__user=user)
        page = self.paginate_queryset(queryset)
        serializer = UserSubscrptionSerializer(
            page,
            many=True,
            context={'request': request}
        )
        return self.get_paginated_response(serializer.data)
