from django.urls import path

from landing.views import home

app_name = "landing"

urlpatterns = [
    path("", home, name="home"),
]
