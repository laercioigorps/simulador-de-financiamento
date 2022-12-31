from django.test import TestCase, RequestFactory, Client
from ..views import SimuladorView
from django.urls import reverse
from ..forms import SimulacaoFormulario

class SimuladorDeImoveisViewTest(TestCase):

    def setUp(self) -> None:
        self.rf = RequestFactory()
        self.client = Client()
        self.simuladorView = SimuladorView.as_view()

    def test_get_pagina_do_simulador(self):
        response = self.client.get(reverse("imoveis:simulador"))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "imoveis/pagina_simulador.html")
        self.assertTrue("form" in response.context)
        self.assertTrue(isinstance(response.context["form"], SimulacaoFormulario))
