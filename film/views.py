from django.views import View
from django.http  import JsonResponse

from .models import (
    Film,
    Country,
    ServiceProvider,
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
                    "id": film.id,
                    "title": film.korean_title,
                    "countries": country_names,
                    "year": film.release_date.year,
                    "avg_rating": film.avg_rating,
                    "poster_url": film.poster_url,
                    "service_providers": service_provider_names
                }
                data["films"].append(body)
            return JsonResponse(data, status = 200)
        
        return JsonResponse(
            {"message": "INVALID_QUERY_PARAMETER_SERVICE_PROVIDER"},
            status = 400
        )