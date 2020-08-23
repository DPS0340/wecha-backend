from collections import Counter

from django.views     import View
from django.http      import JsonResponse
from django.db.models import Count

from .models import (
    Film,
    Country,
    ServiceProvider,
    FilmURL,
    Person,
    Cast,
    Genre,
    FilmGenre,
    FilmCountry,
)
from user.models import (
    Collection,
    Review,
    User,
    FilmCollection,
)

class FilmRankingView(View):
    def get(self, request):
        service_provider_name = request.GET.get('sp', None)
        if ServiceProvider.objects                              \
                          .filter(name = service_provider_name) \
                          .exists():
            service_provider = ServiceProvider.objects \
                                              .get(name = service_provider_name)
            films = Film.objects                                     \
                        .filter(service_provider = service_provider) \
                        .only(
                            'id',
                            'korean_title', 
                            'release_date', 
                            'avg_rating', 
                            'poster_url'
                        )                                             \
                        .order_by('-avg_rating')[:10]

            
            data = {
                "films": []
            }
            for film in films:
                country_names = [
                    country['name'] for country in film.country.values()
                ]
                service_provider_names = [
                    service_provider['name'] for service_provider in film.service_provider.values()
                ]

                body = {
                    "id"               : film.id,
                    "title"            : film.korean_title,
                    "countries"        : country_names,
                    "year"             : film.release_date.year,
                    "avg_rating"       : film.avg_rating,
                    "poster_url"       : film.poster_url,
                    "service_providers": service_provider_names
                }
                data["films"].append(body)
            return JsonResponse(data, status = 200)
        
        return JsonResponse(
            {"message": "INVALID_QUERY_PARAMETER_SERVICE_PROVIDER"},
            status = 400
        )

class FilmDetailView(View):
    def get(self, request, film_id):
        if Film.objects.filter(pk = film_id).exists():

            film = Film.objects.get(pk = film_id)
            country_names = [
                country['name'] for country in film.country.values()
            ]
            genre_names = [
               genre['name'] for genre in film.genre.values() 
            ]
            service_provider_names = [
                service_provider['name'] for service_provider in film.service_provider.values()
            ]

            film_urls = []
            film_urls_queryset = FilmURL.objects.filter(film=film)
            for film_url_query in film_urls_queryset:
                film_urls.append({
                    "film_url_type": film_url_query.film_url_type.name,
                    "film_url"     : film_url_query.url
                })
            
            casts = []
            cast_queryset = Cast.objects.filter(film=film)
            for cast_query in cast_queryset:
                person = cast_query.person
                casts.append({
                    "name"    : person.name,
                    "role"    : cast_query.role,
                    "face_url": person.face_image_url
                })

            collections = []
            collection_queryset = Collection.objects.filter(film=film)
            for collection_query in collection_queryset:
                film_collection_queryset = FilmCollection.objects.filter(collection=collection_query).select_related('film')[:4]
                poster_urls = [film_collection_query.film.poster_url for film_collection_query in film_collection_queryset]
                collections.append({
                    "id"     : collection_query.id,
                    "name"   : collection_query.name,
                    "user_id": collection_query.user.id,
                    "poster_urls": poster_urls
                })

            reviews = []
            review_queryset = Review.objects.filter(film=film).exclude(score__isnull=True)
            review_count = len(review_queryset)

            for review_query in review_queryset:
                if User.objects.filter(id = review_query.user.id).exists():
                    user = User.objects.get(id = review_query.user.id)
                    reviews.append({
                        "id" : review_query.id,
                        "comment": review_query.comment,
                        "like_count": review_query.like_count,
                        "score": review_query.score,
                        "user_id": user.id,
                        "user_face_image_url": user.face_image_url
                    })

            score_counts = Review.objects.filter(film=film).values('score').annotate(total=Count('score')).order_by('total')

            body = {
                "id"                 : film.id,
                "korean_title"       : film.korean_title,
                "original_title"     : film.original_title,
                "year"               : film.release_date.year,
                "running_time_hour"  : film.running_time.hour,
                "running_time_minute": film.running_time.minute,
                "description"        : film.description,
                "poster_url"         : None,
                "avg_rating"         : film.avg_rating,
                "countries"          : country_names,
                "genres"             : genre_names,
                "service_providers"  : service_provider_names,
                "film_urls"          : film_urls,
                "casts"              : casts,
                "collections"        : collections,
                "reviews"            : reviews,
                "review_count"       : review_count,
                "score_counts"       : list(score_counts),
            }
            
            return JsonResponse(body, status=200)

        return JsonResponse(
            {"message": "INVALID_PATH_VARIABLE_FILM_ID"},
            status = 400
        )

