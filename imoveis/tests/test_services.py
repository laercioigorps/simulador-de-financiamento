from django.test import TestCase
from ..services import SimuladorDeFinanciamento
from decimal import *

class SimuladorDeFinanciamentoTest(TestCase):

    def test_set_juros_mes_atualiza_juros_ano(self):
        simulador = SimuladorDeFinanciamento()
        juros_mes = 1
        simulador.set_juros_mes(juros_mes)
        self.assertTrue(isinstance(simulador.juros_mes, Decimal))
        self.assertEqual(simulador.juros_mes, 1)
        self.assertEqual(simulador.juros_ano.compare( Decimal("12.68")), 0)

    def test_set_juros_ano_atualiza_juros_mes(self):
        simulador = SimuladorDeFinanciamento()
        juros_ano = Decimal("12.68")
        simulador.set_juros_ano(juros_ano)
        self.assertTrue(isinstance(simulador.juros_ano, Decimal))
        self.assertEqual(simulador.juros_ano.compare( Decimal("12.68")), 0)
        self.assertEqual(simulador.juros_mes.compare( Decimal("1")), 0) 