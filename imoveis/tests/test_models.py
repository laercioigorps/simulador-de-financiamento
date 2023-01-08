from django.test import TestCase
from ..models import (
    SimuladorDeFinanciamento,
    Amortizacao,
    AmortizacaoSAC,
    AmortizacaoPRICE,
)
from decimal import *
import datetime


class SimuladorDeFinanciamentoTest(TestCase):
    def setUp(self) -> None:
        self.simulador = SimuladorDeFinanciamento(
            valor_do_imovel=Decimal("150000"),
            valor_da_entrada=Decimal("30000"),
            prestacoes=240,
            incluir_ITBI=False,
        )
        # define taxas e indices para testes
        self.simulador.set_juros_mes(Decimal("0.64"))
        self.simulador.indice_itbi = Decimal("5.2")
        self.simulador.indice_custas = 0
        self.simulador.indice_seguro_cliente = Decimal("0.025017795")
        self.simulador.indice_seguro_imovel = Decimal("0.0044")
        self.simulador.tarifa = Decimal("25.00")
        self.simulador.indice_tac = Decimal("4")
        self.simulador.indice_renda_composta = Decimal("32")
        # valor total do financiamento fica 124800.00
        self.simulador.calcular_emprestimo_total()

    def test_set_juros_mes_atualiza_juros_ano(self):
        simulador = SimuladorDeFinanciamento()
        juros_mes = 1
        simulador.set_juros_mes(juros_mes)
        self.assertTrue(isinstance(simulador.juros_mes, Decimal))
        self.assertEqual(simulador.juros_mes, 1)
        self.assertEqual(simulador.juros_ano.compare(Decimal("12.68")), 0)

    def test_set_juros_ano_atualiza_juros_mes(self):
        simulador = SimuladorDeFinanciamento()
        juros_ano = Decimal("12.68")
        simulador.set_juros_ano(juros_ano)
        self.assertTrue(isinstance(simulador.juros_ano, Decimal))
        self.assertEqual(simulador.juros_ano.compare(Decimal("12.68")), 0)
        self.assertEqual(simulador.juros_mes.compare(Decimal("1")), 0)

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
        self.assertTrue(hasattr(simulador, "indice_renda_composta"))

    def test_simulador_de_financiamento_init(self):
        simulador = SimuladorDeFinanciamento(
            valor_do_imovel=Decimal("150000"),
            valor_da_entrada=Decimal("30000"),
            prestacoes=240,
            incluir_ITBI=False,
        )
        self.assertEqual(simulador.valor_do_imovel, Decimal("150000"))
        self.assertEqual(simulador.valor_da_entrada, Decimal("30000"))
        self.assertEqual(simulador.prestacoes, 240)
        self.assertEqual(simulador.incluir_ITBI, False)

    def test_calculo_do_valor_tac(self):
        self.assertEqual(self.simulador.valor_tac, Decimal("4800"))

    def test_calculo_do_valor_ITBI(self):
        self.simulador.incluir_ITBI = True
        self.simulador.calcular_ITBI()
        self.assertEqual(self.simulador.valor_ITBI, Decimal("7800"))

    def test_calcular_valor_total_do_financiamento_sem_ITBI(self):
        self.simulador.calcular_emprestimo_total()
        self.assertEqual(self.simulador.valor_total, Decimal("124800.00"))

    def test_calcular_valor_total_do_financiamento_com_ITBI(self):
        self.simulador.incluir_ITBI = True
        self.simulador.calcular_emprestimo_total()
        self.assertEqual(self.simulador.valor_total, Decimal("132912.00"))

    def test_data_de_simulacao_hoje(self):
        self.simulador.incluir_ITBI = True
        self.simulador.calcular_emprestimo_total()
        self.assertEqual(self.simulador.data, datetime.date.today())

    def test_tem_valor_das_prestacoes(self):
        self.simulador.gerar_tabela_price()
        self.assertEqual(self.simulador.prestacao, 1081.98)

    def test_get_cet_anualizado(self):
        self.simulador.gerar_tabela_price()
        self.assertEqual(self.simulador.get_cet(), 8.72)

    def test_get_renda_composta(self):
        self.simulador.prestacao = Decimal("1558.01")
        self.assertEqual(self.simulador.get_renda_composta(), Decimal("4868.78"))

    def test_simulacao_tem_saldo_com_vendedor(self):
        self.assertEqual(self.simulador.saldo_vendedor, Decimal("120000.00"))


