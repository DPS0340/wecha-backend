from django.db import models

from film.models import Film

class User(models.Model):
    email          = models.EmailField(max_length=256)
    password       = models.CharField(max_length=512)
    name           = models.CharField(max_length=128)
    description    = models.TextField(null=True)
    face_image_url = models.URLField(max_length=2048, null=True)
    minute_watched = models.IntegerField(default=0)

    class Meta:
        db_table = "users"

class Collection(models.Model):
    name = models.CharField(max_length=512)
    user = models.ForeignKey('User', on_delete=models.CASCADE)
    film = models.ManyToManyField('Film', through="FilmCollection")

    class Meta:
        db_table = "collections"

class FilmCollection(models.Model): 
    film       = models.ForeignKey('Film' on_delete=models.CASCADE)
    collection = models.ForeignKey('Collection', on_delete=models.CASCADE)

    class Meta:
        db_table = "film_collections"
        
class ReviewType(models.Model):
    name = models.CharField(max_length=128)

    class Meta:
        db_table = "review_types"

class Review(models.Model):
    score       = models.DecimalField(
        max_digits     = 2,
        decimal_places = 1,
        null           = True
    )
    comment     = models.TextField(null=True)
    like_count  = models.IntegerField(default=0)
    review_type = models.ForeignKey('ReviewType', on_delete=models.CASCADE)
    film        = models.ForeignKey('Film', on_delete=models.CASCADE)
    user        = models.ManyToManyField('User')

    class Meta:
        db_table = "reviews"

class UserReview(models.Model):
    user   = models.ForeignKey('User', on_delete=models.CASCADE)
    review = models.ForeignKey('Review', on_delete=models.CASCADE)

    class Meta:
        db_table = "user_reviews"