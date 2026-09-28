from django.urls import path

from . import views

app_name = "catalog"

urlpatterns = [
    path("", views.HomeView.as_view(), name="home"),
    path("phim-bo/", views.SeriesListView.as_view(), name="series"),
    path("phim-le/", views.MovieListView.as_view(), name="movies"),
    path("phim/<slug:slug>/", views.MovieDetailView.as_view(), name="detail"),
    path("tim-kiem/", views.SearchView.as_view(), name="search"),
    path("danh-sach/<slug:slug>/", views.toggle_my_list, name="my_list_toggle"),
]
