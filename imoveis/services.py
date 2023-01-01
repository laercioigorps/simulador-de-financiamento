from decimal import *
import datetime

class SimuladorDeFinanciamento:

    def __init__(
        self, 
        valor_do_imovel = None,
        valor_da_entrada = None, 
        prestacoes = None, 
        incluir_ITBI = False
    ) -> None:
        self.valor_do_imovel = valor_do_imovel
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
        self.set_juros_mes(0.64)
        self.indice_itbi = Decimal("5.2")
        self.indice_custas = 0
        self.indice_seguro_cliente = Decimal("0.025017795")
        self.indice_seguro_imovel = Decimal("0.0044")
        self.tarifa = Decimal("25.00")
        self.indice_tac = Decimal("4")

    def calcular_tac(self):
        self.valor_tac = (self.valor_do_imovel - self.valor_da_entrada + self.valor_ITBI) * self.indice_tac/100

    def calcular_ITBI(self):
        self.valor_ITBI = self.valor_do_imovel * self.indice_itbi/100

    def calcular_emprestimo_total(self):
        if(self.incluir_ITBI):
            self.calcular_ITBI()
        self.calcular_tac()
        self.valor_total = (self.valor_do_imovel - self.valor_da_entrada) + self.valor_tac + self.valor_ITBI