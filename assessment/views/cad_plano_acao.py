from django.http import JsonResponse
from django.shortcuts import render, redirect
from django.views import View

from ..forms import MeuModeloAcaoForm, MeuModeloAcaoEditForm 
from ..models import PlanoAcaoModel, CadPlanodeAcaoModel

class CadPlanodeAcao(View):
    template_name = 'paginas/cad_plano_acao.html'

    def get(self, request, id):

        acao = PlanoAcaoModel.objects.get(id=id)
        cad_acoes = CadPlanodeAcaoModel.objects.filter(planoacao=acao)
        form1 = MeuModeloAcaoForm()
        form2 = MeuModeloAcaoEditForm()

        return render(request, self.template_name, {    
            'acao': acao,
            'cad_acoes': cad_acoes,
            'acao_id': id,
            'form1': form1,
            'form2': form2
        })

    def post(self, request, id):
        form1 = MeuModeloAcaoForm(request.POST, request.FILES)
        if form1.is_valid():
            cad_acao_instance = form1.save(commit=False)  # Cria a instância sem salvar no banco
            cad_acao_instance.planoacao = PlanoAcaoModel.objects.get(id=id)  # Ajuste conforme o id necessário
            cad_acao_instance.save()  # Salva no banco com o campo `planoacao`

            return redirect('cad_planodeacao', id=id)


        return render(request, self.template_name, {
            'form1': form1,
            'cad_acoes': CadPlanodeAcaoModel.objects.filter(planoacao_id=id),
            'acao_id': id
        })

    # Excluir Plano de Ação
    def delete(self, request, id):
        try:
            cad_acao = CadPlanodeAcaoModel.objects.get(id=id)

            # Exclui o plano de ação
            cad_acao.delete()
            return JsonResponse({'success': True})
        except PlanoAcaoModel.DoesNotExist:
            return JsonResponse({'success': False, 'error': 'Item não encontrado'})

def editar_cad_plano_acao(request, id):
    cad_acao = CadPlanodeAcaoModel.objects.get(id=id)  # Obtenha a instância correta

    if request.method == 'POST':
        # Passe a instância que deseja atualizar
        form = MeuModeloAcaoEditForm(request.POST, request.FILES, instance=cad_acao)
        if form.is_valid():
            form.save()  # Atualiza a instância existente
            return redirect('cad_planodeacao', id=cad_acao.planoacao.id)  # Redireciona para uma página de sucesso (ou para outra página desejada)
    
    # Requisição AJAX para buscar os dados atuais da instância
    if request.headers.get('x-requested-with') == 'XMLHttpRequest':
        response_data = {
            'projeto': cad_acao.projeto,
            'subcontrole': cad_acao.subcontrole,
            'acao': cad_acao.acao,
            'onde': cad_acao.onde,
            'responsavel': cad_acao.responsavel,
            'inicio_pla': cad_acao.inicio_pla,
            'fim_pla': cad_acao.fim_pla,
            'inicio_real': cad_acao.inicio_real,
            'fim_real': cad_acao.fim_real,
            'quanto': cad_acao.quanto,
            'observacao': cad_acao.observacao
        }
        return JsonResponse(response_data)
    
    # Renderiza o formulário de edição com a instância correta
    else:
        form = MeuModeloAcaoEditForm(instance=cad_acao)
        return render(request, 'paginas/cad_plano_acao.html', {'form2': form, 'cad_acao': cad_acao})

# Função dedicada pra realizar os downloads dos arquivos
def download_file(request, filename):
    file_path = os.path.join(settings.MEDIA_ROOT, filename)
    if os.path.exists(file_path):
        with open(file_path, 'rb') as fh:
            response = HttpResponse(fh.read(), content_type="application/vnd.ms-excel")
            response['Content-Disposition'] = f'attachment; filename={os.path.basename(file_path)}'
            return response
    raise Http404
