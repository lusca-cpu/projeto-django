from django.conf import settings
from django.http import HttpResponse, JsonResponse
from django.shortcuts import render
from django.views import View

from ..models import PlanoAcaoModel

import os

# Função para renderizar a página planodeacao.html
class PlanodeAcao(View):
    template_name = 'paginas/plano_acao.html'

    def get(self, request):
        acoes = PlanoAcaoModel.objects.all()

        return render(request, self.template_name, { 'acoes': acoes })

    # Excluir Plano de Ação
    def delete(self, request, id):
        try:
            acao = PlanoAcaoModel.objects.get(id=id)

            # Exclui o palno de ação
            acao.delete()
            return JsonResponse({'success': True})
        except PlanoAcaoModel.DoesNotExist:
            return JsonResponse({'success': False, 'error': 'Item não encontrado'})

