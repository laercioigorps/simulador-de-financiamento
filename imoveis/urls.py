from django.contrib import admin
from django.urls import path
from .views import SimuladorView

app_name = "imoveis"

urlpatterns = [
    path('simulador/', SimuladorView.as_view(), name="simulador"),
]
