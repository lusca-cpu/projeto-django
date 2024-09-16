from django.shortcuts import render, redirect, get_object_or_404
from .forms import MeuModeloForm, MeuModeloEditForm, NovoAssessmentForm
from .models import MeuModelo, PlanilhaGenerica, CisControl, Iso, NistCsf

from django.views import View
from django.views.generic import TemplateView
from django.views.generic.edit import UpdateView
from django.conf import settings
from django.http import HttpResponse, JsonResponse
from django.template.loader import render_to_string
from django.contrib import messages
import os
import pandas as pd
import uuid


def index(request):
    return render(request, 'paginas/index.html')

def security_assessment(request):
    return render(request, 'paginas/security.html')

# Função para renderizar a página framework.html
class Framework(View):
    template_name = 'paginas/framework.html'

    # Exibir frameworks e o formulário
    def get(self, request):
        frameworks = MeuModelo.objects.all()
        form1 = MeuModeloForm()  # Inicializa o formulário no GET
        fomr2 = MeuModeloEditForm()
        return render(request, self.template_name, {
            'frameworks': frameworks, 
            'form1': form1, # Passa o formulário de upload para o template
            'form2': fomr2  # Passa o formulário de edição para o template
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

                # Gera um ID único para este upload
                upload_id = uuid.uuid4()

                # Verifica o nome do arquivo e decide em qual modelo salvar
                if 'iso' in file_name:
                    for _, row in df.iterrows():
                        Iso.objects.create(
                            framework=framework,  
                            secao=row['Seção'],
                            codCatecoria=row['Cod. Categoria'],
                            categoria=row['Categoria'],
                            controle=row['Controle'],
                            diretrizes=row['Diretrizes para implementação'],
                            prioControle=row['Prioridade do controle'],
                            nota=row['Nota'],
                            comentarios=row['Comentários'],
                            meta=row['Meta'],
                            upload_id=upload_id  # Adiciona o upload_id único
                        )

                elif 'nist' in file_name:
                    for _, row in df.iterrows():
                        NistCsf.objects.create(
                            framework=framework,  
                            categoria=row['Categoria'],
                            funcao=row['Função'],
                            codigo=row['Código'],
                            subcategoria=row['Subcategoria'],
                            informacao=row['Informações adicionais'],
                            nota=row['Nota'],
                            comentarios=row['Comentários'],
                            meta=row['Meta'],
                            upload_id=upload_id  # Adiciona o upload_id único
                        )

                elif 'cis' in file_name:
                    for _, row in df.iterrows():
                        CisControl.objects.create(
                            framework=framework,  
                            idControle=row['# Controle'],
                            controle=row['Controle'],
                            tipoAtivo=row['Tipo de Ativo'],
                            funcao=row['Função'],
                            idSubConjunto=row['# Subconjunto'],
                            subConjunto=row['Subconjunto'],
                            nivel=row['Nível'],
                            resultado=row['Resultado'],
                            comentarios=row['Comentários'],
                            meta=row['Meta'],
                            upload_id=upload_id  # Adiciona o upload_id único
                        )

                # Se o campo is_proprio estiver marcado, salvar em PlanilhaGenerica
                if framework.is_proprio:
                    for _, row in df.iterrows():
                        PlanilhaGenerica.objects.create(
                            framework=framework,  
                            idControle=row['Id Controle*'],
                            controle=row['Controle*'],
                            idSubControle=row['Id Subcontrole'],
                            subControle=row['Subcontrole'],
                            funcaoSeguranca=row['Função de segurança'],
                            tipoAtivo=row['Tipo de Ativo'],
                            informacoesAdicionais=row['Informações Adicionais'],
                            upload_id=upload_id  # Adiciona o upload_id único
                        )

                # Renderiza a página com a URL do arquivo enviado
                uploaded_file_url = framework.excel_file.url
                return render(request, self.template_name, {
                    'form1': MeuModeloForm(),  
                    'uploaded_file_url': uploaded_file_url,
                    'frameworks': MeuModelo.objects.all()  
                })
            else:
                return render(request, self.template_name, {
                    'form1': form1,
                    'error_message': 'Nenhum arquivo foi associado ao framework.',
                    'frameworks': MeuModelo.objects.all()
                })
        else:
            return render(request, self.template_name, {
                'form1': form1,
                'frameworks': MeuModelo.objects.all()  
            })


    # Excluir Framework
    def delete(self, request, id):
        try:
            framework = MeuModelo.objects.get(id=id)
        
            if framework.excel_file: 
                file_path = os.path.join(settings.MEDIA_ROOT, framework.excel_file.name)
                if os.path.isfile(file_path):
                    os.remove(file_path)
            
            framework.delete()
            return JsonResponse({'success': True})
        except MeuModelo.DoesNotExist:
            return JsonResponse({'success': False, 'error': 'Item não encontrado'})

# Editar Framework
def editar_framework(request, id):
    framework = get_object_or_404(MeuModelo, id=id)
    
    if request.method == 'POST':
        form = MeuModeloEditForm(request.POST, request.FILES, instance=framework)
        if form.is_valid():
            # Primeiro, salve a instância para garantir que o novo arquivo é processado
            form.save()
            
            # Verifique se houve alteração no campo de arquivo
            if 'excel_file' in form.changed_data:
                old_file = framework.excel_file
                if old_file and old_file.name:
                    old_file_path = os.path.join(settings.MEDIA_ROOT, old_file.name)
                    if os.path.isfile(old_file_path):
                        os.remove(old_file_path)
            
            return redirect('listar_frameworks')
    else:
        form = MeuModeloEditForm(instance=framework)
    
    # Renderizar a página com o formulário, ou retornar os dados como JSON para preencher o modal
    if request.headers.get('x-requested-with') == 'XMLHttpRequest':
        # Se for uma requisição AJAX, retorna os dados do framework
        return JsonResponse({
            'nome': framework.nome,
            'descricao': framework.descricao,
            'criterio': framework.criterio,
            'uploaded_file_url': framework.excel_file.url if framework.excel_file else None,
            'is_proprio': framework.is_proprio
        })
    else:
        return render(request, 'paginas/framework.html', {'edit_form': form, 'framework': framework})

# Função para renderizar a página assessment.html
class Assessment(View):
    template_name = 'paginas/assessment.html'

    def get(self, request):
        modelos = MeuModelo.objects.all()  # Obtém todos os objetos de MeuModelo
        form1 = NovoAssessmentForm()

        return render(request, self.template_name, {'form1': form1, 'modelos': modelos})

    def post(self, request):
        form1 = NovoAssessmentForm(request.POST, request.FILES)
        if form1.is_valid():
            form1.save()
            return redirect('success')

        modelos = MeuModelo.objects.all()  # Inclui novamente os modelos no caso de erro no formulário
        return render(request, self.template_name, {'form1': form1, 'modelos': modelos})

def assess_cis(request):
    return render(request, 'paginas/assess_cis.html')

def assess_nist(request):
    return render(request, 'paginas/assess_nist.html')

def download_file(request, filename):
    file_path = os.path.join(settings.MEDIA_ROOT, filename)
    if os.path.exists(file_path):
        with open(file_path, 'rb') as fh:
            response = HttpResponse(fh.read(), content_type="application/vnd.ms-excel")
            response['Content-Disposition'] = f'attachment; filename={os.path.basename(file_path)}'
            return response
    raise Http404