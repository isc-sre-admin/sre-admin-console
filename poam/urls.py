from django.urls import path

from poam.views import edit_poam_entry, list_poam_entries

app_name = "poam"

urlpatterns = [
    path("", list_poam_entries, name="list"),
    path("new/", edit_poam_entry, name="create"),
    path("<str:poam_id>/<str:entry_status>/", edit_poam_entry, name="edit"),
]
