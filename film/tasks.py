import random
from celery import shared_task
from django.core.cache import cache
from django.db.models import Avg

from film.models import Movies, UserProfile, Actors


@shared_task
def update_avg_rating(movie_id):
    movie = Movies.objects.get(id=movie_id)
    avg_rating = movie.ratings.aggregate(Avg('user_rate'))['user_rate__avg']
    if avg_rating is not None:
        movie.rating = avg_rating
        movie.save()
        cache.set(f'movie_{movie_id}_avg_rating', avg_rating)


@shared_task
def add_favorite_movie(user_id, movie_id):
    user_profile = UserProfile.objects.get(user_id=user_id)
    movie = Movies.objects.get(id=movie_id)
    user_profile.favorite_movies.add(movie)


@shared_task
def add_favorite_actor(user_id, actor_id):
    user_profile = UserProfile.objects.get(user_id=user_id)
    actor = Actors.objects.get(id=actor_id)
    user_profile.favorite_actors.add(actor)


@shared_task
def shuffle_movies_cache():
    movies_list = list(Movies.objects.prefetch_related('movie_actors'))
    random.shuffle(movies_list)
    cache.set('shuffled_movies', movies_list, timeout=24 * 60 * 60)
