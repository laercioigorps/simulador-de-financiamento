from django.shortcuts import render
from django.views import View
from .forms import SimulacaoFormulario

# Create your views here.

class SimuladorView(View):
    
    def get(self, request):
        form = SimulacaoFormulario()
        return render(request, template_name="imoveis/pagina_simulador.html", context={"form": form})


class ResultadoSimulacaoView(View):

    def get(self, request):
        form = SimulacaoFormulario(request.GET)
        if form.is_valid():
            pass
        else:
            dados_iniciais = form.cleaned_data
            return render(request, template_name="imoveis/pagina_simulador.html", context={"form": form, "dados_iniciais":dados_iniciais}, status=400)
