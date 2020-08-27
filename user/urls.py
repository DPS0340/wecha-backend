from django.urls import path
from .views import SignUp, SignIn, HandleReview, ReviewCount, ReviewLike

app_name='user'

urlpatterns = [
    path('/signup', SignUp.as_view()),
    path('/signin', SignIn.as_view()),
    path('/review', HandleReview.as_view()),
    path('/review/count', ReviewCount.as_view()),
    path('/review/like', ReviewLike.as_view()),
]