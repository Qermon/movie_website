from django.test import TestCase
from django.urls import reverse

from film.models import Movies


# Create your tests here.


class TestMovies(TestCase):

    @classmethod
    def setUpTestData(cls):
        genres = ["Comedy", "Drama", "Action"]
        for i in range(30):
            Movies.objects.create(
                title=f"Movie {i}",
                genre=genres[i % len(genres)],
                release_date=2000 + i % 20,
                rating=(i % 11)
            )

    def test_home(self):
        response = self.client.get('')
        self.assertEqual(response.status_code, 200)

    def test_movie_list(self):
        response = self.client.get('/movielist/')
        self.assertEqual(response.status_code, 200)
        self.assertIn('Comedy', response.content.decode())

    def test_pagination(self):
        response = self.client.get('/movielist/')
        self.assertEqual(response.status_code, 200)
        self.assertTrue('is_paginated' in response.context)
        self.assertTrue(response.context['is_paginated'])
        self.assertEqual(len(response.context['page_obj']), 25)

        response = self.client.get('/movielist/?page=2')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.context['page_obj']), 5)

    def test_invalid_url(self):
        response = self.client.get('/movielist/?page=1000')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.context['page_obj']), 0)

    def test_empty_search(self):
        response = self.client.get('/movielist/')
        self.assertEqual(response.status_code, 200)
        self.assertGreater(len(response.context['page_obj']), 0)

    def test_genre_filter(self):
        response = self.client.get('/movielist/')
        self.assertEqual(response.status_code, 200)
        self.assertTrue(all('Comedy' in movie.genre for movie in response.context['page_obj']))

    def test_year_filter(self):
        response = self.client.get('/movielist/')
        self.assertEqual(response.status_code, 200)
        self.assertTrue(all(movie.release_date == 2005 for movie in response.context['page_obj']))

    def test_genres_in_context(self):
        response = self.client.get('/movielist/')
        self.assertEqual(response.status_code, 200)
        self.assertIn('genres', response.context)
        self.assertEqual(
            response.context['genres'],
            ["Action", "Comedy", "Drama", "Thriller", "Romance", "Horror", "Sci-Fi", "Fantasy", "Prison"]
        )
