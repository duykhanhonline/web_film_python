from django.urls import path

from . import views

app_name = "accounts"

urlpatterns = [
    path("dang-nhap/", views.LoginView.as_view(), name="login"),
]
