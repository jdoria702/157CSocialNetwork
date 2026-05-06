from django.urls import path
from . import views

urlpatterns = [
    path("", views.landing_view, name="landing"),
    path("home/", views.home_view, name="home"),
    path("signup/", views.signup_view, name="signup"),
    path("profile/", views.profile_view, name="profile"),
    path("profile/edit/", views.edit_profile_view, name="edit_profile"),
    path("discover/", views.discover_users_view, name="discover_users"),
    path("follow/<int:user_id>/", views.follow_user_view, name="follow_user"),
    path("following/", views.following_view, name="following"),
    path("followers/", views.followers_view, name="followers"),
    path("mutual_followers/<int:other_user_id>/", views.mutual_followers_view, name="mutual_followers"),
    path("unfollow/<int:user_id>/", views.unfollow_user_view, name="unfollow_user"),
    path("friend_recommendations/", views.friend_recommendations_view, name="friend_recommendations"),

]