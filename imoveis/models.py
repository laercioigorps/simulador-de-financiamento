from decimal import *
import datetime
import pandas as pd
import numpy_financial as npf
import numpy as np
from abc import ABC, abstractmethod


class SimuladorDeFinanciamento:
    def __init__(
        self,
        valor_do_imovel=None,
        valor_da_entrada=None,
        prestacoes=None,
        incluir_ITBI=False,
    ) -> None:
        self.valor_do_imovel = valor_do_imovel
        if self.valor_do_imovel:
            self.valor_do_imovel = valor_do_imovel.quantize(Decimal(".01"))
            self.saldo_vendedor = (valor_do_imovel - valor_da_entrada).quantize(
                Decimal(".01")
            )
        self.valor_da_entrada = valor_da_entrada
        self.prestacoes = prestacoes
        self.incluir_ITBI = incluir_ITBI
        self.valor_ITBI = 0
        self.data = datetime.date.today()
        self.atualizar_indices()

    def set_juros_mes(self, juros):
        self.juros_mes = Decimal(juros).quantize(Decimal(".01"))
        self.juros_ano = ((((1 + self.juros_mes / 100) ** 12) - 1) * 100).quantize(
            Decimal(".01")
        )

    def set_juros_ano(self, juros):
        self.juros_ano = Decimal(juros).quantize(Decimal(".01"))
        self.juros_mes = (
            ((1 + self.juros_ano / 100) ** Decimal(1 / 12) - 1) * 100
        ).quantize(Decimal(".01"))

    def atualizar_indices(self):
        self.set_juros_ano(7.99)
        self.indice_itbi = Decimal("5.2")
        self.indice_custas = 0
        self.indice_seguro_cliente = Decimal("0.025017795")
        self.indice_seguro_imovel = Decimal("0.0044")
        self.tarifa = Decimal("25.00")
        self.indice_tac = Decimal("4")
        self.indice_renda_composta = Decimal("32.00")

    def calcular_tac(self):
        self.valor_tac = (
            (self.valor_do_imovel - self.valor_da_entrada + self.valor_ITBI)
            * self.indice_tac
            / 100
        ).quantize(Decimal(".01"))

    def calcular_ITBI(self):
        self.valor_ITBI = (self.valor_do_imovel * self.indice_itbi / 100).quantize(
            Decimal(".01")
        )

    def calcular_emprestimo_total(self):
        if self.incluir_ITBI:
            self.calcular_ITBI()
        self.calcular_tac()
        self.valor_total = (
            (self.valor_do_imovel - self.valor_da_entrada)
            + self.valor_tac
            + self.valor_ITBI
        ).quantize(Decimal(".01"))

    def get_tabela_inicial_com_datas(self):
        rng = pd.date_range(self.data, periods=self.prestacoes + 1, freq="MS")
        rng.name = "Data_Pagamento"
        df = pd.DataFrame(index=rng, columns=[], dtype="float")
        df.reset_index(inplace=True)
        df.index += 0
        df.index.name = "Periodo"
        return df

    def get_cet(self):
        prest = [-self.valor_total] + self.df["Prestacao"].to_list()[1:]
        cet_m = npf.irr(prest) * 100
        cet_ano = round((((1 + cet_m / 100) ** 12) - 1) * 100, 2)
        return cet_ano

    def get_renda_composta(self):
        return (
            Decimal(str(self.prestacao)) * 100 / self.indice_renda_composta
        ).quantize(Decimal(".01"))

    def set_valor_parcela(self, df):
        df["Parcela"] = df["Juros"] + df["Amortizacao"]
        df.at[0, "Parcela"] = 0
        return df

    def set_valor_amortizacao(self, df, sistema_de_amortizacao):
        amortizacao = sistema_de_amortizacao.get_valor_amortizacao()
        if(type(amortizacao) == np.ndarray):
            amortizacao = np.insert(amortizacao, 0, Decimal("0"), axis=0)
            df["Amortizacao"] = amortizacao
        else:
            df["Amortizacao"] = amortizacao
            df.at[0, "Amortizacao"] = 0

        return df

    def set_valor_juros(self, df):
        df["Juros"] = -(df["Saldo_Devedor"] - df["Amortizacao"]) * self.juros_mes / 100
        df.at[0, "Juros"] = 0
        return df

    def set_total_pago(self, df):
        df["Total_Pago"] = (df["Amortizacao"]).cumsum()
        return df

    def set_saldo_devedor(self, df):
        df["Saldo_Devedor"] = self.valor_total + df["Total_Pago"]
        return df

    def set_seguro_cliente(self, df):
        df["Seguro_Cliente"] = (
            (df["Saldo_Devedor"] - df["Amortizacao"]) * self.indice_seguro_cliente / 100
        )
        df.at[0, "Seguro_Cliente"] = 0
        return df

    def set_seguro_imovel(self, df):
        df["Seguro_Imovel"] = self.valor_do_imovel * self.indice_seguro_imovel / 100
        df.at[0, "Seguro_Imovel"] = 0
        return df

    def set_tarifas(self, df):
        df["Tarifa"] = self.tarifa
        df.at[0, "Tarifa"] = 0
        return df

    def set_valor_total_prestacao(self, df):
        df["Prestacao"] = (
            df["Parcela"] + df["Seguro_Cliente"] + df["Seguro_Imovel"] + df["Tarifa"]
        )
        df["Prestacao"] = df["Prestacao"].astype(float).round(2)
        # registra a primeira prestacao como a base do financiamento
        self.prestacao = df["Prestacao"][1]
        return df

    def arredondar_valores(self, df):
        df["Parcela"] = df["Parcela"].astype(float).round(2)
        df["Amortizacao"] = df["Amortizacao"].astype(float).round(2)
        df["Juros"] = df["Juros"].astype(float).round(2)
        df["Total_Pago"] = df["Total_Pago"].astype(float).round(2)
        df["Saldo_Devedor"] = df["Saldo_Devedor"].astype(float).round(2)
        df["Seguro_Cliente"] = df["Seguro_Cliente"].astype(float).round(2)
        df["Seguro_Imovel"] = df["Seguro_Imovel"].astype(float).round(2)
        df["Tarifa"] = df["Tarifa"].astype(float).round(2)
        return df

    def set_positivo(self, df):
        df["Parcela"] = df["Parcela"].abs()
        df["Amortizacao"] = df["Amortizacao"].abs()
        df["Juros"] = df["Juros"].abs()
        df["Total_Pago"] = df["Total_Pago"].abs()
        return df

    def gerar_tabela(self, sistemaDeAmortizacao):
        df = self.get_tabela_inicial_com_datas()
        self.set_valor_amortizacao(df, sistemaDeAmortizacao)
        self.set_total_pago(df)
        self.set_saldo_devedor(df)
        self.set_valor_juros(df)
        self.set_valor_parcela(df)
        self.set_seguro_cliente(df)
        self.set_seguro_imovel(df)
        self.set_tarifas(df)
        # arredondar valores
        df = self.arredondar_valores(df)
        # turn all into positive values
        df = self.set_positivo(df)
        # calculo total das presta????es
        self.set_valor_total_prestacao(df)
        self.tabela = df.to_dict("records")
        self.amortizacao = sistemaDeAmortizacao.nome
        self.df = df
        return df



class Amortizacao(ABC):
    @abstractmethod
    def get_valor_amortizacao(self):
        pass


class AmortizacaoSAC(Amortizacao):

    nome = "SAC"

    def __init__(self, valor_total, prestacoes) -> None:
        self.valor_total = valor_total
        self.prestacoes = prestacoes

    def get_valor_amortizacao(self):
        return -self.valor_total / self.prestacoes


class AmortizacaoPRICE(Amortizacao):

    nome = "PRICE"

    def __init__(self, juros_mes, valor_total, prestacoes) -> None:
        self.juros_mes = juros_mes
        self.valor_total = valor_total
        self.prestacoes = prestacoes

    def get_valor_amortizacao(self):
        index = [i for i in range(1, self.prestacoes + 1)]
        return npf.ppmt(self.juros_mes, index, self.prestacoes, self.valor_total)
