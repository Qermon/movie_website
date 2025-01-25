import random
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.cache import cache
from django.core.paginator import Paginator
from django.db.models import Count, Avg, F
from django.http import HttpResponseForbidden
from django.shortcuts import get_object_or_404, redirect
from django.template.defaultfilters import slugify
from django.views.generic import ListView, DetailView, TemplateView
from film.forms import RatingForm
from film.models import Movies, Actors, Rating, UserProfile
from django.shortcuts import render
from film.tasks import update_avg_rating, add_favorite_movie, add_favorite_actor


class HomeView(ListView):
    model = Movies
    template_name = 'index.html'
    context_object_name = 'page_obj'
    paginate_by = 5

    def get_queryset(self):
        search_query = self.request.GET.get('search', '')
        if search_query:
            return Movies.objects.filter(title__icontains=search_query)

        shuffled_movies = cache.get('shuffled_movies')
        if not shuffled_movies:
            movies_list = list(Movies.objects.prefetch_related('movie_actors'))
            random.shuffle(movies_list)
            cache.set('shuffled_movies', movies_list, timeout=24 * 60 * 60)
            shuffled_movies = movies_list

        return shuffled_movies


class ShowMovie(DetailView):
    model = Movies
    template_name = 'moviesingle.html'
    context_object_name = 'movie'
    pk_url_kwarg = 'id'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['movies'] = Movies.objects.all()
        context['form'] = RatingForm()
        return context


class ShowCelebrity(DetailView):
    model = Actors
    template_name = 'celebritysingle.html'
    context_object_name = 'actor'
    pk_url_kwarg = 'id'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['actors'] = Actors.objects.all()
        return context


def movie_list(request):
    search_query = request.GET.get('search', '')
    genre_query = request.GET.get('genre', '')
    year_query = request.GET.get('year', '')
    rating_min = request.GET.get('rating_min', '')
    rating_max = request.GET.get('rating_max', '')
    query = Movies.objects.prefetch_related('movie_actors')

    if search_query:
        query = query.filter(title__icontains=search_query)

    if genre_query:
        query = query.filter(genre__icontains=genre_query)

    if year_query:
        query = query.filter(release_date=year_query)

    if rating_min:
        query = query.filter(rating__gte=float(rating_min))
    if rating_max:
        query = query.filter(rating__lte=float(rating_max))

    sort = request.GET.get('sort')
    if sort == 'high_score':
        query = query.order_by('-rating')
    elif sort == 'low_score':
        query = query.order_by('rating')
    elif sort == 'random':
        query = query.order_by('?')
    elif sort == 'title':
        query = query.order_by('title')

    paginator = Paginator(query, 25)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    genres = ["Action", "Comedy", "Drama", "Thriller", "Romance", "Horror", "Sci-Fi", "Fantasy", "Prison"]

    context = {
        'page_obj': page_obj,
        'genres': genres,
    }
    return render(request, 'movielist.html', context)


def celebrity_list(request):
    search_query = request.GET.get('search', '')

    if search_query:
        actors = Actors.objects.filter(actor_names__icontains=search_query)
    else:
        actors = Actors.objects.all()

    paginator = Paginator(actors, 100)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    context = {
        'page_obj': page_obj,
    }

    return render(request, 'celebritylist.html', context)


@login_required(login_url='/users/register/')
def add_rating(request, title, id):
    movie = get_object_or_404(Movies, id=id, title=title)

    if request.method == 'POST':
        form = RatingForm(request.POST)
        if form.is_valid():
            rating = form.save(commit=False)
            rating.movie = movie
            rating.user = request.user
            rating.save()
            update_avg_rating.delay(movie.id)

            return redirect('movie-detail', title=movie.title, id=movie.id)
    else:
        form = RatingForm()

    return render(request, 'moviesingle.html', {'movie': movie, 'form': form})