class FilmRecommendationView(View):
    def get(self, request):
        way_to_recommend = request.GET.get('way', None)
        if way_to_recommend == "genre":

            # TODO: 로그인 되어있는지 확인 처리
            if User.objects.filter(pk = 101).exists():
                genre_count_dict = {}
                user = User.objects.get(pk = 101)
                review_queryset = Review.objects.filter(user = user).select_related('film')[:10]
                for review_query in review_queryset:
                    film_genre_queryset = FilmGenre.objects.filter(film=review_query.film).select_related('genre')
                    for film_genre_query in film_genre_queryset:
                        genre_name = film_genre_query.genre.name
                        if genre_name in genre_count_dict:
                            genre_count_dict[genre_name] += 1
                        else:
                            genre_count_dict[genre_name] = 1
                
                most_genre_name, _ = Counter(genre_count_dict).most_common(1)[0]
                most_genre = Genre.objects.get(name=most_genre_name)
                film_queryset = Film.objects.filter(genre=most_genre)[:12]
                
                data = {
                    "films": []
                }
                for film_query in film_queryset:
                    country_names = [
                        country['name'] for country in film_query.country.values()
                    ]
                    service_provider_names = [
                        service_provider['name'] for service_provider in film_query.service_provider.values()
                    ]

                    body = {
                        "id"               : film_query.id,
                        "title"            : film_query.korean_title,
                        "countries"        : country_names,
                        "year"             : film_query.release_date.year,
                        "avg_rating"       : film_query.avg_rating,
                        "poster_url"       : film_query.poster_url,
                        "service_providers": service_provider_names
                    }
                    data["films"].append(body)
                return JsonResponse(data, status = 200)
        if way_to_recommend == "country":
            if User.objects.filter(pk = 101).exists():
                country_count_dict = {}
                user = User.objects.get(pk = 101)
                review_queryset = Review.objects.filter(user = user).select_related('film')[:10]
                for review_query in review_queryset:
                    film_country_queryset = FilmCountry.objects.filter(film=review_query.film).select_related('country')
                    for film_country_query in film_country_queryset:
                        country_name = film_country_query.country.name
                        if country_name in country_count_dict:
                            country_count_dict[country_name] += 1
                        else:
                            country_count_dict[country_name] = 1
                
                most_country_name, _ = Counter(country_count_dict).most_common(1)[0]
                most_country = Country.objects.get(name=most_country_name)
                film_queryset = Film.objects.filter(country=most_country)[:12]
                
                data = {
                    "films": []
                }
                for film_query in film_queryset:
                    country_names = [
                        country['name'] for country in film_query.country.values()
                    ]
                    service_provider_names = [
                        service_provider['name'] for service_provider in film_query.service_provider.values()
                    ]

                    body = {
                        "id"               : film_query.id,
                        "title"            : film_query.korean_title,
                        "countries"        : country_names,
                        "year"             : film_query.release_date.year,
                        "avg_rating"       : film_query.avg_rating,
                        "poster_url"       : film_query.poster_url,
                        "service_providers": service_provider_names
                    }
                    data["films"].append(body)
                return JsonResponse(data, status = 200)
        if way_to_recommend == "person":
            if User.objects.filter(pk = 101).exists():
                person_count_dict = {}
                user = User.objects.get(pk = 101)
                review_queryset = Review.objects.filter(user = user).select_related('film')[:10]
                for review_query in review_queryset:
                    cast_queryset = Cast.objects.filter(film=review_query.film).select_related('person')
                    for cast_query in cast_queryset:
                        person_id = cast_query.person.id
                        if person_id in person_count_dict:
                            person_count_dict[person_id] += 1
                        else:
                            person_count_dict[person_id] = 1
                
                most_person_id, _ = Counter(person_count_dict).most_common(1)[0]
                most_person = Person.objects.get(id=most_person_id)
                print(most_person.name)
                film_queryset = Film.objects.filter(person=most_person)[:12]
                
                data = {
                    "films": []
                }
                for film_query in film_queryset:
                    country_names = [
                        country['name'] for country in film_query.country.values()
                    ]
                    service_provider_names = [
                        service_provider['name'] for service_provider in film_query.service_provider.values()
                    ]

                    body = {
                        "id"               : film_query.id,
                        "title"            : film_query.korean_title,
                        "countries"        : country_names,
                        "year"             : film_query.release_date.year,
                        "avg_rating"       : film_query.avg_rating,
                        "poster_url"       : film_query.poster_url,
                        "service_providers": service_provider_names
                    }
                    data["films"].append(body)
                return JsonResponse(data, status = 200)

        return JsonResponse(
            {"message": "INVALID_QUERY_PARAMETER_WAY"},
            status = 400
        )

class FilmCollectionListView(View):
    def get(self, request):
        data = {
            "collections": []
        }

        collection_queryset = Collection.objects.all().order_by('?')[:12]
        for collection_query in collection_queryset:
            film_collection_queryset = FilmCollection.objects.filter(collection=collection_query).select_related('film')[:4]
            poster_urls = [film_collection_query.film.poster_url for film_collection_query in film_collection_queryset]
            body = {
                "id": collection_query.pk,
                "name": collection_query.name,
                "poster_urls": poster_urls,
            }
            data["collections"].append(body)

        return JsonResponse(data, status = 200)