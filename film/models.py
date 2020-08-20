from django.db import models

class Country(models.Model):
    name = models.CharField(max_length=64)

    class Meta:
        db_table = "countries"

class FilmCountry(models.Model):
    film    = models.ForeignKey('Film', on_delete=models.CASCADE)
    country = models.ForeignKey('Country', on_delete=models.CASCADE)

    class Meta:
        db_table = "film_countries"

class Genre(models.Model):
    name = models.CharField(max_length=64)

    class Meta:
        db_table = "genres"

class FilmGenre(models.Model):
    film  = models.ForeignKey('Film', on_delete=models.CASCADE)
    genre = models.ForeignKey('Genre', on_delete=models.CASCADE)

    class Meta:
        db_table = "film_genres"

class ServiceProvider(models.Model):
    name = models.CharField(max_length=64)

    class Meta:
        db_table = "service_providers"

class FilmServiceProvider(models.Model):
    film             = models.ForeignKey('Film', on_delete=models.CASCADE)
    service_provider = models.ForeignKey(
        'ServiceProvider', 
        on_delete=models.CASCADE
    )

    class Meta:
        db_table = "film_service_providers"

class Film(models.Model):
    korean_title     = models.CharField(max_length=512)
    original_title   = models.CharField(max_length=256, null=True)
    release_date     = models.DateField()
    running_time     = models.TimeField()
    description      = models.TextField()
    poster_url       = models.URLField(max_length=2048, null=True)
    avg_rating       = models.DecimalField(max_digits=2, decimal_places=1)
    country          = models.ManyToManyField(
        'Country', 
        through='FilmCountry'
    )
    genre            = models.ManyToManyField('Genre', through='FilmGenre')
    service_provider = models.ManyToManyField(
        'ServiceProvider', 
        through='FilmServiceProvider'
    )
    person           = models.ManyToManyField('Person', through='Cast')

    class Meta:
        db_table = "films"

class FilmURLType(models.Model):
    name = models.CharField(max_length=32)

    class Meta:
        db_table = "film_url_types"

class FilmURL(models.Model): 
    url           = models.URLField(max_length=2048, null=True)
    film_url_type = models.ForeignKey('FilmURLType', on_delete=models.CASCADE)
    film          = models.ForeignKey('Film', on_delete=models.CASCADE)
    
    class Meta:
        db_table = "film_urls"

class Person(models.Model):
    name           = models.CharField(max_length=256)
    face_image_url = models.URLField(max_length=2048, null=True)

    class Meta:
        db_table = "people"

class Cast(models.Model):
    role   = models.CharField(max_length=128)
    film   = models.ForeignKey('Film', on_delete=models.CASCADE)
    person = models.ForeignKey('Person', on_delete=models.CASCADE)

    class Meta:
        db_table = "casts"