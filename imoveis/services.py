from decimal import *
import datetime
import pandas as pd
import numpy as np
import numpy_financial as npf

class SimuladorDeFinanciamento:

    def __init__(
        self, 
        valor_do_imovel = None,
        valor_da_entrada = None, 
        prestacoes = None, 
        incluir_ITBI = False
    ) -> None:
        self.valor_do_imovel = valor_do_imovel
        if(self.valor_do_imovel):
            self.valor_do_imovel = valor_do_imovel.quantize(Decimal('.01'))
            self.saldo_vendedor = (valor_do_imovel - valor_da_entrada).quantize(Decimal('.01'))
        self.valor_da_entrada = valor_da_entrada
        self.prestacoes = prestacoes
        self.incluir_ITBI = incluir_ITBI
        self.valor_ITBI = 0
        self.data = datetime.date.today()
        self.atualizar_indices()
    
    def set_juros_mes(self, juros):
        self.juros_mes = Decimal(juros).quantize(Decimal('.01'))
        self.juros_ano = ((((1 + self.juros_mes/100) ** 12) -1) *100).quantize(Decimal('.01'))  

    def set_juros_ano(self, juros):
        self.juros_ano = Decimal(juros).quantize(Decimal('.01'))
        self.juros_mes = (((1 + self.juros_ano/100) ** Decimal(1/12) - 1) * 100).quantize(Decimal('.01'))

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
        self.valor_tac = ((self.valor_do_imovel - self.valor_da_entrada + self.valor_ITBI) * self.indice_tac/100).quantize(Decimal('.01'))  

    def calcular_ITBI(self):
        self.valor_ITBI = (self.valor_do_imovel * self.indice_itbi/100).quantize(Decimal('.01'))  

    def calcular_emprestimo_total(self):
        if(self.incluir_ITBI):
            self.calcular_ITBI()
        self.calcular_tac()
        self.valor_total = ((self.valor_do_imovel - self.valor_da_entrada) + self.valor_tac + self.valor_ITBI).quantize(Decimal('.01'))  

    def get_tabela_inicial_com_datas(self):
        rng = pd.date_range(self.data, periods=self.prestacoes + 1, freq='MS')
        rng.name = "Data_Pagamento"
        df = pd.DataFrame(index=rng,columns=[], dtype='float')
        df.reset_index(inplace=True)
        df.index += 0
        df.index.name = "Periodo"
        return df

    def get_cet(self):
        cet_mes = npf.rate(self.prestacoes, -Decimal(self.prestacao), self.valor_total, 0)
        return ((((1 + cet_mes) ** 12) -1) *100).quantize(Decimal('.01'))

    def get_renda_composta(self):
        return (Decimal(str(self.prestacao))*100/self.indice_renda_composta).quantize(Decimal('.01'))

    def set_valor_parcela_price(self, df):
        df["Parcela"] = npf.pmt(self.juros_mes/100, self.prestacoes, self.valor_total)
        df.at[0,'Parcela'] = 0
        return df

    def set_valor_parcela_sac(self, df):
        df['Parcela'] = df['Juros'] + df['Amortizacao'].abs()
        df.at[0,'Parcela'] = 0
        return df

    def set_valor_amortizacao_price(self, df):
        df["Amortizacao"] = npf.ppmt(self.juros_mes/100, df.index, self.prestacoes, self.valor_total)
        df.at[0,'Amortizacao'] = 0
        return df

    def set_valor_amortizacao_sac(self, df):
        df["Amortizacao"] = -self.valor_total/self.prestacoes
        df.at[0,'Amortizacao'] = 0
        return df

    def set_valor_juros(self, df):
        df["Juros"] = npf.ipmt(self.juros_mes/100, df.index, self.prestacoes, self.valor_total)
        df.at[0,'Juros'] = 0
        return df

    def set_valor_juros_sac(self, df):
        df["Juros"] = ((df["Saldo_Devedor"] - df["Amortizacao"]) * float(self.juros_mes/100)).round(2)
        df.at[0,'Juros'] = 0
        return df

    def set_total_pago(self, df):
        df["Total_Pago"] = (df["Amortizacao"]).cumsum()
        return df

    def set_saldo_devedor(self, df):
        df["Saldo_Devedor"] = self.valor_total + df["Total_Pago"]
        return df

    def set_seguro_cliente(self, df):
        df["Seguro_Cliente"] = (df["Saldo_Devedor"] - df["Amortizacao"]) * self.indice_seguro_cliente/100
        df.at[0,'Seguro_Cliente'] = 0
        return df

    def set_seguro_imovel(self, df):
        df["Seguro_Imovel"] = self.valor_do_imovel * self.indice_seguro_imovel/100
        df.at[0,'Seguro_Imovel'] = 0
        return df

    def set_tarifas(self, df):
        df["Tarifa"] = self.tarifa
        df.at[0,'Tarifa'] = 0

    def set_valor_total_prestacao(self, df):
        df["Prestacao"] = df["Parcela"] + df["Seguro_Cliente"] + df["Seguro_Imovel"] + df["Tarifa"]
        df['Prestacao'] = df['Prestacao'].astype(float).round(2)
        #registra a primeira prestacao como a base do financiamento
        self.prestacao = df["Prestacao"][1]
        return df

    def gerar_tabela_price(self):
        df = self.get_tabela_inicial_com_datas()
        self.set_valor_parcela_price(df)
        self.set_valor_amortizacao_price(df)
        self.set_valor_juros(df)
        self.set_total_pago(df)
        self.set_saldo_devedor(df)
        self.set_seguro_cliente(df)
        self.set_seguro_imovel(df)
        self.set_tarifas(df)
        # arredondar valores
        df['Parcela'] = df['Parcela'].astype(float).round(2)
        df['Amortizacao'] = df['Amortizacao'].astype(float).round(2)
        df['Juros'] = df['Juros'].astype(float).round(2)
        df['Total_Pago'] = df['Total_Pago'].astype(float).round(2)
        df['Saldo_Devedor'] = df['Saldo_Devedor'].astype(float).round(2)
        df['Seguro_Cliente'] = df['Seguro_Cliente'].astype(float).round(2)
        df['Seguro_Imovel'] = df['Seguro_Imovel'].astype(float).round(2)
        df['Tarifa'] = df['Tarifa'].astype(float).round(2)
        #turn all into positive values
        df["Parcela"] = df["Parcela"].abs()
        df["Amortizacao"] = df["Amortizacao"].abs()
        df["Juros"] = df["Juros"].abs()
        df["Total_Pago"] = df["Total_Pago"].abs()
        #calculo total das prestações
        self.set_valor_total_prestacao(df)
        self.tabela = df.to_dict("records")
        return df