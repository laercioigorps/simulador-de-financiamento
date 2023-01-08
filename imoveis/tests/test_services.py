from django.test import TestCase
from ..forms import SimulacaoFormulario
from ..services import gerar_simulacao
from ..models import SimuladorDeFinanciamento

class TestServicoGerarSimulacao(TestCase):

    def setUp(self) -> None:
        self.validSimulationData = {
            "data_nascimento": "09/08/1997",
            "valor_do_imovel": 150000,
            "valor_da_entrada": 30000,
            "incluir_ITBI": False,
            "prestacoes": 360,
            "amortizacao": "PRICE",
        }
        self.form_valido = SimulacaoFormulario(self.validSimulationData)

    def test_gerar_simulacao_servico(self):
        self.assertTrue(self.form_valido.is_valid())
        simulacao = gerar_simulacao(self.form_valido.cleaned_data)
        self.assertTrue(isinstance(simulacao, SimuladorDeFinanciamento))
        self.assertTrue(hasattr(simulacao, "valor_total"))
        self.assertTrue(hasattr(simulacao, "tabela"))