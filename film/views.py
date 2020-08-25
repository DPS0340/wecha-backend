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
from user.utils import token_authorization

class FilmRankingView(View):
    # 서비스 제공자에 따라 평균 별점이 높은 n개의 영화를 리턴한다.
    def get(self, request):
        service_provider_name = request.GET.get('sp', None)
        limit                 = request.GET.get('limit', 10)
        
        if ServiceProvider.objects.filter(name = service_provider_name).exists():
            service_provider = ServiceProvider.objects.get(name = service_provider_name)
            films = service_provider.film_set.order_by('-avg_rating')[:limit]
            
            body = [
                {
                    "id"               : f.id,
                    "title"            : f.korean_title,
                    "year"             : f.release_date.year,
                    "avg_rating"       : f.avg_rating,
                    "poster_url"       : f.poster_url,
                    "countries"        : [ c['name'] for c in f.country.values()],
                    "service_providers": [ s['name'] for s in f.service_provider.values()]
                }
                for f in films
            ]
            return JsonResponse({"films": body}, status = 200)

        return JsonResponse(
            {"message": "INVALID_QUERY_PARAMETER_SERVICE_PROVIDER"},
            status = 400
        )

class FilmDetailView(View):
    @token_authorization
    def get(self, request, film_id):        
        if Film.objects.filter(pk = film_id).exists():
            film = Film.objects.get(pk = film_id)

            body = {
                "id"                 : film.id,
                "korean_title"       : film.korean_title,
                "original_title"     : film.original_title,
                "year"               : film.release_date.year,
                "running_time_hour"  : film.running_time.hour,
                "running_time_minute": film.running_time.minute,
                "description"        : film.description,
                "poster_url"         : film.poster_url,
                "avg_rating"         : film.avg_rating,
                "countries"          : [c['name'] for c in film.country.values()],
                "genres"             : [g['name'] for g in film.genre.values()],
                "service_providers"  : [sp['name'] for sp in film.service_provider.values()],
                "film_urls"          : [
                    {
                        "id"           : fu.id,
                        "film_url_type": fu.film_url_type.name,
                        "film_url"     : fu.url
                    }  
                    for fu in film.filmurl_set.all().select_related('film_url_type')
                ],
                "casts" : [
                    {
                        "id"      : c.id,
                        "name"    : c.person.name,
                        "role"    : c.role,
                        "face_url": c.person.face_image_url
                    }  
                    for c in film.cast_set.all().select_related('person')
                ],
                "collections" : [
                    {
                        "id"         : c.id,
                        "name"       : c.name,
                        "user_id"    : c.user.id,
                        "poster_urls": [ f.poster_url for f in c.film.all()[:4] ]
                    }  
                    for c in film.collection_set.all().prefetch_related('film', 'user')
                ],
                "reviews" : [
                    {
                        "id"                 : r.id,
                        "comment"            : r.comment,
                        "like_count"         : r.like_count,
                        "score"              : r.score,
                        "user_id"            : r.user.id,
                        "user_face_image_url": r.user.face_image_url
                    }
                    for r in film.review_set.all().select_related('user').exclude(score__isnull=True)
                ],
                "score_counts"         : [
                    score
                    for score in film.review_set.values('score').annotate(total=Count('score')).order_by('total')
                ],
            }
            
            # 로그인된 유저가 요청한 영화에 대한 리뷰가 있으면 body 추가해준다.
            if request.user:
                review = film.review_set.filter(film=film, user=request.user).exclude(score__isnull=True).select_related('user')
                if review.exists():
                    review = review.first()
                    body["authenticated_user_review"] =  {
                        "id"                 : review.id,
                        "comment"            : review.comment,
                        "id"                 : review.pk,
                        "comment"            : review.comment,
                        "user_id"            : review.user.id,
                        "user_face_image_url": review.user.face_image_url
                    }

            return JsonResponse(body, status = 200)

        return JsonResponse(
            {"message": "INVALID_PATH_VARIABLE_FILM_ID"},
            status = 400
        )

