from django.contrib.auth.models import User
from django.core.cache import cache
from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator
from django.db.models import Avg
from django.utils.timezone import now


class Actors(models.Model):
    actor_names = models.CharField(max_length=255, null=True, db_index=True)
    image_actors = models.URLField(null=True, blank=True)
    descrip_actors = models.TextField(null=True, blank=True)

    class Meta:
        verbose_name = 'Actor'
        verbose_name_plural = 'Actors'

    def __str__(self):
        return self.actor_names


class Movies(models.Model):
    title = models.CharField(max_length=255, verbose_name='name', db_index=True)
    description = models.TextField(null=True, blank=True)
    release_date = models.PositiveIntegerField(null=True, blank=True)
    image = models.URLField(null=True, blank=True)
    rating = models.FloatField(null=True, default=0)
    rating2 = models.CharField(max_length=255, null=True, blank=True, default='')
    directors = models.CharField(max_length=255, null=True, blank=True)
    writers = models.CharField(max_length=255, default='Unknown', blank=True)
    duration = models.CharField(max_length=255, null=True, blank=True)
    movie_actors = models.ManyToManyField(Actors, through='MovieActor', related_name='movies')
    genre = models.CharField(max_length=255, blank=True)

    class Meta:
        verbose_name = 'Film'
        verbose_name_plural = 'Films'

    def get_cached_avg_rating(movie):
        cache_key = f'movie_{movie.id}_avg_rating'
        avg_rating = cache.get(cache_key)
        if avg_rating is None:
            avg_rating = movie.ratings.aggregate(Avg('user_rate'))['user_rate__avg']
            if avg_rating is not None:
                cache.set(cache_key, avg_rating)
        return avg_rating

    def __str__(self):
        return self.title


class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    favorite_actors = models.ManyToManyField('Actors', blank=True, related_name='favorite')
    favorite_movies = models.ManyToManyField('Movies', blank=True, related_name='favorite')
    avatar = models.ImageField(
        upload_to='avatars/',
        null=True,
        blank=True
    )

    class Meta:
        verbose_name = 'User Profile'
        verbose_name_plural = 'User Profiles'

    def __str__(self):
        return f"Profile of {self.user.username}"


class Rating(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='ratings')
    movie = models.ForeignKey('Movies', on_delete=models.CASCADE, related_name='ratings')
    user_rate = models.PositiveIntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(10)],
        verbose_name='Rating'
    )
    review = models.TextField(null=True, blank=True, verbose_name='Review')
    time_create = models.DateTimeField(auto_now_add=True)
    time_update = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Rating'
        verbose_name_plural = 'Ratings'

    def __str__(self):
        return f"{self.user.username} rated {self.movie.title} - {self.user_rate}/10"


class MovieActor(models.Model):
    movie = models.ForeignKey(Movies, on_delete=models.CASCADE)
    actor = models.ForeignKey(Actors, on_delete=models.CASCADE)
    role = models.CharField(max_length=255, null=True, blank=True)

    class Meta:
        unique_together = ('movie', 'actor')
        verbose_name = 'MovieActor'
        verbose_name_plural = 'MovieActors'
        ordering = ['?']


class Notification(models.Model):
    INFORMATIVE = 'informative'
    ATTENTION = 'attention'
    CRITICAL = 'critical'
    LEVEL_CHOICES = [
        (INFORMATIVE, 'Informative'),
        (ATTENTION, 'Attention'),
        (CRITICAL, 'Critical'),
    ]

    recipient = models.ForeignKey(User, on_delete=models.CASCADE, related_name='notifications')
    text = models.TextField()
    level = models.CharField(max_length=12, choices=LEVEL_CHOICES, default=INFORMATIVE)
    created_at = models.DateTimeField(default=now)

    def __str__(self):
        return f'Notification for {self.recipient.username}'
