from django.urls import path

from . import views

app_name = "player"

urlpatterns = [
    path("xem/<slug:slug>/tap-<int:number>/", views.watch, name="watch"),
    path("xem/<slug:slug>/", views.watch, name="watch"),
]
