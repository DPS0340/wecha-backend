def make_service_provider_json(service_provider):
    return {
        "id"  : service_provider.id,
        "name": service_provider.name
    }

def make_service_providers_json(service_providers):
    return [ 
        make_service_provider_json(service_provider)
        for service_provider in service_providers
    ]

def make_country_json(country):
    return {
        "id"  : country.id,
        "name": country.name
    }

def make_countries_json(countries):
    return [ make_country_json(country) for country in countries ]

def make_genre_json(genre):
    return {
        "id"  : genre.id,
        "name": genre.name
    }

def make_genres_json(genres):
    return [ make_genre_json(genre) for genre in genres ]

def make_film_for_list_json(film):
    return {
        "id"               : film.id,
        "title"            : film.korean_title,
        "year"             : film.release_date.year,
        "avg_rating"       : film.avg_rating,
        "poster_url"       : film.poster_url,
        "countries"        : make_countries_json(film.country.all()),
        "service_providers": make_service_providers_json(film.service_provider.all())
    }

def make_films_for_list_json(films):
    return [ make_film_for_list_json(film) for film in films ]

def make_film_for_detail_json(film):
    return {
        "id"                 : film.id,
        "korean_title"       : film.korean_title,
        "original_title"     : film.original_title,
        "year"               : film.release_date.year,
        "running_time_hour"  : film.running_time.hour,
        "running_time_minute": film.running_time.minute,
        "description"        : film.description,
        "poster_url"         : film.poster_url,
        "avg_rating"         : film.avg_rating,
        "countries"          : make_countries_json(film.country.all()),
        "genres"             : make_genres_json(film.genre.all()),
        "service_providers"  : make_service_providers_json(film.service_provider.all())
    }

def make_film_url_json(film_url):
    return {
        "id"           : film_url.id,
        "film_url_type": film_url.film_url_type.name,
        "film_url"     : film_url.url
    }

def make_film_urls_json(film_urls):
    return [ make_film_url_json(film_url) for film_url in film_urls ]

def make_cast_json(cast):
    return {
        "id"      : cast.id,
        "name"    : cast.person.name,
        "role"    : cast.role,
        "face_url": cast.person.face_image_url
    }

def make_casts_json(casts):
    return [ make_cast_json(cast) for cast in casts ]

def make_user_json(user):
    return {
        "id"            : user.id,
        "name"          : user.name,
        "face_image_url": user.face_image_url
    }

def make_collection_for_list_json(collection):
    poster_urls_required = 4
    return  {
        "id"         : collection.id,
        "name"       : collection.name,
        "user"       : make_user_json(collection.user),
        "poster_urls": [ film.poster_url for film in collection.film.all()[:poster_urls_required] ]
    }

def make_collections_for_list_json(collections):
    return [ make_collection_for_list_json(collection) for collection in collections ]

def make_review_json(review):
    return {
        "id"         : review.id,
        "review_type": review.review_type.name,
        "comment"    : review.comment,
        "like_count" : review.like_count,
        "score"      : review.score,
        "user"       : make_user_json(review.user)
    }

def make_reviews_json(reviews):
    return [ make_review_json(review) for review in reviews ]

def make_score_counts_json(score_counts):
    return [ score_count for score_count in score_counts ]

def make_film_search_result_json(film):
    return {
        "id": film.id,
        "korean_title": film.korean_title,
    }

def make_film_search_results_json(films):
    return [ make_film_search_result_json(film) for film in films ]