class FilmRecommendationView(View):
    def get_count_dict(self, user, way, manager):
        counter_dict    = {}
        review_queryset = Review.objects.filter(user = user).select_related('film')[:10]
        for rq in review_queryset:
            film_way_queryset = manager.filter(film=rq.film).select_related(way)
            for fwq in film_way_queryset:
                if way == "genre":
                    key = fwq.genre.name
                elif way == "country":
                    key = fwq.country.name
                elif way == 'person':
                    key = fwq.person.id

                if key in counter_dict:
                    counter_dict[key] += 1
                else:
                    counter_dict[key] = 1
        return counter_dict

    def get(self, request):
        way = request.GET.get('way', None)

        # 장르로 추천
        if way == "genre":
            # TODO: 로그인 되어있는지 확인 처리
            if User.objects.filter(pk = 101).exists():
                user               = User.objects.get(pk = 101)
                genre_count_dict   = self.get_count_dict(user, way, FilmGenre.objects)
                most_genre_name, _ = Counter(genre_count_dict).most_common(1)[0]
                most_genre         = Genre.objects.get(name = most_genre_name)
                film_queryset      = Film.objects.filter(genre = most_genre)[:12]
                
                data = {
                    "films": []
                }
                for query in film_queryset:
                    country_names          = [c['name'] for c in query.country.values()]
                    service_provider_names = [sp['name'] for sp in query.service_provider.values()]

                    body = {
                        "id"               : query.id,
                        "title"            : query.korean_title,
                        "countries"        : country_names,
                        "year"             : query.release_date.year,
                        "avg_rating"       : query.avg_rating,
                        "poster_url"       : query.poster_url,
                        "service_providers": service_provider_names
                    }
                    data["films"].append(body)
                    data["genre"] = {
                        "id": most_genre.pk,
                        "name": most_genre_name
                    }
                return JsonResponse(data, status = 200)

        # 국가로 추천
        if way == "country":
            # TODO: 로그인 되어있는지 확인 처리
            if User.objects.filter(pk = 101).exists():
                user                 = User.objects.get(pk = 101)
                country_count_dict   = self.get_count_dict(user, way, FilmCountry.objects)
                most_country_name, _ = Counter(country_count_dict).most_common(1)[0]
                most_country         = Country.objects.get(name=most_country_name)
                film_queryset        = Film.objects.filter(country=most_country)[:12]
                
                data = {
                    "films": []
                }
                for query in film_queryset:
                    country_names          = [c['name'] for c in query.country.values()]
                    service_provider_names = [sp['name'] for sp in query.service_provider.values()]

                    body = {
                        "id"               : query.id,
                        "title"            : query.korean_title,
                        "countries"        : country_names,
                        "year"             : query.release_date.year,
                        "avg_rating"       : query.avg_rating,
                        "poster_url"       : query.poster_url,
                        "service_providers": service_provider_names
                    }
                    data["films"].append(body)
                    data["country"] = {
                        "id": most_country.pk,
                        "name": most_country.name
                    }
                return JsonResponse(data, status = 200)
                
        # 인물로 추천
        if way == "person":
            # TODO: 로그인 되어있는지 확인 처리
            if User.objects.filter(pk = 101).exists():
                user              = User.objects.get(pk = 101)
                person_count_dict = self.get_count_dict(user, way, Cast.objects)
                most_person_id, _ = Counter(person_count_dict).most_common(1)[0]
                most_person       = Person.objects.get(id = most_person_id)
                film_queryset     = Film.objects.filter(person = most_person)[:12]
                
                data = {
                    "films": []
                }
                for query in film_queryset:
                    country_names          = [c['name'] for c in query.country.values()]
                    service_provider_names = [sp['name'] for sp in query.service_provider.values()]

                    body = {
                        "id"               : query.id,
                        "title"            : query.korean_title,
                        "countries"        : country_names,
                        "year"             : query.release_date.year,
                        "avg_rating"       : query.avg_rating,
                        "poster_url"       : query.poster_url,
                        "service_providers": service_provider_names
                    }
                    data["films"].append(body)
                    data["person"] = {
                        "id"  : most_person_id,
                        "name": most_person.name
                    }
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

        # 랜덤 컬렉션 
        collection_queryset = Collection.objects.all().order_by('?')[:12]
        for query in collection_queryset:
            film_collection_queryset = FilmCollection.objects.filter(collection=query).select_related('film')[:4]
            poster_urls = [fcq.film.poster_url for fcq in film_collection_queryset]
            body = {
                "id": query.pk,
                "name": query.name,
                "poster_urls": poster_urls,
            }
            data["collections"].append(body)
        return JsonResponse(data, status = 200)

class FilmSearchView(View):
    def get(self, request):
        search_term = request.GET.get('term', None)
        if search_term:
            data = {
                "search_results": []
            }
            # 검색어를 포함하는 영화 정보
            film_queryset = Film.objects.filter(korean_title__icontains=search_term)[:9]
            for query in film_queryset:
                body = {
                    "id": query.pk,
                    "korean_title": query.korean_title
                }
                data["search_results"].append(body)
            return JsonResponse(data, status = 200)

        return JsonResponse(
            {"message": "INVALID_QUERY_PARAMETER_TERM"},
            status = 400
        ) 