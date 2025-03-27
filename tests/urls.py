## tests/urls.py

from django.urls import path, include

urlpatterns = [
    path("api/", include("django_emqx.urls")),
]
