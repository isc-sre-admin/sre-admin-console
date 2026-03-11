from django.urls import path

from poam.views import poam_edit, poam_list

app_name = "poam"

urlpatterns = [
    path("", poam_list, name="list"),
    path("new/", poam_edit, name="new"),
    path("<str:poam_id>/", poam_edit, name="edit"),
]
