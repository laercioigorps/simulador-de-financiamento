from django.test import TestCase
from django.urls import resolve, reverse
from ..views import SimuladorView

class SimulacaoDoFinanciamentoURLTest(TestCase):
    
    def test_url_da_simulacao(self):
        self.assertEqual(reverse('imoveis:simulador') , "/imoveis/simulador/")