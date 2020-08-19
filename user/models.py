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
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    film = models.ManyToManyField(Film)

    class Meta:
        db_table = "collections"
        
class ReviewType(models.Model):
    TYPE_CHOICES = (
        ('R', 'Rated'),
        ('W', 'Wish'),
        ('O', 'Ongoing'),
    )
    name = models.CharField(max_length=128, choices=TYPE_CHOICES)

    class Meta:
        db_table = "review_types"

class Review(models.Model):
    score       = models.DecimalField(max_digits=2, decimal_places=1, null=True)
    comment     = models.TextField(null=True)
    like_count  = models.IntegerField(default=0)
    review_type = models.ForeignKey(ReviewType, on_delete=models.CASCADE)
    film        = models.ForeignKey(Film, on_delete=models.CASCADE)
    user        = models.ManyToManyField(User)

    class Meta:
        db_table = "reviews"