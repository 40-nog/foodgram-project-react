from django.contrib import admin

from .models import (FavoriteRecipes, Ingredient, Recipe, RecipeTag,
                     ShoppingCart, Tag)


class IngredientInline(admin.TabularInline):
    model = Recipe.ingredients.through
    extra = 1


class TagInline(admin.TabularInline):
    model = RecipeTag
    extra = 1


class RecipeAdmin(admin.ModelAdmin):
    list_display = ('name', 'author', 'favorites')
    list_filter = ('author', 'name', 'tags')
    search_fields = ('tags__name',)
    inlines = (IngredientInline, TagInline)

    def favorites(self, obj):
        if FavoriteRecipes.objects.filter(recipe=obj).exists():
            return FavoriteRecipes.objects.filter(recipe=obj).count()


class IngredientAdmin(admin.ModelAdmin):
    list_display = ('name', 'measurement_unit')
    list_filter = ('name',)
    search_fields = ('name',)


class TagAdmin(admin.ModelAdmin):
    list_display = ('name', 'color', 'slug')
    list_filter = ('name',)
    search_fields = ('name', 'slug')


class FavoritesAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'recipe')
    search_fields = ('user__username', 'user__email')


class ShoppingCartAdmin(admin.ModelAdmin):
    list_display = ('user', 'recipe')
    search_fields = ('user__username', 'user__email')


admin.site.register(Recipe, RecipeAdmin)
admin.site.register(Ingredient, IngredientAdmin)
admin.site.register(Tag, TagAdmin)
admin.site.register(FavoriteRecipes, FavoritesAdmin)
admin.site.register(ShoppingCart, ShoppingCartAdmin)
