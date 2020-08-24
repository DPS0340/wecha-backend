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
        # 서비스 제공자에 따라 평균 별점이 높은 10개의 영화를 리턴한다.
        sp_manager            = ServiceProvider.objects
        service_provider_name = request.GET.get('sp', None)
        if sp_manager.filter(name = service_provider_name).exists():
            service_provider = sp_manager.get(name = service_provider_name)
            films            = Film.objects.filter(service_provider = service_provider) \
                                .only(
                                    'id',
                                    'korean_title', 
                                    'release_date', 
                                    'avg_rating', 
                                    'poster_url'
                                ).order_by('-avg_rating')[:10]
            
            # 영화 10개
            data = {
                "films": []
            }
            for film in films:
                country_names          = [c['name'] for c in film.country.values()]
                service_provider_names = [sp['name'] for sp in film.service_provider.values()]

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
        film_manager = Film.objects
        if film_manager.filter(pk = film_id).exists():
            film = film_manager.get(pk = film_id)

            # 국가, 장르, 서비스 제공자
            country_names          = [c['name'] for c in film.country.values()]
            genre_names            = [g['name'] for g in film.genre.values()]
            service_provider_names = [sp['name'] for sp in film.service_provider.values()]

            # 영화 정보에 필요한 URLs
            film_urls          = []
            film_urls_queryset = FilmURL.objects.filter(film = film)
            for query in film_urls_queryset:
                film_urls.append({
                    "film_url_type": query.film_url_type.name,
                    "film_url"     : query.url
                })
            
            # 캐스팅 정보
            casts         = []
            cast_queryset = Cast.objects.filter(film = film)
            for query in cast_queryset:
                person = query.person
                casts.append({
                    "name"    : person.name,
                    "role"    : query.role,
                    "face_url": person.face_image_url
                })

            # 요청 받은 영화가 포함된 컬렉션 리스트
            collections         = []
            collection_queryset = Collection.objects.filter(film = film)
            for query in collection_queryset:
                film_collection_queryset = FilmCollection.objects.filter(collection = query) \
                                                         .select_related('film')[:4]
                poster_urls = [q.film.poster_url for q in film_collection_queryset]
                collections.append({
                    "id"         : query.id,
                    "name"       : query.name,
                    "user_id"    : query.user.id,
                    "poster_urls": poster_urls
                })

            # 영화에 대한 리뷰
            reviews         = []
            review_queryset = Review.objects.filter(film = film).exclude(score__isnull = True)
            review_count    = len(review_queryset)
            for query in review_queryset:
                if User.objects.filter(id = query.user.id).exists():
                    user = User.objects.get(id = query.user.id)
                    reviews.append({
                        "id"                 : query.id,
                        "comment"            : query.comment,
                        "like_count"         : query.like_count,
                        "score"              : query.score,
                        "user_id"            : user.id,
                        "user_face_image_url": user.face_image_url
                    })

            # 각 평점의 카운트
            score_counts = Review.objects.filter(film = film)\
                        .values('score').annotate(total=Count('score'))\
                        .order_by('total')

            # 리스폰스 바디
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