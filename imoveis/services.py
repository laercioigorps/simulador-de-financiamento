from .models import SimuladorDeFinanciamento
from .models import AmortizacaoPRICE, AmortizacaoSAC


def gerar_simulacao(dados):
    simulacao = SimuladorDeFinanciamento(
        valor_do_imovel=dados["valor_do_imovel"],
        valor_da_entrada=dados["valor_da_entrada"],
        prestacoes=int(dados["prestacoes"]),
        incluir_ITBI=dados["incluir_ITBI"],
    )
    simulacao.calcular_emprestimo_total()
    if dados["amortizacao"] == "PRICE":
        amortizacao = AmortizacaoPRICE(simulacao.juros_mes/100, simulacao.valor_total, simulacao.prestacoes)
    else:
        amortizacao = AmortizacaoSAC(simulacao.valor_total, simulacao.prestacoes)
    simulacao.gerar_tabela(amortizacao)
    return simulacao
