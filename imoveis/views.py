from django.shortcuts import render
from django.views import View
from .forms import SimulacaoFormulario
from .services import SimuladorDeFinanciamento

# Create your views here.

class SimuladorView(View):
    
    def get(self, request):
        form = SimulacaoFormulario()
        return render(request, template_name="imoveis/pagina_simulador.html", context={"form": form})


class ResultadoSimulacaoView(View):

    def get(self, request):
        form = SimulacaoFormulario(request.GET)
        if form.is_valid():
            dados_iniciais = form.cleaned_data
            simulacao = SimuladorDeFinanciamento(
                    valor_do_imovel = form.cleaned_data["valor_do_imovel"],
                    valor_da_entrada = form.cleaned_data["valor_da_entrada"], 
                    prestacoes = int(form.cleaned_data["prestacoes"]), 
                    incluir_ITBI = form.cleaned_data["incluir_ITBI"]
                )
            simulacao.calcular_emprestimo_total()
            if(dados_iniciais["amortizacao"] == "PRICE"):
                simulacao.gerar_tabela_price()
            else:
                simulacao.gerar_tabela_sac()
            return render(request, template_name="imoveis/resultado_simulacao.html", context={"dados_iniciais":dados_iniciais, "simulacao": simulacao})
        else:
            dados_iniciais = form.cleaned_data
            return render(request, template_name="imoveis/pagina_simulador.html", context={"form": form, "dados_iniciais":dados_iniciais}, status=400)
