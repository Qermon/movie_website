"""
URL configuration for djangoProject project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import path, include

from djangoProject import settings
from film import views


urlpatterns = [
    path('admin/', admin.site.urls),
    path('users/', include('users.urls', namespace='users')),
    path('accounts/', include('allauth.urls')),
    path('', views.HomeView.as_view(), name='home'),
    path('moviesingle/', views.ShowMovie.as_view(), name='movie_single'),
    path('moviegrid/', views.movie_grid, name='movie_grid'),
    path('movielist/', views.movie_list, name='movie_list'),
    path('celebritylist/', views.celebrity_list, name='celebrity_list'),
    path('celebritysingle/', views.ShowCelebrity.as_view(), name='celebrity_single'),
    path('top_users/', views.top_users_comments, name='top_users'),
    path('userprofile./', views.user_profile, name='user_profile'),
    path('change-avatar/', views.change_avatar, name='change_avatar'),
    path('add-to-favorite/<int:movie_id>/', views.add_to_favorite, name='add_to_favorite'),
    path('add_actor_favorite/<int:actor_id>/', views.add_actor_favorite, name='add_actor_favorite'),
    path('userfavoritegrid/', views.user_favorite_grid, name='user_favorite_grid'),
    path('userrate/<int:user_id>/', views.user_rate, name='user_rate'),
    path('rating/<int:id>/delete/', views.delete_rating, name='delete-rating'),
    path('favorite_movie/<int:id>/delete/', views.delete_favorite_movie, name='delete_favorite_movie'),
    path('favorite_actor/<int:id>/delete/', views.delete_favorite_actor, name='delete_favorite_actor'),
    path('userfavoritelist/', views.user_favorite_list, name='user_favorite_list'),
    path('landing/', views.Landing.as_view(), name='landing'),
    path('404/', views.Error.as_view(), name='404'),
    path('comingsoon/', views.ComingSoon.as_view(), name='comingsoon'),
    path('celebrity/<slug:actor_names>/<int:id>/', views.ShowCelebrity.as_view(), name='actor-detail'),
    path('movie/<str:title>/<int:id>/', views.ShowMovie.as_view(), name='movie-detail'),
    path('movie/<str:title>/<int:id>/add_rating/', views.add_rating, name='add_rating'),


]
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)