def top_users_comments(request):
    top_users = UserProfile.objects.annotate(
        num_comments=Count('user__ratings'),
        avg_rating=Avg('user__ratings__user_rate')
    ).order_by('-num_comments')[:25]

    for user in top_users:
        if user.avg_rating is not None:
            user.avg_rating = round(user.avg_rating, 1)
        else:
            user.avg_rating = 0

    return render(request, 'top_users.html', {'top_users': top_users})


@login_required(login_url='/users/register/')
def delete_rating(request, id):
    rating = get_object_or_404(Rating, id=id, user=request.user)
    movie_id = rating.movie.id
    if request.method == 'POST':
        rating.delete()
        update_avg_rating.delay(movie_id)
        return redirect('/')


@login_required(login_url='/users/register/')
def add_to_favorite(request, movie_id):
    movie = get_object_or_404(Movies, id=movie_id)
    user_profile = request.user.profile

    if movie in user_profile.favorite_movies.all():
        messages.info(request, f'{movie.title} вже в списку улюблених!')
    else:
        add_favorite_movie.delay(request.user.id, movie_id)
        messages.success(request, f'{movie.title} додано до списку улюблених.')

    return redirect('movie-detail', title=movie.title, id=movie.id)


@login_required(login_url='/users/register/')
def delete_favorite_movie(request, id):
    movie = get_object_or_404(Movies, id=id)
    user_profile = request.user.profile

    if movie in user_profile.favorite_movies.all():
        user_profile.favorite_movies.remove(movie)

    return redirect('user_favorite_grid')


@login_required(login_url='/users/register/')
def add_actor_favorite(request, actor_id):
    actor = get_object_or_404(Actors, id=actor_id)
    user_profile = request.user.profile

    if actor in user_profile.favorite_actors.all():
        messages.info(request, f'{actor.actor_names} вже в списку улюблених!')
    else:
        add_favorite_actor.delay(request.user.id, actor_id)
        messages.info(request, f'{actor.actor_names} додано до списку улюблених.')

    slugified_actor_name = slugify(actor.actor_names)

    return redirect('actor-detail', actor_names=slugified_actor_name, id=actor_id)


@login_required(login_url='/users/register/')
def delete_favorite_actor(request, id):
    actor = get_object_or_404(Actors, id=id)
    user_profile = request.user.profile

    if actor in user_profile.favorite_actors.all():
        user_profile.favorite_actors.remove(actor)

    return redirect('user_favorite_grid')


@login_required(login_url='/users/register/')
def user_profile(request):
    return render(request, 'userprofile.html')


@login_required(login_url='/users/register/')
def user_favorite_movies(request):
    user_profile = UserProfile.objects.get(user=request.user)
    favorite_movies = user_profile.favorite_movies.all()
    favorite_actors = user_profile.favorite_actors.all()
    return render(request, 'userfavoritelist.html', {'favorite_movies': favorite_movies}, {'favorite_actors': favorite_actors})


@login_required(login_url='/users/register/')
def change_avatar(request):
    if request.method == 'POST':
        avatar = request.FILES.get('avatar')
        if avatar:
            profile = request.user.profile
            profile.avatar = avatar
            profile.save()
            messages.success(request, 'Avatar updated successfully!')
        else:
            messages.error(request, 'Please select an image.')
    return redirect('user_profile')


def movie_grid(request):
    return render(request, 'moviegrid.html')


def user_favorite_grid(request):
    return render(request, 'userfavoritegrid.html')


def user_favorite_list(request):
    return render(request, 'userfavoritelist.html')


@login_required(login_url='/users/register/')
def user_rate(request, user_id):
    rated_movies = Rating.objects.filter(user_id=user_id).select_related('movie')
    return render(request, 'userrate.html', {'rated_movies': rated_movies})


class Landing(TemplateView):
    template_name = 'landing.html'


class Error(TemplateView):
    template_name = '404.html'


class ComingSoon(TemplateView):
    template_name = 'comingsoon.html'
