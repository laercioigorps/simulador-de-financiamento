from django.test import TestCase, RequestFactory, Client
from ..views import SimuladorView
from django.urls import reverse
from ..forms import SimulacaoFormulario

class SimuladorDeImoveisViewTest(TestCase):

    def setUp(self) -> None:
        self.rf = RequestFactory()
        self.client = Client()
        self.simuladorView = SimuladorView.as_view()

        self.validSimulationData = {
            "data_nascimento" : "1997-08-09",
            "valor_do_imovel" : 150000,
            "valor_da_entrada" : 30000,
            "prestacoes" : 360,
        }

    def test_get_pagina_do_simulador(self):
        response = self.client.get(reverse("imoveis:simulador"))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "imoveis/pagina_simulador.html")
        self.assertTrue("form" in response.context)
        self.assertTrue(isinstance(response.context["form"], SimulacaoFormulario))

    
    def test_get_resultado_da_simulacao_com_dados_invalidos_retorna_para_formulario(self):
        self.validSimulationData["valor_da_entrada"] = 1000
        response = self.client.get(reverse("imoveis:resultado-simulacao"), self.validSimulationData)
        self.assertEqual(response.status_code, 400)
        self.assertTemplateUsed(response, "imoveis/pagina_simulador.html")
        self.assertTrue("form" in response.context)
        self.assertTrue(isinstance(response.context["form"], SimulacaoFormulario))
        self.assertTrue("dados_iniciais" in response.context)
        dados_iniciais = response.context["dados_iniciais"]
        self.assertEqual(str(dados_iniciais["valor_do_imovel"]), "150000")
        self.assertEqual(dados_iniciais["data_nascimento"].strftime("%Y-%m-%d"), "1997-08-09")
        self.assertFalse(dados_iniciais["incluir_ITBI"])
        self.assertEqual(dados_iniciais["prestacoes"], "360")
        self.assertTrue("valor_da_entrada" not in dados_iniciais)

    def test_resultado_da_simulacao_valida_contem_dados_iniciais(self):
        response = self.client.get(reverse("imoveis:resultado-simulacao"), self.validSimulationData)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "imoveis/resultado_simulacao.html")
        self.assertTrue("dados_iniciais" in response.context)
        dados_iniciais = response.context["dados_iniciais"]
        self.assertEqual(str(dados_iniciais["valor_do_imovel"]), "150000")
        self.assertEqual(str(dados_iniciais["valor_da_entrada"]), "30000")
        self.assertEqual(dados_iniciais["data_nascimento"].strftime("%Y-%m-%d"), "1997-08-09")
        self.assertFalse(dados_iniciais["incluir_ITBI"])
        self.assertEqual(dados_iniciais["prestacoes"], "360")

    def test_resultado_da_simulacao_sem_ITBI(self):
        response = self.client.get(reverse("imoveis:resultado-simulacao"), self.validSimulationData)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "imoveis/resultado_simulacao.html")
        self.assertTrue("dados_iniciais" in response.context)
        dados_iniciais = response.context["dados_iniciais"]
        self.assertEqual(str(dados_iniciais["valor_do_imovel"]), "150000")
        self.assertEqual(str(dados_iniciais["valor_da_entrada"]), "30000")
        self.assertEqual(dados_iniciais["data_nascimento"].strftime("%Y-%m-%d"), "1997-08-09")
        self.assertFalse(dados_iniciais["incluir_ITBI"])
        self.assertEqual(dados_iniciais["prestacoes"], "360")

