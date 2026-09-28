from django.urls import path

from . import views

app_name = "billing"

urlpatterns = [
    path("vip/", views.PlanListView.as_view(), name="plans"),
]
