from django.shortcuts import render
from django.views import View
from .forms import SimulacaoFormulario

# Create your views here.

class SimuladorView(View):
    
    def get(self, request):
        form = SimulacaoFormulario()
        return render(request, template_name="imoveis/pagina_simulador.html", context={"form": form})


class ResultadoSimulacaoView(View):
    pass
