from django.urls import path
from .views import username_reveal

urlpatterns = [
    path("username-reveal/", username_reveal)
]