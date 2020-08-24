from django.urls import path
from .views import SignUp, SignIn

app_name='user'

urlpatterns = [
    path('/signup', SignUp.as_view()),
    path('/signin', SignIn.as_view()),
]