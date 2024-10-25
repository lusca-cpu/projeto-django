from django.conf import settings
from django.http import HttpResponse, JsonResponse, HttpResponseRedirect
from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse
from django.utils import timezone
from django.views import View

from datetime import date

from ..forms import MeuModeloForm, MeuModeloEditForm
from ..models import FrameworkModel, AssessmentModel, CisModelTemplate, IsoModelTemplate, NistModelTemplate, PlanilhaGenericaTemplate

import os
import pandas as pd

# Class para renderizar a página framework.html
class Framework(View):
    template_name = 'paginas/framework.html'

    # Exibir FrameworksModel e o formulário
    def get(self, request):
        frameworks = FrameworkModel.objects.all()
        form1 = MeuModeloForm()  # Inicializa o formulário no GET
        form2 = MeuModeloEditForm()
        return render(request, self.template_name, {
            'frameworks': frameworks, 
            'form1': form1, # Passa o formulário de upload para o template
            'form2': form2  # Passa o formulário de edição para o template
        })

    # Adicionar Framework
    def post(self, request):
        form1 = MeuModeloForm(request.POST, request.FILES)
        if form1.is_valid():
            framework = form1.save()  # Salva o framework e o arquivo no banco de dados

            if framework.excel_file:
                file_path = framework.excel_file.path  # Caminho do arquivo no servidor
                file_name = framework.excel_file.name.lower()  # Nome do arquivo (minúsculo)

                # Carregar o arquivo Excel usando pandas
                df = pd.read_excel(file_path)

                # Verifica o nome do arquivo e decide em qual modelo salvar
                if 'iso' in file_name:
                    for _, row in df.iterrows():
                        IsoModelTemplate.objects.create(
                            framework=framework,  
                            secao=row['Seção'],
                            codCatecoria=row['Cod. Categoria'],
                            categoria=row['Categoria'],
                            controle=row['Controle'],
                            diretrizes=row['Diretrizes para implementação'],
                            prioControle=row['Prioridade do controle'],
                            notaCss=row['Nota (Css)'],
                            notaCl=row['Nota (Cl.)'],
                            comentarios=row['Comentários'],
                            meta=row['Meta'],
                        )

                elif 'nist' in file_name:
                    for _, row in df.iterrows():
                        NistModelTemplate.objects.create(
                            framework=framework,  
                            categoria=row['Categoria'],
                            funcao=row['Função'],
                            codigo=row['Código'],
                            subcategoria=row['Subcategoria'],
                            informacao=row['Informações adicionais'],
                            notaCss=row['Nota (Css)'],
                            notaCl=row['Nota (Cl.)'],
                            comentarios=row['Comentários'],
                            meta=row['Meta'],
                        )

                elif 'cis' in file_name:
                    for _, row in df.iterrows():
                        CisModelTemplate.objects.create(
                            framework=framework,  
                            idControle=row['# Controle'],
                            controle=row['Controle'],
                            tipoAtivo=row['Tipo de Ativo'],
                            funcao=row['Função'],
                            idSubConjunto=row['# Subconjunto'],
                            subConjunto=row['Subconjunto'],
                            nivel=row['Nível'],
                            resultadoCss=row['Resultado (Css)'],
                            resultadoCl=row['Resultado (Cl.)'],
                            comentarios=row['Comentários'],
                            meta=row['Meta'],
                        )

                # Se o campo is_proprio estiver marcado, salvar em PlanilhaGenerica
                if framework.is_proprio:
                    for _, row in df.iterrows():
                        PlanilhaGenericaTemplate.objects.create(
                            framework=framework,  
                            idControle=row['Id Controle*'],
                            controle=row['Controle*'],
                            idSubControle=row['Id Subcontrole'],
                            subControle=row['Subcontrole'],
                            funcaoSeguranca=row['Função de segurança'],
                            tipoAtivo=row['Tipo de Ativo'],
                            informacoesAdicionais=row['Informações Adicionais'],
                            resultadoCss=row['Resultado (Css)'],
                            resultadoCl=row['Resultado (Cl.)'],
                            comentarios=row['Comentários'],
                            meta=row['Meta'],
                        )
            # Redireciona para evitar o reenvio do formulário ao atualizar a página
            return HttpResponseRedirect(reverse('framework'))

        # Se o formulário não for válido, renderiza a página novamente com o erro
        return render(request, self.template_name, {
            'form1': form1,
            'frameworks': FrameworkModel.objects.all()
        })

    # Excluir Framework
    def delete(self, request, id):
        try:
            framework = FrameworkModel.objects.get(id=id)

            # Exclui o arquivo relacionado ao framework
            if framework.excel_file: 
                file_path = os.path.join(settings.MEDIA_ROOT, framework.excel_file.name)
                if os.path.isfile(file_path):
                    os.remove(file_path)

            # Exclui o framework
            framework.delete()
            return JsonResponse({'success': True})
        except FrameworkModel.DoesNotExist:
            return JsonResponse({'success': False, 'error': 'Item não encontrado'})

def editar_framework(request, id):
    framework = FrameworkModel.objects.get(id=id)
    
    # Verifica se existe uma instância no AssessmentModel associada a este framework
    assessments = AssessmentModel.objects.filter(framework=framework)
    has_assessment = assessments.exists()
    assessment = assessments.first() if has_assessment else None

    
    if request.method == 'POST':
        form = MeuModeloEditForm(request.POST, request.FILES, instance=framework)
        if form.is_valid():
            # Salvar a instância para garantir que o novo arquivo é processado
            old_file = framework.excel_file
            form.save()

            # Atualizar a data de upload para a data atual
            framework.data_upload = timezone.now().date()
            framework.save()

            # Verifique se houve alteração no campo de arquivo
            if 'excel_file' in form.changed_data:
                if old_file and old_file.name:
                    # Caminho do arquivo antigo
                    old_file_path = os.path.join(settings.MEDIA_ROOT, 'uploads', old_file.name)
                    if os.path.isfile(old_file_path):
                        os.remove(old_file_path)

            # Se a instância de AssessmentModel existir, atualize-a
            if has_assessment:
                assessment.nome = framework.nome
                assessment.excel_file = framework.excel_file
                assessment.save()

            return redirect('listar_frameworks')
    
    # Retorna dados em formato JSON para requisições AJAX
    if request.headers.get('x-requested-with') == 'XMLHttpRequest':
        response_data = {
            'nome': framework.nome,
            'descricao': framework.descricao,
            'criterio': framework.criterio,
            'uploaded_file_url': framework.excel_file.url if framework.excel_file else None,
            'has_assessment': has_assessment
        }
        return JsonResponse(response_data)
    
    # Renderizar a página normalmente em caso de GET sem ser AJAX
    else:
        form = MeuModeloEditForm(instance=framework)
        return render(request, 'paginas/framework.html', {'form2': form, 'framework': framework})

# Função dedicada pra realizar os downloads dos arquivos
def download_file(request, filename):
    file_path = os.path.join(settings.MEDIA_ROOT, filename)
    if os.path.exists(file_path):
        with open(file_path, 'rb') as fh:
            response = HttpResponse(fh.read(), content_type="application/vnd.ms-excel")
            response['Content-Disposition'] = f'attachment; filename={os.path.basename(file_path)}'
            return response
    raise Http404