class SimuladorDeFinanciamentoGeracaoDeTabelaDFTest(TestCase):
    def setUp(self) -> None:
        self.simulador = SimuladorDeFinanciamento(
            valor_do_imovel=Decimal("150000"),
            valor_da_entrada=Decimal("30000"),
            prestacoes=120,
            incluir_ITBI=False,
        )
        self.simulador.calcular_emprestimo_total()
        # define taxas e indices para testes
        self.simulador.set_juros_mes(Decimal("0.64"))
        self.simulador.indice_itbi = Decimal("5.2")
        self.simulador.indice_custas = 0
        self.simulador.indice_seguro_cliente = Decimal("0.025017795")
        self.simulador.indice_seguro_imovel = Decimal("0.0044")
        self.simulador.tarifa = Decimal("25.00")
        self.simulador.indice_tac = Decimal("4")
        # valor total do financiamento fica 124800.00

    def test_tabela_pandas_data_frame_gerada_tem_datas_mensais_de_parcelas_com_periodo_0(
        self,
    ):
        data = datetime.date(year=2023, month=1, day=1)
        self.simulador.data = data
        self.simulador.prestacoes = 4
        tabela = self.simulador.gerar_tabela_price()
        self.assertTrue("Data_Pagamento" in tabela)
        # primeira data não conta como parcela
        self.assertEqual(tabela["Data_Pagamento"][0].date(), data)

        self.assertEqual(
            tabela["Data_Pagamento"][1].date(), datetime.date(year=2023, month=2, day=1)
        )
        self.assertEqual(
            tabela["Data_Pagamento"][2].date(), datetime.date(year=2023, month=3, day=1)
        )
        self.assertEqual(
            tabela["Data_Pagamento"][3].date(), datetime.date(year=2023, month=4, day=1)
        )
        self.assertEqual(
            tabela["Data_Pagamento"][4].date(), datetime.date(year=2023, month=5, day=1)
        )

    def test_valor_parcela_do_financiamento_de_120_meses(self):
        df = self.simulador.gerar_tabela_price()
        self.assertTrue("Parcela" in df)
        # primeira parcela com valor 0
        self.assertEqual(df["Parcela"][0], 0)
        # demais parcelas valor normal
        self.assertEqual(df["Parcela"][1], 1493.15)

    def test_valor_da_amortizacao(self):
        df = self.simulador.gerar_tabela_price()
        self.assertTrue("Amortizacao" in df)
        # primeira parcela com amortizacao 0
        self.assertEqual(df["Amortizacao"][0], 0)
        # demais parcelas
        self.assertEqual(df["Amortizacao"][1], 694.43)
        self.assertEqual(df["Amortizacao"][120], 1483.65)

    def test_valor_do_juros(self):
        df = self.simulador.gerar_tabela_price()
        self.assertTrue("Juros" in df)
        # primeira parcela com juros 0
        self.assertEqual(df["Juros"][0], 0)
        # demais parcelas
        self.assertEqual(df["Juros"][1], 798.72)
        self.assertEqual(df["Juros"][120], 9.5)

    def test_total_pago(self):
        df = self.simulador.gerar_tabela_price()
        self.assertTrue("Total_Pago" in df)
        # primeira parcela com total_pago 0
        self.assertEqual(df["Total_Pago"][0], 0)
        # demais parcelas
        self.assertEqual(df["Total_Pago"][1], 694.43)
        self.assertEqual(df["Total_Pago"][120], 124800)

    def test_saldo_devedor(self):
        df = self.simulador.gerar_tabela_price()
        self.assertTrue("Saldo_Devedor" in df)
        # primeira parcela com saldo devedor total
        self.assertEqual(df["Saldo_Devedor"][0], 124800)
        # demais parcelas
        self.assertEqual(df["Saldo_Devedor"][1], 124105.57)
        self.assertEqual(df["Saldo_Devedor"][120], 0)

    def test_valor_seguro_do_cliente(self):
        df = self.simulador.gerar_tabela_price()
        self.assertTrue("Seguro_Cliente" in df)
        # primeiro seguro cliente com valor 0
        self.assertEqual(df["Seguro_Cliente"][0], 0)
        # demais parcelas
        self.assertEqual(df["Seguro_Cliente"][1], 31.22)
        self.assertEqual(df["Seguro_Cliente"][120], 0.37)

    def test_valor_seguro_imovel(self):
        df = self.simulador.gerar_tabela_price()
        self.assertTrue("Seguro_Imovel" in df)
        # primeiro seguro do imovel com valor 0
        self.assertEqual(df["Seguro_Imovel"][0], 0)
        # demais parcelas fixas
        self.assertEqual(df["Seguro_Imovel"][1], 6.6)
        self.assertEqual(df["Seguro_Imovel"][120], 6.6)

    def test_valor_da_tarifa_para_cada_prestacao(self):
        df = self.simulador.gerar_tabela_price()
        self.assertTrue("Tarifa" in df)
        # primeiro parcela com tarifa 0
        self.assertEqual(df["Tarifa"][0], 0)
        # demais parcelas fixas
        self.assertEqual(df["Tarifa"][1], 25)
        self.assertEqual(df["Tarifa"][120], 25)

    def test_valor_total_da_prestacao(self):
        df = self.simulador.gerar_tabela_price()
        self.assertTrue("Prestacao" in df)
        # primeiro parcela com tarifa 0
        self.assertEqual(df["Prestacao"][0], 0)
        # demais parcelas fixas
        self.assertEqual(df["Prestacao"][1], 1555.97)
        self.assertEqual(df["Prestacao"][120], 1525.12)

    def test_simulacao_gera_tabela(self):
        df = self.simulador.gerar_tabela_price()
        self.assertTrue(hasattr(self.simulador, "tabela"))
        self.assertEqual(type(self.simulador.tabela), list)

    def test_gerar_tabela_sac_valor_amortizacao(self):
        self.simulador.valor_total = Decimal("120000")
        self.simulador.prestacoes = 120
        df = self.simulador.gerar_tabela_sac()
        self.assertEqual(df["Amortizacao"][0], 0)
        self.assertEqual(df["Amortizacao"][1], 1000)

    def test_gerar_tabela_sac_valor_juros(self):
        self.simulador.valor_total = Decimal("120000")
        self.simulador.prestacoes = 120
        df = self.simulador.gerar_tabela_sac()
        self.assertEqual(df["Juros"][0], 0)
        self.assertEqual(df["Juros"][1], 768)
        self.assertEqual(df["Juros"][2], 761.6)
        self.assertEqual(df["Juros"][3], 755.2)
        self.assertEqual(df["Juros"][120], 6.4)

    def test_gerar_tabela_sac_valor_parcela(self):
        self.simulador.valor_total = Decimal("120000")
        self.simulador.prestacoes = 120
        df = self.simulador.gerar_tabela_sac()
        self.assertEqual(df["Parcela"][0], 0)
        self.assertEqual(df["Parcela"][1], 1768)
        self.assertEqual(df["Parcela"][2], 1761.6)
        self.assertEqual(df["Parcela"][3], 1755.2)
        self.assertEqual(df["Parcela"][120], 1006.4)

    def test_gerar_tabela_sac_valor_seguro_do_cliente(self):
        df = self.simulador.gerar_tabela_sac()
        self.assertTrue("Seguro_Cliente" in df)
        # primeiro seguro cliente com valor 0
        self.assertEqual(df["Seguro_Cliente"][0], 0)
        # demais parcelas
        self.assertEqual(df["Seguro_Cliente"][1], 31.22)
        self.assertEqual(df["Seguro_Cliente"][120], 0.26)

    def test_gerar_tabela_sac_valor_seguro_imovel(self):
        df = self.simulador.gerar_tabela_sac()
        self.assertTrue("Seguro_Imovel" in df)
        # primeiro seguro do imovel com valor 0
        self.assertEqual(df["Seguro_Imovel"][0], 0)
        # demais parcelas fixas
        self.assertEqual(df["Seguro_Imovel"][1], 6.6)
        self.assertEqual(df["Seguro_Imovel"][120], 6.6)

    def test_gerar_tabela_sac_valor_tarifas(self):
        df = self.simulador.gerar_tabela_sac()
        self.assertTrue("Tarifa" in df)
        # primeiro parcela com tarifa 0
        self.assertEqual(df["Tarifa"][0], 0)
        # demais parcelas fixas
        self.assertEqual(df["Tarifa"][1], 25)
        self.assertEqual(df["Tarifa"][120], 25)

    def test_gerar_tabela_sac_valor_total_da_prestacao(self):
        df = self.simulador.gerar_tabela_sac()
        # primeiro parcela com tarifa 0
        self.assertEqual(df["Prestacao"][0], 0)
        # 798.72(juros) + 1040(Amortização) + 31.22(seguro cliente) + 6.6(seguro imovel) + 25(taxas)
        self.assertEqual(df["Prestacao"][1], 1901.54)
        # 6.66(juros) + 1040(Amortização) + 0.26 (seguro cliente) + 6.6(seguro imovel) + 25(taxas)
        self.assertEqual(df["Prestacao"][120], 1078.52)

    def test_gerar_tabela_sac_tabela(self):
        df = self.simulador.gerar_tabela_sac()
        self.assertTrue(hasattr(self.simulador, "tabela"))
        self.assertEqual(type(self.simulador.tabela), list)

    def test_gerar_tabela_sac_gera_atributo_amortizacao_sac(self):
        df = self.simulador.gerar_tabela_sac()
        self.assertEqual(self.simulador.amortizacao, "SAC")

    def test_gerar_tabela_price_gera_atributo_amortizacao_price(self):
        df = self.simulador.gerar_tabela_price()
        self.assertEqual(self.simulador.amortizacao, "PRICE")


