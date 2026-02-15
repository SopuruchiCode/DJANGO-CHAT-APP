from django.urls import path
from . import views

urlpatterns = [
    path("", views.home_page),
    path("login/", views.login_page),
    path("signup/", views.signup_page),
    path("logout/", views.logout_page),
    path("get-chat-data/<str:friend_username>/", views.get_chat_data),
    path("profile-search/", views.profile_search_page)
]