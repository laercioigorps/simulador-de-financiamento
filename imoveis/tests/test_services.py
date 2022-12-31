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

    def test_atualizar_indices_do_simulador(self):
        simulador = SimuladorDeFinanciamento()
        simulador.atualizar_indices()
        self.assertTrue(hasattr(simulador, "juros_ano"))
        self.assertTrue(hasattr(simulador, "juros_mes"))
        self.assertTrue(hasattr(simulador, "indice_itbi"))
        self.assertTrue(hasattr(simulador, "indice_tac"))
        self.assertTrue(hasattr(simulador, "indice_custas"))
        self.assertTrue(hasattr(simulador, "indice_seguro_cliente"))
        self.assertTrue(hasattr(simulador, "indice_seguro_imovel"))
        self.assertTrue(hasattr(simulador, "tarifa"))

    def test_simulador_de_financiamento_init(self):
        simulador = SimuladorDeFinanciamento(
            valor_do_imovel=Decimal("150000"),
            valor_da_entrada=Decimal("30000"),
            prestacoes = 240,
            incluir_ITBI=False,
        )
        self.assertEqual(simulador.valor_do_imovel, Decimal("150000"))
        self.assertEqual(simulador.valor_da_entrada, Decimal("30000"))
        self.assertEqual(simulador.prestacoes, 240)
        self.assertEqual(simulador.incluir_ITBI, False)

    def test_calculo_do_valor_tac(self):
        simulador = SimuladorDeFinanciamento(
            valor_do_imovel=Decimal("150000"),
            valor_da_entrada=Decimal("30000"),
            prestacoes = 240,
            incluir_ITBI=False,
        )
        simulador.atualizar_indices()
        simulador.calcular_tac()
        self.assertEqual(simulador.valor_tac, Decimal("4800"))

    def test_calculo_do_valor_ITBI(self):
        simulador = SimuladorDeFinanciamento(
            valor_do_imovel=Decimal("150000"),
            valor_da_entrada=Decimal("30000"),
            prestacoes = 240,
            incluir_ITBI=True,
        )
        simulador.atualizar_indices()
        simulador.calcular_ITBI()
        self.assertEqual(simulador.valor_ITBI, Decimal("7800"))


    def test_calcular_valor_total_do_financiamento_sem_ITBI(self):
        simulador = SimuladorDeFinanciamento(
            valor_do_imovel=Decimal("150000"),
            valor_da_entrada=Decimal("30000"),
            prestacoes = 240,
            incluir_ITBI=False,
        )
        simulador.calcular_emprestimo_total()
        self.assertEqual(simulador.valor_total, Decimal("124800.00"))


    def test_calcular_valor_total_do_financiamento_com_ITBI(self):
        simulador = SimuladorDeFinanciamento(
            valor_do_imovel=Decimal("150000"),
            valor_da_entrada=Decimal("30000"),
            prestacoes = 240,
            incluir_ITBI=True,
        )
        simulador.calcular_emprestimo_total()
        self.assertEqual(simulador.valor_total, Decimal("132912.00"))


