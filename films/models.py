from django.db import models

class Country(models.Model):
    name = models.CharField(max_length=64)

    class Meta:
        db_table = "countries"

class Genre(models.Model):
    name = models.CharField(max_length=64)

    class Meta:
        db_table = "genres"

class ServiceProvider(models.Model):
    name = models.CharField(max_length=64)

    class Meta:
        db_table = "service_providers"

class Film(models.Model):
    name_kr          = models.CharField(max_length=512)
    name_en          = models.CharField(max_length=256, null=True)
    release_date     = models.DateField()
    running_time     = models.IntegerField()
    description      = models.TextField()
    poster_url       = models.URLField(max_length=2048, null=True)
    avg_rating       = models.DecimalField(max_digits=2, decimal_places=1)
    country          = models.ManyToManyField(Country)
    genre            = models.ManyToManyField(Genre)
    service_provider = models.ManyToManyField(ServiceProvider)

    class Meta:
        db_table = "films"

class FilmURLType(models.Model):
    TYPE_CHOICES = (
        ('V', 'Video'),
        ('I', 'Image'),
        ('B', 'Background'),
    )
    name = models.CharField(max_length=32, choices=TYPE_CHOICES)

    class Meta:
        db_table = "film_url_types"

class FilmURL(models.Model): 
    url           = models.URLField(max_length=2048)
    film_url_type = models.ForeignKey(FilmURLType, on_delete=models.CASCADE)
    film          = models.ForeignKey(Film, on_delete=models.CASCADE)
    
    class Meta:
        db_table = "film_urls"

class Person(models.Model):
    name         = models.CharField(max_length=256)
    face_img_url = models.URLField(max_length=2048, null=True)

    class Meta:
        db_table = "people"

class Cast(models.Model):
    role   = models.CharField(max_length=128)
    film   = models.ForeignKey(Film, on_delete=models.CASCADE)
    person = models.ForeignKey(Person, on_delete=models.CASCADE)

    class Meta:
        db_table = "casts"