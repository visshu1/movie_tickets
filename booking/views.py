import json
from datetime import datetime

import redis
from django.core.exceptions import ValidationError
from django.shortcuts import render

# Create your views here.
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from .models import Movie, Theatre, Booking


@csrf_exempt
def create_movie(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        title = data.get('title')
        description = data.get('description')
        release_date_str = data.get('release_date')
        try:
            release_date = datetime.strptime(release_date_str, '%Y-%m-%d').date()
        except ValueError:
            return JsonResponse({'error': 'Invalid release date format'})
        movie = Movie(title=title, description=description, release_date=release_date)
        movie.save()
        return JsonResponse({'message': 'Movie created successfully'})
    else:
        return JsonResponse({'error': 'Invalid request method'})


def movie_theatre_list(request):
    movies = Movie.objects.all()
    # theatres = Theatre.objects.all()
    data = {
        'movies': list(movies.values())
        # 'theatres': list(theatres.values()),
    }
    return JsonResponse(data)


@csrf_exempt
def add_theatre(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        name = data.get('name')
        city = data.get('city')
        state = data.get('state')
        capacity = data.get('capacity')
        if not name or not city or not state or not capacity:
            raise ValidationError("Required data is missing: name, city, state, or capacity.")
        theatres = Theatre.objects.create(name=name, city=city, state=state, capacity=capacity)
        theatres.save()
        theatre_dict = dict(name=theatres.name, city=theatres.city, state=theatres.state, capacity=theatres.capacity)
        return JsonResponse(theatre_dict)


@csrf_exempt
def create_booking(request):
    if request.method == 'POST':
        movie_id = request.POST.get('movie_id')
        theatre_id = request.POST.get('theatre_id')
        show_time = request.POST.get('show_time')
        seats_booked = request.POST.get('seats_booked')
        movie = Movie.objects.get(id=movie_id)
        theatre = Theatre.objects.get(id=theatre_id)
        booking = Booking.objects.create(
            movie=movie,
            theatre=theatre,
            show_time=show_time,
            seats_booked=seats_booked,
        )
        data = {
            'booking_id': booking.id,
        }
        return JsonResponse(data)
    else:
        return JsonResponse({'error': 'Invalid request method'})


r = redis.Redis(host='localhost', port=6379, db=0)


@csrf_exempt
def movie_theatres(request):
    # Define the movies_dict variable before the if statement
    movies_dict = {'movies': []}

    # Check if the data is cached in Redis
    movies_data = r.get('movies_data')
    if movies_data:
        # If cached data is available, update the movies_dict variable
        movies_dict.update(json.loads(movies_data))
    else:
        # If cached data is not available, fetch it from the database
        movies = Movie.objects.all()
        # Convert the queryset to a dictionary and manually serialize the date fields
        movies_dict['movies'] = [
            {
                'id': movie.id,
                'title': movie.title,
                'description': movie.description,
                'release_date': movie.release_date.strftime('%Y-%m-%d'),
            } for movie in movies
        ]
        # Cache the data in Redis
        movies_json = json.dumps(movies_dict)
        r.set('movies_data', movies_json)

    # Return the data as a JSON response
    return JsonResponse(movies_dict)


@csrf_exempt
def get_theatre(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            city = data.get("city")
            theatres = Theatre.objects.filter(city=city)
            if not theatres:
                raise ValidationError("The city you entered does not exists")
            Theatre_names = [[theatre.name, theatre.capacity] for theatre in theatres]
            theatre_dict = {'Theatre_list': Theatre_names}
            return JsonResponse(theatre_dict)
        except ValidationError as e:
            return JsonResponse({'response': str(e)}, status=400)
