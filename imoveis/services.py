from decimal import *

class SimuladorDeFinanciamento:
    
    def set_juros_mes(self, juros):
        self.juros_mes = Decimal(juros).quantize(Decimal('.01'))
        self.juros_ano = ((((1 + self.juros_mes/100) ** 12) -1) *100).quantize(Decimal('.01'))

    def set_juros_ano(self, juros):
        self.juros_ano = Decimal(juros).quantize(Decimal('.01'))
        self.juros_mes = (((1 + self.juros_ano/100) ** Decimal(1/12) - 1) * 100).quantize(Decimal('.01'))
