from .models import SimuladorDeFinanciamento


def gerar_simulacao(dados):
    simulacao = SimuladorDeFinanciamento(
        valor_do_imovel=dados["valor_do_imovel"],
        valor_da_entrada=dados["valor_da_entrada"],
        prestacoes=int(dados["prestacoes"]),
        incluir_ITBI=dados["incluir_ITBI"],
    )
    simulacao.calcular_emprestimo_total()
    if dados["amortizacao"] == "PRICE":
        simulacao.gerar_tabela_price()
    else:
        simulacao.gerar_tabela_sac()
    return simulacao
