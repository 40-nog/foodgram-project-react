from django.urls import include, path
from rest_framework import routers

from .views import (FavoriteRecipesView, IngredientViewSet, RecipeViewSet,
                    ShoppingCartView, SubscriptionView, TagViewSet,
                    UserSubscriptionsView, download_shopping_list)

app_name = 'api'

router = routers.DefaultRouter()

router.register('recipes', RecipeViewSet, basename='recipes')
router.register('ingredients', IngredientViewSet, basename='ingredients')
router.register('tags', TagViewSet, basename='tags')

urlpatterns = (
    path(
        'users/subscriptions/',
        UserSubscriptionsView.as_view(),
        name='subscriptions'
    ),
    path(
        'users/<int:id>/subscribe/',
        SubscriptionView.as_view(),
        name='subscribe'
    ),
    path(
        'recipes/download_shopping_cart/',
        download_shopping_list,
        name='download_shopping_list'
    ),
    path(
        'recipes/<int:id>/shopping_cart/',
        ShoppingCartView.as_view(),
        name='shopping_cart'
    ),
    path(
        'recipes/<int:id>/favorite/',
        FavoriteRecipesView.as_view(),
        name='favorite'
    ),
    path('auth/', include('djoser.urls.authtoken')),
    path('', include('djoser.urls')),
    path('', include(router.urls)),
)
