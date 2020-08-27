from collections import Counter

from django.views     import View
from django.http      import JsonResponse
from django.db.models import Count

from .models     import (
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
from user.utils  import token_authorization
from .make_jsons import (
    make_service_provider_json,
    make_service_providers_json,
    make_country_json,
    make_countries_json,
    make_genre_json,
    make_genres_json,
    make_film_for_list_json,
    make_films_for_list_json,
    make_film_for_detail_json,
    make_film_url_json,
    make_film_urls_json,
    make_cast_json,
    make_casts_json,
    make_user_json,
    make_collection_for_list_json,
    make_collections_for_list_json,
    make_review_json,
    make_reviews_json,
    make_score_counts_json,
    make_film_search_result_json,
    make_film_search_results_json
)

class FilmRankingView(View):
    def get(self, request):
        service_provider_name = request.GET.get('sp', None)
        limit                 = int(request.GET.get('limit', 10))
        
        if ServiceProvider.objects.filter(name = service_provider_name).exists():
            service_provider = ServiceProvider.objects.get(name = service_provider_name)
            films            = service_provider.film_set.order_by('-avg_rating')[:limit]
            
            body = { "films": make_films_for_list_json(films) }
            return JsonResponse(body, status = 200)

        return JsonResponse(
            {"message": "INVALID_QUERY_PARAMETER_SERVICE_PROVIDER"},
            status = 404
        )

class FilmDetailView(View):
    @token_authorization
    def get(self, request, film_id):        
        if Film.objects.filter(pk = film_id).exists():
            film = Film.objects.get(pk = film_id)

            body = {
                "film"        : make_film_for_detail_json(film),
                "urls"        : make_film_urls_json(film.filmurl_set.all().select_related('film_url_type')),
                "casts"       : make_casts_json(film.cast_set.all().select_related('person')),
                "collections" : make_collections_for_list_json(film.collection_set.all().prefetch_related('film', 'user')),
                "reviews"     : make_reviews_json(film.review_set.all().select_related('user').exclude(score__isnull=True)),
                "score_counts": make_score_counts_json(film.review_set.values('score').annotate(total=Count('score')).order_by('total')),
            }
            
            if request.user:
                review = film.review_set.filter(film=film, user=request.user).exclude(score__isnull=True).select_related('user', 'review_type')
                if review.exists():
                    review = review.first()
                    body["authenticated_user_review"] = make_review_json(review)

            return JsonResponse(body, status = 200)

        return JsonResponse(
            {"message": "INVALID_PATH_VARIABLE_FILM_ID"},
            status = 404
        )

class FilmRecommendationView(View):
    def get_queryset_by_way(self, way, review):
        way_to_queryset = {
            "genre"  : review.film.genre.all(),
            "country": review.film.country.all(),
            "person" : review.film.person.all()
        }
        return way_to_queryset[way]

    def get_model_by_way(self, way):
        way_to_model = {
            "genre"  : Genre,
            "country": Country,
            "person" : Person,
        }
        return way_to_model[way]

    def get_random_name(self, way):
        return self.get_model_by_way(way).objects.all()\
                .order_by('?').only('name').first().name

    def get_recommendation_by_way(self, user, way, limit):
        if user:
            reviews = user.review_set.select_related('film')
            if reviews:
                name = Counter([
                    obj.name
                    for review in reviews
                    for obj in self.get_queryset_by_way(way, review)
                ]).most_common(1)[0][0]
            else:
                name = self.get_random_name(way)
        else:
            name = self.get_random_name(way)
        
        films = self.get_model_by_way(way).objects.get(name = name).film_set.all()\
            .prefetch_related('country', 'service_provider')[:limit]

        body = {
            way    : name,
            "films": make_films_for_list_json(films)
        }
        return body

    @token_authorization
    def get(self, request):
        way   = request.GET.get('way', None)
        limit = int(request.GET.get('limit', 18))

        if way != "genre" and way != "country" and way != "person":
            return JsonResponse(
                {"message": "INVALID_QUERY_PARAMETER_WAY"},
                status = 404
            )
        body = self.get_recommendation_by_way(request.user, way, limit)
        return JsonResponse(body, status = 200)

class FilmCollectionListView(View):
    def get(self, request):
        limit       = int(request.GET.get('limit', 18))
        collections = Collection.objects.all().prefetch_related('film').order_by('?')[:limit]

        body = { "collections": make_collections_for_list_json(collections) }
        return JsonResponse(body, status = 200)

class FilmCollectionDetailView(View):
    def get(self, request, collection_id):
        if Collection.objects.filter(id=collection_id).exists():
            collection = Collection.objects.get(id=collection_id)
            
            body = {
                "collection": make_collection_for_list_json(collection),
                "films"     : make_films_for_list_json(collection.film.all())
            }
            return JsonResponse(body, status = 200)

        return JsonResponse(
            {"message": "INVALID_PATH_PARAMETER_COLLECTION_ID"},
             status = 404
        )

class FilmSearchView(View):
    def get(self, request):
        term  = request.GET.get('term', None)
        limit = int(request.GET.get('limit', 9))

        if term:
            body = { "search_results": make_film_search_results_json(Film.objects.filter(korean_title__icontains = term)[:limit]) }
            return JsonResponse(body, status = 200)

        return JsonResponse(
            {"message": "INVALID_QUERY_PARAMETER_TERM"},
            status = 404
        )