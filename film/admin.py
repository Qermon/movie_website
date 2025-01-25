from django.contrib import admin
from django.db.models.functions import Length

from .models import *


@admin.register(Movies)
class MovieAdmin(admin.ModelAdmin):
    list_display = ('id', 'title', 'genre', 'release_date', 'rating', 'description_movies')
    list_display_links = ('id', 'title')
    search_fields = ('title', 'genre')
    list_editable = ('rating', )
    list_filter = ('rating',)
    list_per_page = 25

    @admin.display(ordering=Length('description'))
    def description_movies(self, movies: Movies):
        return f'Description {len(movies.description)} symbols'


@admin.register(Actors)
class ActorAdmin(admin.ModelAdmin):
    list_display = ('id', 'actor_names', 'description_actors')
    list_display_links = ('id', 'actor_names')
    search_fields = ('name',)

    @admin.display(ordering='descrip_actors')
    def description_actors(self, actors: Actors):
        return f'Description {len(actors.descrip_actors)} symbols'


@admin.register(MovieActor)
class MovieActorAdmin(admin.ModelAdmin):
    list_display = ('id', 'movie', 'actor', 'role')
    list_display_links = ('id', 'movie', 'actor', 'role')
    search_fields = ('id', 'movie', 'actor', 'role')


@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'get_favorite_actors', 'get_favorite_movies', 'avatar', )
    list_display_links = ('id', 'user')
    search_fields = ('user__username', )
    list_per_page = 25

    def get_favorite_actors(self, obj):
        return ", ".join([actor.actor_names for actor in obj.favorite_actors.all()])
    get_favorite_actors.short_description = 'Favorite Actors'

    def get_favorite_movies(self, obj):
        return ", ".join([movie.title for movie in obj.favorite_movies.all()])
    get_favorite_movies.short_description = 'Favorite Movies'


@admin.register(Rating)
class RatingAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'movie', 'user_rate', 'review', 'time_create', 'time_update')
    list_display_links = ('id', 'user', 'user_rate', 'review')
    search_fields = ('user__username',)
    list_per_page = 25


admin.site.register(Notification)