class TestSistemaDeAmortizacao(TestCase):
    def test_amortizacao_class_abstrata_com_methodos_abstratos(self):
        with self.assertRaises(Exception):
            amortizacao = Amortizacao()

    def test_amortizacao_SAC(self):
        sac = AmortizacaoSAC(valor_total=Decimal("100000"), prestacoes=100)
        self.assertEqual(sac.get_valor_amortizacao(), Decimal("-1000"))

        sac = AmortizacaoSAC(valor_total=Decimal("150000"), prestacoes=100)
        self.assertEqual(sac.get_valor_amortizacao(), Decimal("-1500"))

        self.assertEqual(sac.nome, "SAC")

    def test_amortizacao_PRICE(self):
        price = AmortizacaoPRICE(
            juros_mes=Decimal("0.05"), valor_total=Decimal("100000"), prestacoes=10
        )
        amortizacao = price.get_valor_amortizacao()
        self.assertEqual(round(amortizacao[0], 2), Decimal("-7950.46"))
        self.assertEqual(round(amortizacao[9], 2), Decimal("-12333.77"))

        price = AmortizacaoPRICE(
            juros_mes=Decimal("0.05"), valor_total=Decimal("150000"), prestacoes=10
        )
        amortizacao = price.get_valor_amortizacao()
        self.assertEqual(round(amortizacao[0], 2), Decimal("-11925.69"))
        self.assertEqual(round(amortizacao[9], 2), Decimal("-18500.65"))

        self.assertEqual(price.nome, "PRICE")
