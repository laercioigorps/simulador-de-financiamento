from django.contrib import admin
from django.urls import path
from .views import SimuladorView, ResultadoSimulacaoView

app_name = "imoveis"

urlpatterns = [
    path('simulador/', SimuladorView.as_view(), name="simulador"),
    path('simulador/resultado/', ResultadoSimulacaoView.as_view(), name="resultado-simulacao"),
]
