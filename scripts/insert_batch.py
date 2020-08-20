import csv
import pprint
from decimal import Decimal

import pandas as pd
from ast import literal_eval

from film.models import (
    Country,
    FilmCountry,
    Genre,
    FilmGenre,
    ServiceProvider,
    FilmServiceProvider,
    Film,
    FilmURLType, 
    FilmURL,
    Person,
    Cast
)

FILENAME = "wecha_films.csv"

def run():
    # csv 파일 열기
    df = pd.read_csv(
        FILENAME, 
        converters={
            "countries"        : literal_eval,
            "genres"           : literal_eval,
            "service_providers": literal_eval,
            "casts"            : literal_eval,
            "image_urls"       : literal_eval,
            "video_urls"       : literal_eval
        },
    )

    for _, row in df.iterrows():
        # 컬럼 데이터 가져오기
        korean_title           = row['korean_title']
        original_title         = row['original_title']
        release_date           = row['date']
        running_time           = row['running_time']
        description            = row['description']
        poster_url             = row['poster_url']
        # avg_rating             = row['avg_rating']
        country_names          = row['countries']
        genre_names            = row['genres']
        service_provider_names = row['service_providers']
        casts                  = row['casts']
        background             = row['background']
        image_urls             = row['image_urls']
        video_urls             = row['video_urls']

        # 국가 (다대다)
        for name in country_names:
            Country.objects.get_or_create(name=name)
        
        # 장르 (다대다)
        for name in genre_names:
            Genre.objects.get_or_create(name=name)

        # 서비스 제공자 (다대다)
        for name in service_provider_names:
            ServiceProvider.objects.get_or_create(name=name)
            
        # 인물
        for cast in casts:
            name = cast[0]

            # 얼굴 이미지 url이 빈 문자열이면 None으로 변경
            face_image_url = cast[2]
            if not face_image_url:
                face_image_url = None

            Person.objects.get_or_create(
                name           = name,
                face_image_url = face_image_url
            )

        # 영화
        film, created = Film.objects.get_or_create(
            korean_title     = korean_title,
            original_title   = original_title,
            release_date     = release_date,
            running_time     = running_time,
            description      = description,
            poster_url       = ,
        )
