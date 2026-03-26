from django.urls import path
from . import views

app_name = "activities"

urlpatterns = [
    path("", views.activity_list, name="list"),
    path("materials/<int:material_id>/open/", views.material_open, name="material_open"),
    path("materials/<int:material_id>/download/", views.material_download, name="material_download"),
    path("<slug:slug>/", views.activity_detail, name="detail"),
]
