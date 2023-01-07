from django.test import TestCase
from ..forms import SimulacaoFormulario
import datetime


class FormDeSimulacaoTest(TestCase):
    def setUp(self) -> None:
        self.validSimulationData = {
            "data_nascimento": "09/08/1997",
            "valor_do_imovel": 150000,
            "valor_da_entrada": 30000,
            "incluir_ITBI": False,
            "prestacoes": 360,
            "amortizacao": "PRICE",
        }
        self.form = SimulacaoFormulario()

    def test_empty_form_validation(self):
        is_valid = self.form.is_valid()
        self.assertFalse(is_valid)

    def test_valid_simulation(self):
        form = SimulacaoFormulario(self.validSimulationData)
        self.assertTrue(form.is_valid())

    # testes do campo de valor do imóvel

    def test_not_valid_price(self):
        data = self.validSimulationData
        data["valor_do_imovel"] = "150mil"
        form = SimulacaoFormulario(self.validSimulationData)
        self.assertFalse(form.is_valid())

    def test_form_price_decimal_field(self):
        data = self.validSimulationData
        data["valor_do_imovel"] = 120.12
        form = SimulacaoFormulario(data)
        self.assertTrue(form.is_valid())
        self.assertEqual(str(form.cleaned_data["valor_do_imovel"]), "120.12")

    def test_form_price_decimal_field(self):
        data = self.validSimulationData
        data["valor_do_imovel"] = 120.12
        form = SimulacaoFormulario(data)
        self.assertTrue(form.is_valid())
        self.assertEqual(str(form.cleaned_data["valor_do_imovel"]), "120.12")

    def test_valor_do_imovel_negativo_deve_falhar(self):
        data = self.validSimulationData
        data["valor_do_imovel"] = -120.12
        form = SimulacaoFormulario(data)
        self.assertFalse(form.is_valid())

    # testes do campo de valor da entrada

    def test_valor_da_entrada_invalido(self):
        data = self.validSimulationData
        data["valor_da_entrada"] = "30mil"
        form = SimulacaoFormulario(data)
        self.assertFalse(form.is_valid())

    def test_valor_da_entrada_menor_que_zero(self):
        data = self.validSimulationData
        data["valor_da_entrada"] = -35000
        form = SimulacaoFormulario(data)
        self.assertFalse(form.is_valid())

    def test_valor_da_entrada_nao_pode_ser_menor_que_20_porcento_do_total(self):
        data = self.validSimulationData
        data["valor_do_imovel"] = 100001
        data["valor_da_entrada"] = 20000
        form = SimulacaoFormulario(data)
        self.assertFalse(form.is_valid())
        self.assertEqual(
            form.errors["valor_da_entrada"][0],
            "Entrada não pode ser menor que 20% do valor do imovel",
        )

    # testes do campo de data de nascimento
    def test_data_de_nascimento_formato_invalido(self):
        data = self.validSimulationData
        data["data_nascimento"] = "120"
        form = SimulacaoFormulario(data)
        self.assertFalse(form.is_valid())

    def test_data_de_nascimento_menor_de_18_anos_erro(self):
        # date de 17 anos atrás
        date = datetime.date.today() - datetime.timedelta(weeks=4 * 12 * 17)
        data = self.validSimulationData
        data["data_nascimento"] = date.strftime("%Y-%m-%d")
        form = SimulacaoFormulario(data)
        self.assertFalse(form.is_valid())
        self.assertEqual(
            form.errors["data_nascimento"][0],
            "É necessario ser maior de idade para realizar financiamento!",
        )

    def test_data_de_nascimento_maior_de_18_anos_valida(self):
        # date de 19 anos atrás
        mesmo_dia_19_anos_atras = date = datetime.date.today() - datetime.timedelta(
            days=365 * 19
        )
        data = self.validSimulationData
        data["data_nascimento"] = mesmo_dia_19_anos_atras.strftime("%Y-%m-%d")
        form = SimulacaoFormulario(data)
        self.assertTrue(form.is_valid())
        self.assertEqual(form.cleaned_data["data_nascimento"], mesmo_dia_19_anos_atras)

    def test_form_sem_data_de_nascimento(self):
        del self.validSimulationData["data_nascimento"]
        form = SimulacaoFormulario(self.validSimulationData)
        self.assertFalse(form.is_valid())

    # testes do campo de prazo de pagamento

    def test_campo_de_prazo_de_pagamento_required(self):
        del self.validSimulationData["prestacoes"]
        form = SimulacaoFormulario(self.validSimulationData)
        self.assertFalse(form.is_valid())

    def test_campo_de_prazo_de_pagamento_com_4_opcoes(self):
        self.validSimulationData["prestacoes"] = 120
        form = SimulacaoFormulario(self.validSimulationData)
        self.assertTrue(form.is_valid())

        self.validSimulationData["prestacoes"] = 180
        form = SimulacaoFormulario(self.validSimulationData)
        self.assertTrue(form.is_valid())

        self.validSimulationData["prestacoes"] = 240
        form = SimulacaoFormulario(self.validSimulationData)
        self.assertTrue(form.is_valid())

        self.validSimulationData["prestacoes"] = 360
        form = SimulacaoFormulario(self.validSimulationData)
        self.assertTrue(form.is_valid())

        self.validSimulationData["prestacoes"] = 121
        form = SimulacaoFormulario(self.validSimulationData)
        self.assertFalse(form.is_valid())

    # teste campo de financiamento ITBI

    def test_campo_de_ITBI_com_2_opcoes(self):
        self.validSimulationData["incluir_ITBI"] = "true"
        form = SimulacaoFormulario(self.validSimulationData)
        self.assertTrue(form.is_valid())

        del self.validSimulationData["incluir_ITBI"]
        form = SimulacaoFormulario(self.validSimulationData)
        self.assertTrue(form.is_valid())
        self.assertFalse(form.cleaned_data["incluir_ITBI"])

    # test campo sistema de amortização

    def test_campo_amortizacao_sem_dados(self):
        del self.validSimulationData["amortizacao"]
        form = SimulacaoFormulario(self.validSimulationData)
        self.assertFalse(form.is_valid())

    def test_campo_amortizacao_com_valor_invalido(self):
        # opções validas: "PRICE" e "SAC"
        self.validSimulationData["amortizacao"] = "CAS"
        form = SimulacaoFormulario(self.validSimulationData)
        self.assertFalse(form.is_valid())
