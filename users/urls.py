from django.urls import path
from . import views

app_name = 'users'

urlpatterns = [
    path('login/', views.LoginUser.as_view(), name='login'),
    path('logout/', views.logout_user, name='logout'),
    path('register/', views.register, name='register'),
    path('change_pasword/', views.UserPasswordChange.as_view(), name='password_change')

]
