from django.shortcuts import render
from django.views import View

# Create your views here.

class SimuladorView(View):
    
    def get(self, request):
        return render(request, template_name="imoveis/pagina_simulador.html")
