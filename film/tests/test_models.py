from django.contrib.auth.models import User
from django.test import TestCase

from film.models import Movies, Actors, MovieActor, UserProfile


class MoviesModelTest(TestCase):

    @classmethod
    def setUpTestData(cls):
        actor1 = Actors.objects.create(actor_names='Fred Hechinger')
        actor2 = Actors.objects.create(actor_names='Russell Crowe')
        movie = Movies.objects.create(
            title='Kraven the Hunter',
            description='A movie about Kraven the Hunter, a Marvel character.',
            release_date=2024,
            image='https://www.imdb.com/title/tt8790086/mediaviewer/rm797010177/?ref_=tt_ov_i',
            rating=0,
            rating2='8.5/10',
            directors='J.C. Chandor',
            writers='Art Marcum, Matt Holloway',
            duration='2h 7min',
            genre='Action, Adventure'
        )

        MovieActor.objects.create(movie=movie, actor=actor1, role='Chameleon')
        MovieActor.objects.create(movie=movie, actor=actor2, role='Nikolai Kravinoff')
        user = User.objects.create_user(username='usertest', password='testpassword')
        profile = UserProfile.objects.create(user=user)
        profile.favorite_movies.add(movie)
        profile.favorite_actors.add(actor1, actor2)

    def test_movie_has_actors(self):
        movie = Movies.objects.get(title='Kraven the Hunter')
        actors = movie.movie_actors.all()
        self.assertEqual(actors.count(), 2)
        self.assertIn('Fred Hechinger', [actor.actor_names for actor in actors])
        self.assertIn('Russell Crowe', [actor.actor_names for actor in actors])

    def test_actor_movies(self):
        actor = Actors.objects.get(actor_names='Fred Hechinger')
        movies = actor.movies.all()
        self.assertEqual(movies.count(), 1)
        self.assertEqual(movies[0].title, 'Kraven the Hunter')

    def test_role(self):
        movie_actor = MovieActor.objects.get(role='Chameleon')
        self.assertEqual(movie_actor.actor.actor_names, 'Fred Hechinger')
        self.assertEqual(movie_actor.movie.title, 'Kraven the Hunter')

    def test_favorite_movies(self):
        user = User.objects.get(username='usertest')
        profile = user.profile
        favorite_movies = profile.favorite_movies.all()
        self.assertEqual(favorite_movies.count(), 1)
        self.assertEqual(favorite_movies[0].title, 'Kraven the Hunter')

    def test_favorite_actors(self):
        user = User.objects.get(username='usertest')
        profile = user.profile
        favorite_actors = profile.favorite_actors.all()
        self.assertEqual(favorite_actors.count(), 2)
        self.assertIn('Fred Hechinger', [actor.actor_names for actor in favorite_actors])
        self.assertIn('Russell Crowe', [actor.actor_names for actor in favorite_actors])

    def test_title_label(self):
        movie = Movies.objects.get(id=1)
        field_label = movie._meta.get_field('title').verbose_name
        self.assertEqual(field_label, 'name')

    def test_title_max_length(self):
        movie = Movies.objects.get(id=1)
        max_length = movie._meta.get_field('title').max_length
        self.assertEqual(max_length, 255)

    def test_release_date_nullable(self):
        movie = Movies.objects.get(id=1)
        nullable = movie._meta.get_field('release_date').null
        self.assertTrue(nullable)

    def test_image_field_blank(self):
        movie = Movies.objects.get(id=1)
        blank = movie._meta.get_field('image').blank
        self.assertTrue(blank)

    def test_default_rating(self):
        movie = Movies.objects.get(id=1)
        self.assertEqual(movie.rating, 0)

    def test_directors_field(self):
        movie = Movies.objects.get(id=1)
        self.assertEqual(movie.directors, 'J.C. Chandor')

    def test_object_name_is_title(self):
        movie = Movies.objects.get(id=1)
        self.assertEqual(str(movie), 'Kraven the Hunter')

    def test_ordering(self):
        self.assertIn('?', Movies._meta.ordering)

    def test_genre_blank(self):
        movie = Movies.objects.get(id=1)
        field_blank = movie._meta.get_field('genre').blank
        self.assertTrue(field_blank)

    def test_duration_field_nullable(self):
        movie = Movies.objects.get(id=1)
        nullable = movie._meta.get_field('duration').null
        self.assertTrue(nullable)

    def test_verbose_name_plural(self):
        verbose_name_plural = Movies._meta.verbose_name_plural
        self.assertEqual(verbose_name_plural, 'Films')

