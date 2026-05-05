from django.urls import path
from . import views

urlpatterns = [
    path("", views.landing_view, name="landing"),
    path("home/", views.home_view, name="home"),
    path("signup/", views.signup_view, name="signup"),
]