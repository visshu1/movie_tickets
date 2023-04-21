from django.urls import path
from . import views

urlpatterns = [
    path('movie-theatre-list/', views.movie_theatre_list, name='movie-theatre-list'),
    path('create-booking/', views.create_booking, name='create-booking'),
    path('create-movie/', views.create_movie, name='create-movie'),
    path('movies/', views.movie_theatres, name='movies'),
    path('add-theatre/', views.add_theatre, name='add_theatre'),
    path('get_theatre/', views.get_theatre, name='theatre_name')
]

