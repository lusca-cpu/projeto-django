from django.shortcuts import render, redirect, get_object_or_404
from .forms import MeuModeloForm, MeuModeloEditForm, NovoAssessmentForm
from .models import FrameworkModel, AssessmentModel, PlanilhaGenericaTemplate, PlanilhaGenericaModel, CisModelTemplate, CisModel, IsoModelTemplate, IsoModel, NistModelTemplate, NistModel

from django.views import View
from django.views.generic import TemplateView
from django.views.generic.edit import UpdateView
from django.conf import settings
from django.http import HttpResponse, JsonResponse, HttpResponseRedirect
from django.urls import reverse
from django.template.loader import render_to_string
from django.contrib import messages
import os
import pandas as pd
import plotly.graph_objects as go
from datetime import date


def index(request):
    return render(request, 'paginas/index.html')

def security_assessment(request):
    return render(request, 'paginas/security.html')

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
    framework = get_object_or_404(FrameworkModel, id=id)
    
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

# ========================= FUNÇÕES  ========================= #
# -------- CIS -------- #
# Função quando a pessoa aperta o botão "Salvar" do Cis
def process_save_cis(request, assessment):
    # Filtra os CisModel que estão associados ao assessment atual
    cis_models = CisModel.objects.filter(assessment=assessment)

    # Itera sobre os CisModels filtrados e atualiza os campos
    for key, value in request.POST.items():
        if key.startswith('resultadoCss_'):
            print('entrou')
            cis_id = key.split('_')[1]
            cis = CisModel.objects.filter(id=cis_id).first()
            if cis:
                if value in ['Sim', 'Não']:
                    cis.resultadoCss = value
                    cis.save()
        elif key.startswith('resultadoCl_'):
            cis_id = key.split('_')[1]
            cis = CisModel.objects.filter(id=cis_id).first()
            if cis:
                if value in ['Sim', 'Não']:
                    cis.resultadoCl = value
                    cis.save()
        elif key.startswith('comentarios_'):
            print('entrou')
            cis_id = key.split('_')[1]
            cis = CisModel.objects.filter(id=cis_id).first()
            if cis: 
                cis.comentarios = value
                cis.save()
        elif key.startswith('meta_'):
            cis_id = key.split('_')[1]
            cis = CisModel.objects.filter(id=cis_id).first()
            if cis:
                if value in ['Sim', 'Não']:
                    cis.meta = value
                    cis.save()
    
    update_assessment_file_cis(assessment)
# Função quando a pessoa aperta o botão "Enviar" do Cis
def process_submit_cis(request, assessment):
    cis_models = CisModel.objects.filter(assessment=assessment)

    total_css_sim = 0
    total_css_count = 0
    total_meta_sim = 0
    total_meta_count = 0

    for key, value in request.POST.items():
        if key.startswith('resultadoCss_'):
            cis_id = key.split('_')[1]
            cis = CisModel.objects.filter(id=cis_id).first()
            if cis:
                if value in ['Sim', 'Não']:
                    cis.resultadoCss = value
                    cis.save()
                    # Contagem para o resultado CSS
                    if value == 'Sim':
                        total_css_sim += 1
                    total_css_count += 1
        elif key.startswith('resultadoCl_'):
            cis_id = key.split('_')[1]
            cis = CisModel.objects.filter(id=cis_id).first()
            if cis:
                if value in ['Sim', 'Não']:
                    cis.resultadoCl = value
                    cis.save()
        elif key.startswith('comentarios_'):
            cis_id = key.split('_')[1]
            cis = CisModel.objects.filter(id=cis_id).first()
            if cis: 
                cis.comentarios = value
                cis.save()
        elif key.startswith('meta_'):
            cis_id = key.split('_')[1]
            cis = CisModel.objects.filter(id=cis_id).first()
            if cis:
                if value in ['Sim', 'Não']:
                    cis.meta = value
                    cis.save()
                    # Contagem para a meta
                    if value == 'Sim':
                        total_meta_sim += 1
                    total_meta_count += 1

    if (total_css_sim and total_css_count) > 0:
        resultado_css_percent = (total_css_sim / total_css_count) * 100
    else:
        resultado_css_percent = 0

    if (total_meta_sim and total_meta_count) > 0:
        meta_percent = (total_meta_sim / total_meta_count) * 100
    else:
        meta_percent = 0

    # Atualiza o AssessmentModel com os novos dados
    assessment.status = AssessmentModel.CONCLUIDO  
    assessment.resultado = f"{resultado_css_percent:.2f}%" 
    assessment.meta = f"{meta_percent:.2f}%"

    update_assessment_file_cis(assessment)
# Função para processar o arquivo Excel Cis
def andamento_excel_cis(excel_file, assessment):
    df = pd.read_excel(excel_file)

    # Filtra os CisModel que estão associados ao assessment atual
    cis_models = CisModel.objects.filter(assessment=assessment)

    for cis, (_, row) in zip(cis_models, df.iterrows()):
        # Processa resultado CSS
        if 'ResultadoCss' in row and pd.notna(row['ResultadoCss']):
            cis.resultadoCss = row['ResultadoCss'] if row['ResultadoCss'] in ['Sim', 'Não'] else cis.resultadoCss

        # Processa resultado CL
        if 'ResultadoCl' in row and pd.notna(row['ResultadoCl']):
            cis.resultadoCl = row['ResultadoCl'] if row['ResultadoCl'] in ['Sim', 'Não'] else cis.resultadoCl

        # Processa comentários
        if 'Comentários' in row and pd.notna(row['Comentários']):
            cis.comentarios = row['Comentários']

        # Processa meta
        if 'Meta' in row and pd.notna(row['Meta']):
            cis.meta = row['Meta'] if row['Meta'] in ['Sim', 'Não'] else cis.meta

        # Salva as alterações no banco de dados
        cis.save()

    # Atualiza o arquivo do assessment
    update_assessment_file_cis(assessment)
# Função para processar o arquivo Excel Cis
def concluido_excel_cis(excel_file, assessment):
    # Ler o arquivo Excel usando pandas
    df = pd.read_excel(excel_file)  

    # Inicializar variáveis para contagem
    total_css_sim = 0
    total_css_count = 0
    total_meta_sim = 0
    total_meta_count = 0

    # Iterar sobre as linhas do DataFrame para processar as colunas 'ResultadoCSS' e 'Meta'
    for index, row in df.iterrows():
        # Processar resultado CSS
        resultado_css = row['Resultado (Css)'] 
        if resultado_css in ['Sim', 'Não']:
            if resultado_css == 'Sim':
                total_css_sim += 1
            total_css_count += 1
        
        # Processar meta
        meta = row['Meta'] 
        if meta in ['Sim', 'Não']:
            if meta == 'Sim':
                total_meta_sim += 1
            total_meta_count += 1

    # Calcular as porcentagens
    if (total_css_sim and total_css_count) > 0:
        resultado_css_percent = (total_css_sim / total_css_count) * 100
    else:
        resultado_css_percent = 0

    if (total_meta_sim and total_meta_count) > 0:
        meta_percent = (total_meta_sim / total_meta_count) * 100
    else:
        meta_percent = 0

    # Atualizar o modelo de Assessment com os resultados
    assessment.status = AssessmentModel.CONCLUIDO  
    assessment.resultado = f"{resultado_css_percent:.2f}%" 
    assessment.meta = f"{meta_percent:.2f}%"
    
    assessment.save()

    # Função personalizada para manipular o arquivo final (caso necessário)
    update_assessment_file_cis(assessment)
# Função para criar um arquivo excel do Cis
def update_assessment_file_cis(assessment):
    cis_model = CisModel.objects.filter(assessment=assessment)  # Filtra os CisModel do framework
    data = []
    for cis in cis_model:
        data.append({
            '# Controle': cis.idControle,
            'Controle': cis.controle,
            'Tipo de Ativo': cis.tipoAtivo,
            'Função': cis.funcao,
            '# Subconjunto': cis.idSubConjunto,
            'Subconjunto': cis.subConjunto,
            'Nível': cis.nivel,
            'Resultado (Css)': cis.resultadoCss,
            'Resultado (Cl.)': cis.resultadoCl,
            'Comentários': cis.comentarios,
            'Meta': cis.meta
        })
    df = pd.DataFrame(data)
    data_atual = date.today()
    excel_file_path = f'media/assessments/{assessment.nome}_{data_atual}.xlsx'  # Define o caminho do arquivo
    df.to_excel(excel_file_path, index=False)

    # Atualiza o campo excel_file do AssessmentModel
    with open(excel_file_path, 'rb') as excel_file:
        assessment.excel_file.save(f'{assessment.nome}_{data_atual}.xlsx', excel_file)
    # Remove o arquivo temporário após o upload
    os.remove(excel_file_path)
    # Salva a instância de AssessmentModel
    assessment.save()


# -------- NIST -------- #
# Função quando a pessoa aperta o botão "Salvar" do Nist
def process_save_nist(request, assessment):
        # Filtra os NistModel que estão associados ao assessment atual
        nist_models = NistModel.objects.filter(assessment=assessment)

        for key, value in request.POST.items():
            if key.startswith('notaCss_'):
                nist_id = key.split('_')[1]
                nist = NistModel.objects.filter(id=nist_id).first()
                if nist:
                    nist.notaCss = value
                    nist.save()
            elif key.startswith('notaCl_'):
                nist_id = key.split('_')[1]
                nist = NistModel.objects.filter(id=nist_id).first()
                if nist:
                    nist.notaCl = value
                    nist.save()
            elif key.startswith('comentarios_'):
                nist_id = key.split('_')[1]
                nist = NistModel.objects.filter(id=nist_id).first()
                if nist:
                    nist.comentarios = value
                    nist.save()
            elif key.startswith('meta_'):
                nist_id = key.split('_')[1]
                nist = NistModel.objects.filter(id=nist_id).first()
                if nist:
                    nist.meta = value
                    nist.save()

        update_assessment_file_nist(assessment)
# Função quando a pessoa aperta o botão "Enviar" do Nist
def process_submit_nist(request, assessment):
    nist_models = NistModel.objects.filter(assessment=assessment)

    total_css = 0
    total_css_count = 0
    total_meta = 0
    total_meta_count = 0
    
    for key, value in request.POST.items():
        if key.startswith('notaCss_'):
            nist_id = key.split('_')[1]
            nist = NistModel.objects.filter(id=nist_id).first()
            if nist:
                nist.notaCss = int(value)
                nist.save()
                total_css += nist.notaCss
                total_css_count += 1
        elif key.startswith('notaCl_'):
            nist_id = key.split('_')[1]
            nist = NistModel.objects.filter(id=nist_id).first()
            if nist:
                nist.notaCl = value
                nist.save()
        elif key.startswith('comentarios_'):
            nist_id = key.split('_')[1]
            nist = NistModel.objects.filter(id=nist_id).first()
            if nist:
                nist.comentarios = value
                nist.save()
        elif key.startswith('meta_'):
            nist_id = key.split('_')[1]
            nist = NistModel.objects.filter(id=nist_id).first()
            if nist:
                nist.meta = int(value)
                nist.save()
                total_meta += nist.meta
                total_meta_count += 1

    # Calcula os resultados e atualiza o AssessmentModel
    if (total_css and total_css_count) > 0:
        resultado_css = total_css / total_css_count
    else:
        resultado_css_percent = 0

    if (total_meta and total_meta_count) > 0:
        resultado_meta = total_meta / total_meta_count
    else:
        resultado_meta = 0
    
    # Atualiza o AssessmentModel com os novos dados
    assessment.status = AssessmentModel.CONCLUIDO
    assessment.resultado = f"{resultado_css:.2f}"
    assessment.meta = f"{resultado_meta:.2f}"

    # Atualiza o campo excel_file do AssessmentModel
    update_assessment_file_nist(assessment)

def andamento_excel_nist(excel_file, assessment):
    df = pd.read_excel(excel_file)

    nist_queryset = NistModel.objects.all()
    
    for nist, (_, row) in zip(nist_queryset, df.iterrows()):
        # Processar nota CSS
        if 'NotaCss' in row and pd.notna(row['NotaCss']):
            nist.notaCss = row['NotaCss']  # Atualizar o campo notaCss no modelo
        
        # Processar nota Cl
        if 'NotaCl' in row and pd.notna(row['NotaCl']):
            nist.notaCl = row['NotaCl']  # Atualizar o campo notaCl no modelo
        
        # Processar comentários
        if 'Comentários' in row and pd.notna(row['Comentários']):
            nist.comentarios = row['Comentários']  # Atualizar o campo comentarios no modelo
        
        # Processar meta
        if 'Meta' in row and pd.notna(row['Meta']):
            nist.meta = row['Meta']  # Atualizar o campo meta no modelo
        
        # Salvar as mudanças no banco de dados
        nist.save()

    # Função personalizada para manipular o arquivo final, se necessário
    update_assessment_file_nist(assessment)
# Função para criar um arquivo excel do Nist
def concluido_excel_nist(excel_file, assessment):
    df = pd.read_excel(excel_file)

    total_css = 0
    total_css_count = 0
    total_meta = 0
    total_meta_count = 0

    for index, row in df.iterrows():
        # Processar nota CSS
        nota_css = row['Nota (Css)']  # Nome da coluna no Excel
        if pd.notna(nota_css):  # Verifica se o valor não é NaN
            total_css += int(nota_css)
            total_css_count += 1
        
        # Processar meta
        meta = row['Meta']  # Nome da coluna no Excel
        if pd.notna(meta):  # Verifica se o valor não é NaN
            total_meta += int(meta)
            total_meta_count += 1

    # Calcula os resultados e atualiza o AssessmentModel
    if (total_css and total_css_count) > 0:
        resultado_css = total_css / total_css_count
    else:
        resultado_css_percent = 0

    if (total_meta and total_meta_count) > 0:
        resultado_meta = total_meta / total_meta_count
    else:
        resultado_meta = 0

    assessment.status = AssessmentModel.CONCLUIDO  
    assessment.resultado = f"{resultado_css:.2f}"
    assessment.meta = f"{resultado_meta:.2f}"
    
    assessment.save()

    # Função personalizada para manipular o arquivo final (caso necessário)
    update_assessment_file_nist(assessment)
# Função para criar um arquivo excel do Nist
def update_assessment_file_nist(assessment):
    #Gera e atualiza o arquivo Excel com as informações de NistCsf.
    nist_models = NistModel.objects.filter(assessment=assessment)
    data = []

    for nist in nist_models:
        data.append({
            'Categoria': nist.categoria,
            'Função': nist.funcao,
            'Código': nist.codigo,
            'Subcategoria': nist.subcategoria,
            'Informações adicionais': nist.informacao,
            'Nota (Css)': nist.notaCss,
            'Nota (Cl.)': nist.notaCl,
            'Comentários': nist.comentarios,
            'Meta': nist.meta
        })
    df = pd.DataFrame(data)
    data_atual = date.today()
    excel_file_path = f'media/assessments/{assessment.nome}_{data_atual}.xlsx'
    df.to_excel(excel_file_path, index=False)

    # Atualiza o campo excel_file do AssessmentModel
    with open(excel_file_path, 'rb') as excel_file:
        assessment.excel_file.save(f'{assessment.nome}_{data_atual}.xlsx', excel_file)

    # Remove o arquivo temporário após o upload
    os.remove(excel_file_path)

    # Salva a instância de AssessmentModel
    assessment.save()


# -------- ISO -------- #
# Função quando a pessoa aperta o botão "Salvar" do Iso
def process_save_iso(request, assessment):
    # Filtra os CisModel que estão associados ao assessment atual
    iso_models = IsoModel.objects.filter(assessment=assessment)

    # Itera sobre os IsoModels filtrados e atualiza os campos 
    for key, value in request.POST.items():
        if key.startswith('notaCss_'):
            iso_id = key.split('_')[1]
            iso = IsoModel.objects.filter(id=iso_id).first()
            if iso:
                if value in ['Conforme', 'Parcialmente','Não']:
                    iso.notaCss = value
                    iso.save()
        elif key.startswith('notaCl_'):
            iso_id = key.split('_')[1]
            iso = IsoModel.objects.filter(id=iso_id).first()
            if iso:
                if value in ['Conforme', 'Parcialmente','Não']:
                    iso.notaCl = value
                    iso.save()
        elif key.startswith('comentarios_'):
            iso_id = key.split('_')[1]
            iso = IsoModel.objects.filter(id=iso_id).first()
            if iso:
                iso.comentarios = value
                iso.save()
        elif key.startswith('meta_'):
            iso_id = key.split('_')[1]
            iso = IsoModel.objects.filter(id=iso_id).first()
            if iso:   
                if value in ['Conforme', 'Parcialmente','Não']:
                    iso.meta = value
                    iso.save()

    # Atualiza o campo excel_file do AssessmentModel com os dados atualizados
    update_assessment_file_iso(assessment)
# Função quando a pessoa aperta o botão "Enviar" do Iso
def process_submit_iso(request, assessment):
    iso_models = IsoModel.objects.filter(assessment=assessment)

    total_css_conf = 0
    total_css_count = 0
    total_meta_conf = 0
    total_meta_count = 0

    for key, value in request.POST.items():
        if key.startswith('notaCss_'):
            iso_id = key.split('_')[1]
            iso = IsoModel.objects.filter(id=iso_id).first()
            if iso:
                if value in ['Conforme', 'Parcialmente', 'Não']:
                    iso.notaCss = value
                    iso.save()
                    # Contagem para o nota CSS
                    if value == 'Conforme':
                        total_css_conf += 1
                    total_css_count += 1
        elif key.startswith('notaCl_'):
            iso_id = key.split('_')[1]
            iso = IsoModel.objects.filter(id=iso_id).first()
            if iso:
                if value in ['Conforme', 'Parcialmente', 'Não']:
                    iso.notaCl = value
                    iso.save()
        elif key.startswith('comentarios_'):
            iso_id = key.split('_')[1]
            iso = IsoModel.objects.filter(id=iso_id).first()
            if iso:
                iso.comentarios = value
                iso.save()
        elif key.startswith('meta_'):
            iso_id = key.split('_')[1]
            iso = IsoModel.objects.filter(id=iso_id).first()
            if iso:
                if value in ['Conforme', 'Parcialmente', 'Não']:
                    iso.meta = value
                    iso.save()
                    # Contagem para o resultado CSS
                    if value == 'Conforme':
                        total_meta_conf += 1
                    total_meta_count += 1

    if (total_css_conf and total_css_count) > 0:
        resultado_css_percent = (total_css_conf / total_css_count) * 100
    else:
        resultado_css_percent = 0

    if (total_meta_conf and total_meta_count) > 0:
        meta_percent = (total_meta_conf / total_meta_count) * 100
    else:
        meta_percent = 0

    # Atualiza o AssessmentModel com os novos dados
    assessment.status = AssessmentModel.CONCLUIDO  
    assessment.resultado = f"{resultado_css_percent:.2f}%" 
    assessment.meta = f"{meta_percent:.2f}%"

    # Atualiza o campo excel_file do AssessmentModel
    update_assessment_file_iso(assessment)
# Função para criar um arquivo excel do Iso
def andamento_excel_iso(excel_file, assessment):
    df = pd.read_excel(excel_file)

    # Filtra os IsoModel que estão associados ao assessment atual
    iso_models = IsoModel.objects.filter(assessment=assessment)

    for iso, (_, row) in zip(iso_models, df.iterrows()):
        # Processa nota CSS
        if 'NotaCss' in row and pd.notna(row['NotaCss']):
            iso.notaCss = row['NotaCss'] if row['NotaCss'] in ['Conforme', 'Parcialmente', 'Não'] else iso.notaCss

        # Processa nota CL
        if 'NotaCl' in row and pd.notna(row['NotaCl']):
            iso.notaCl = row['NotaCl'] if row['NotaCl'] in ['Conforme', 'Parcialmente', 'Não'] else iso.notaCl

        # Processa comentários
        if 'Comentários' in row and pd.notna(row['Comentários']):
            iso.comentarios = row['Comentários']

        # Processa meta
        if 'Meta' in row and pd.notna(row['Meta']):
            iso.meta = row['Meta'] if row['Meta'] in ['Conforme', 'Parcialmente', 'Não'] else iso.meta

        # Salva as alterações no banco de dados
        iso.save()

    # Atualiza o arquivo do assessment
    update_assessment_file_iso(assessment)
# Função para criar um arquivo excel do Iso
def concluido_excel_iso(excel_file, assessment):
    df = pd.read_excel(excel_file)

    total_css_conf = 0
    total_css_count = 0
    total_meta_conf = 0
    total_meta_count = 0

    for index, row in df.iterrows():
        # Processar nota CSS
        nota_css = row['Nota (Css)']  
        if nota_css in ['Conforme', 'Parcialmente', 'Não']:
            if nota_css == 'Conforme':
                total_css_conf += 1
            total_css_count += 1
        
        # Processar meta
        meta = row['Meta']  
        if meta in ['Conforme', 'Parcialmente', 'Não']:
            if meta == 'Conforme':
                total_meta_conf += 1
            total_meta_count += 1

    if (total_css_conf and total_css_count) > 0:
        resultado_css_percent = (total_css_conf / total_css_count) * 100
    else:
        resultado_css_percent = 0

    if (total_meta_conf and total_meta_count) > 0:
        meta_percent = (total_meta_conf / total_meta_count) * 100
    else:
        meta_percent = 0

    # Atualiza o AssessmentModel com os novos dados
    assessment.status = AssessmentModel.CONCLUIDO  
    assessment.resultado = f"{resultado_css_percent:.2f}%" 
    assessment.meta = f"{meta_percent:.2f}%"

    # Atualiza o campo excel_file do AssessmentModel
    update_assessment_file_iso(assessment)

# Função para criar um arquivo excel do Iso
def update_assessment_file_iso(assessment):
    iso_models = IsoModel.objects.filter(assessment=assessment)  # Filtra os Iso que estão relacionados do framework
    data = []
    for iso in iso_models:
        data.append({
            'Seção': iso.secao,
            'Cod. Categoria': iso.codCatecoria,
            'Categoria': iso.categoria,
            'Controle': iso.controle,
            'Diretrizes para implementação': iso.diretrizes,
            'Prioridade do controle': iso.prioControle,
            'Nota (Css)': iso.notaCss,
            'Nota (Cl.)': iso.notaCl,
            'Comentários': iso.comentarios,
            'Meta': iso.meta
        })

    # Cria um DataFrame e salva como Excel
    df = pd.DataFrame(data)
    data_atual = date.today()
    excel_file_path = f'media/assessments/{assessment.nome}_{data_atual}.xlsx'  # Define o caminho do arquivo
    df.to_excel(excel_file_path, index=False)

    # Atualiza o campo excel_file do AssessmentModel
    with open(excel_file_path, 'rb') as excel_file:
        assessment.excel_file.save(f'{assessment.nome}_{data_atual}.xlsx', excel_file)

    # Remove o arquivo temporário após o upload
    os.remove(excel_file_path)

    # Salva a instância de AssessmentModel
    assessment.save()


# -------- Framework Proprio -------- #
# Função quando a pessoa aperta o botão "Salvar" do Framework Proprio
def process_save_prop(request, assessment):

    prop_models = PlanilhaGenericaModel.objects.filter(assessment=assessment)

    for key, value in request.POST.items():
        if key.startswith('resultadoCss_'):
            prop_id = key.split('_')[1]
            prop = PlanilhaGenericaModel.objects.filter(id=prop_id).first()
            if prop:
                if value in ['Sim', 'Não']:
                    prop.resultadoCss = value
                    prop.save()
        elif key.startswith('resultadoCl_'):
            prop_id = key.split('_')[1]
            prop = PlanilhaGenericaModel.objects.filter(id=prop_id).first()
            if prop:
                if value in ['Sim', 'Não']:
                    prop.resultadoCl = value
                    prop.save()
        elif key.startswith('comentarios_'):
            prop_id = key.split('_')[1]
            prop = PlanilhaGenericaModel.objects.filter(id=prop_id).first()
            if prop:
                prop.comentarios = value
                prop.save()
        elif key.startswith('meta_'):
            prop_id = key.split('_')[1]
            prop = PlanilhaGenericaModel.objects.filter(id=prop_id).first()
            if prop:
                if value in ['Sim', 'Não']:
                    prop.meta = value
                    prop.save()
    # Atualiza o campo excel_file do AssessmentModel com os dados atualizados
    update_assessment_file_prop(assessment)
# Função quando a pessoa aperta o botão "Enviar" do Framework Proprio
def process_submit_prop(request, assessment):
    prop_generica = PlanilhaGenericaModel.objects.filter(assessment=assessment)

    total_css_sim = 0
    total_css_count = 0
    total_meta_sim = 0
    total_meta_count = 0

    for key, value in request.POST.items():
        if key.startswith('resultadoCss_'):
            prop_id = key.split('_')[1]
            prop = PlanilhaGenericaModel.objects.filter(id=prop_id).first()
            if prop:
                if value in ['Sim', 'Não']:
                    prop.resultadoCss = value
                    prop.save()
                    # Contagem para o resultado CSS
                    if value == 'Sim':
                        total_css_sim += 1
                    total_css_count += 1
        elif key.startswith('resultadoCl_'):
            prop_id = key.split('_')[1]
            prop = PlanilhaGenericaModel.objects.filter(id=prop_id).first()
            if prop:
                if value in ['Sim', 'Não']:
                    prop.resultadoCl = value
                    prop.save()
        elif key.startswith('comentarios_'):
            prop_id = key.split('_')[1]
            prop = PlanilhaGenericaModel.objects.filter(id=prop_id).first()
            if prop:
                prop.comentarios = value
                prop.save()
        elif key.startswith('meta_'):
            prop_id = key.split('_')[1]
            prop = PlanilhaGenericaModel.objects.filter(id=prop_id).first()
            if prop:                
                if value in ['Sim', 'Não']:
                    prop.meta = value
                    prop.save()
                    # Contagem para a meta
                    if value == 'Sim':
                        total_meta_sim += 1
                    total_meta_count += 1

    if (total_css_sim and total_css_count) > 0:
        resultado_css_percent = (total_css_sim / total_css_count) * 100
    else:
        resultado_css_percent = 0

    if (total_meta_sim and total_meta_count) > 0:
        meta_percent = (total_meta_sim / total_meta_count) * 100
    else:
        meta_percent = 0

    # Atualiza o AssessmentModel com os novos dados
    assessment.status = AssessmentModel.CONCLUIDO  
    assessment.resultado = f"{resultado_css_percent:.2f}%" 
    assessment.meta = f"{meta_percent:.2f}%"  

    update_assessment_file_prop(assessment)
# Função para criar um arquivo excel do Framework Proprio
def andamento_excel_prop(excel_file, assessment):
    df = pd.read_excel(excel_file)

    # Filtra os PlanilhaGenericaModel que estão associados ao assessment atual
    prop_models = PlanilhaGenericaModel.objects.filter(assessment=assessment)

    for prop, (_, row) in zip(prop_models, df.iterrows()):
        # Processa resultado CSS
        if 'ResultadoCss' in row and pd.notna(row['ResultadoCss']):
            prop.resultadoCss = row['ResultadoCss'] if row['ResultadoCss'] in ['Sim', 'Não'] else prop.resultadoCss

        # Processa resultado CL
        if 'ResultadoCl' in row and pd.notna(row['ResultadoCl']):
            prop.resultadoCl = row['ResultadoCl'] if row['ResultadoCl'] in ['Sim', 'Não'] else prop.resultadoCl

        # Processa comentários
        if 'Comentários' in row and pd.notna(row['Comentários']):
            prop.comentarios = row['Comentários']

        # Processa meta
        if 'Meta' in row and pd.notna(row['Meta']):
            prop.meta = row['Meta'] if row['Meta'] in ['Sim', 'Não'] else prop.meta

        # Salva as alterações no banco de dados
        prop.save()

    # Atualiza o arquivo do assessment
    update_assessment_file_prop(assessment)
# Função para criar um arquivo excel do Framework Proprio
def concluido_excel_prop(excel_file, assessment):
    df = pd.read_excel(excel_file)

    # Inicializar variáveis para contagem
    total_css_sim = 0
    total_css_count = 0
    total_meta_sim = 0
    total_meta_count = 0

    # Iterar sobre as linhas do DataFrame para processar as colunas 'ResultadoCSS' e 'Meta'
    for index, row in df.iterrows():
        # Processar resultado CSS
        resultado_css = row['Resultado (Css)']
        if resultado_css in ['Sim', 'Não']:
            if resultado_css == 'Sim':
                total_css_sim += 1
            total_css_count += 1
        
        # Processar meta
        meta = row['Meta'] 
        if meta in ['Sim', 'Não']:
            if meta == 'Sim':
                total_meta_sim += 1
            total_meta_count += 1

    # Calcular as porcentagens
    if (total_css_sim and total_css_count) > 0:
        resultado_css_percent = (total_css_sim / total_css_count) * 100
    else:
        resultado_css_percent = 0

    if (total_meta_sim and total_meta_count) > 0:
        meta_percent = (total_meta_sim / total_meta_count) * 100
    else:
        meta_percent = 0

    # Atualizar o modelo de Assessment com os resultados
    assessment.status = AssessmentModel.CONCLUIDO  
    assessment.resultado = f"{resultado_css_percent:.2f}%" 
    assessment.meta = f"{meta_percent:.2f}%"
    
    assessment.save()

    # Função personalizada para manipular o arquivo final (caso necessário)
    update_assessment_file_cis(assessment)
# Função para criar um arquivo excel do Framework Proprio
def update_assessment_file_prop(assessment):
    prop_generica = PlanilhaGenericaModel.objects.filter(assessment=assessment)
    data = []
    for prop in prop_generica:
        data.append({
            'Id Controle*': prop.idControle,
            'Controle*': prop.controle,
            'Id Subcontrole': prop.idSubControle,
            'Subcontrole': prop.subControle,
            'Função de segurança': prop.funcaoSeguranca,
            'Tipo de Ativo': prop.tipoAtivo,
            'Informações Adicionais': prop.informacoesAdicionais,
            'Resultado (Css)': prop.resultadoCss,
            'Resultado (Cl.)': prop.resultadoCl,
            'Comentários': prop.comentarios,
            'Meta': prop.meta
        })
    df = pd.DataFrame(data)
    data_atual = date.today()
    excel_file_path = f'media/assessments/{assessment.nome}_{data_atual}.xlsx'  # Define o caminho do arquivo
    df.to_excel(excel_file_path, index=False)

    # Atualiza o campo excel_file do AssessmentModel
    with open(excel_file_path, 'rb') as excel_file:
        assessment.excel_file.save(f'{assessment.nome}_{data_atual}.xlsx', excel_file)

    # Remove o arquivo temporário após o upload
    os.remove(excel_file_path)
    
    # Salva a instância de AssessmentModel
    assessment.save()


# Class para renderizar a página assessment.html
class Assessment(View):
    template_name = 'paginas/assessment.html'

    def get(self, request):
        frameworks = FrameworkModel.objects.all()  # Obtém todos os objetos de FrameworkModel
        assessments = AssessmentModel.objects.all()  # Obtém todos os objetos de AssessmentModel
        form1 = NovoAssessmentForm()

        return render(request, self.template_name, {
            'form1': form1,
            'frameworks': frameworks,
            'assessments': assessments
        })

    def post(self, request):
        form1 = NovoAssessmentForm(request.POST, request.FILES)
        if form1.is_valid():
            # Salva o formulário e obtém a instância salva
            form1.save()
            frameworks = FrameworkModel.objects.all()
            assessment = form1.instance  # Obtém a instância recém-criada ou editada
            framework = assessment.framework  # Obtém o framework associado ao assessment
            nome_framework = framework.nome.lower() 

            excel_file = request.FILES.get('excel_file')

            if excel_file:
                df = pd.read_excel(excel_file)

                # Verifica o nome do framework e o status para chamar a função correta
                if "nist" in nome_framework:  # Função para salvar os dados do NIST
                    for _, row in df.iterrows():
                        NistModel.objects.create(
                            assessment=assessment, 
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
                    if assessment.status == 'Andamento':  # Corrigido de 'staus' para 'status'
                        andamento_excel_nist(excel_file, assessment)
                    elif assessment.status == 'Concluído':
                        concluido_excel_nist(excel_file, assessment)

                elif "iso" in nome_framework:  # Função para salvar os dados do Iso
                    for _, row in df.iterrows():
                        IsoModel.objects.create(
                            assessment=assessment,
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
                    if assessment.status == 'Andamento':
                        andamento_excel_iso(excel_file, assessment)
                    elif assessment.status == 'Concluído':
                        concluido_excel_iso(excel_file, assessment)

                elif "cis" in nome_framework:
                    # Função para salvar os dados do Cis
                    for _, row in df.iterrows():
                        CisModel.objects.create(
                            assessment=assessment,  
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
                    if assessment.status == 'Andamento':
                        andamento_excel_cis(excel_file, assessment)
                    elif assessment.status == 'Concluído':
                        concluido_excel_cis(excel_file, assessment)

                elif framework.is_proprio:  # Função para salvar os dados do Framework Próprio
                    for _, row in df.iterrows():
                        PlanilhaGenericaModel.objects.create(
                            assessment=assessment,  
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
                    if assessment.status == 'Andamento':
                        andamento_excel_prop(excel_file, assessment)
                    elif assessment.status == 'Concluído':
                        concluido_excel_prop(excel_file, assessment)

            return redirect('assessment')
        else:
            frameworks = FrameworkModel.objects.all()  # Obtém os frameworks novamente no caso de erro
            assessments = AssessmentModel.objects.all()  # Obtém os assessments novamente no caso de erro
            return render(request, self.template_name, {
                'form1': form1,
                'frameworks': frameworks,
                'assessments': assessments
            })


    # Excluir Assessment
    def delete(self, request, id):
        try:
            assessment = AssessmentModel.objects.get(id=id)
        
            if assessment.excel_file: 
                file_path = os.path.join(settings.MEDIA_ROOT, assessment.excel_file.name)
                if os.path.isfile(file_path):
                    os.remove(file_path)
            
            assessment.delete()
            return JsonResponse({'success': True})
        except AssessmentModel.DoesNotExist:
            return JsonResponse({'success': False, 'error': 'Item não encontrado'})

# Redirecionar para o Framework para fazer a primeira avaliação
class RedirecionarFramework(View):
    def get(self, request, id):
        try:
            # Obtém o framework específico
            framework = FrameworkModel.objects.get(id=id)
        except FrameworkModel.DoesNotExist:
            # Se o framework não for encontrado, redireciona para a página de assessment
            return redirect('assessment')

        # Verifica o nome do arquivo Excel
        excel_name = framework.excel_file.name.lower()

        # Redireciona para a página de avaliação correta
        if 'nist' in excel_name:
            return redirect('assess_nist_up', id=framework.id)
        elif 'cis' in excel_name:
            return redirect('assess_cis_up', id=framework.id)
        elif 'iso' in excel_name:
            return redirect('assess_iso_up', id=framework.id)
        elif framework.is_proprio:
            return redirect('assess_prop_up', id=framework.id)
        else:
            # Se nenhuma condição for atendida, retorna para a página principal de assessment
            return redirect('assessment')
# Redirecionar para o Framework para vizualizar 
class RedirecionarFramework2(View):
    def get(self, request, id):
        try:
            # Obtém o assessment específico
            assessment = AssessmentModel.objects.get(id=id)
        except AssessmentModel.DoesNotExist:
            # Se o assessment não for encontrado, redireciona para a página de assessment
            return redirect('assessment')

        # Verifica o nome do arquivo Excel
        excel_name = assessment.excel_file.name.lower()

        # Redireciona para a página de avaliação correta
        if 'nist' in excel_name:
            return redirect('assess_nist', id=assessment.id)
        elif 'cis' in excel_name:
            return redirect('assess_cis', id=assessment.id)
        elif 'iso' in excel_name:
            return redirect('assess_iso', id=assessment.id)
        elif assessment.framework.is_proprio:
            return redirect('assess_prop', id=assessment.id)
        else:
            # Se nenhuma condição for atendida, retorna para a página principal de assessment
            return redirect('assessment')


# Class para renderizar a página assess_cis_up.html
class AssessCisUpload(View):
    template_name = 'paginas/assess_cis_up.html'

    def get(self, request, id):
        # Obtém o framework específico
        framework = FrameworkModel.objects.get(id=id)

        # Cria um novo AssessmentModel
        assessment = AssessmentModel.objects.create(
            framework=framework,
            nome=framework.nome,
            status=AssessmentModel.ANDAMENTO,
            resultado="",
            meta=""
        )
        # Atualiza o AssessmentModel com o arquivo enviado, se houver
        if request.FILES.get('excel_file'):
            assessment.excel_file = request.FILES.get('excel_file')
            assessment.save()
        
        cis_models = []
        # Cria novas instâncias de CisModel com base no template
        cis_uploads = CisModelTemplate.objects.filter(framework=framework)
        for upload in cis_uploads:
            cis = CisModel.objects.create(
                assessment=assessment,
                idControle=upload.idControle,
                controle=upload.controle,
                tipoAtivo=upload.tipoAtivo,
                funcao=upload.funcao,
                idSubConjunto=upload.idSubConjunto,
                subConjunto=upload.subConjunto,
                nivel=upload.nivel,
                resultadoCss=upload.resultadoCss,
                resultadoCl=upload.resultadoCl,
                comentarios=upload.comentarios,
                meta=upload.meta
            )
            cis_models.append(cis)

        # Envia os novos CisModel criados para o template
        return render(request, self.template_name, {
            'assessment': assessment,
            'cis_models': cis_models,
            'assessment_id': assessment.id,  # Passando as novas instâncias
        })

    def post(self, request, id):
        try:
            assessment = AssessmentModel.objects.get(id=id)
        except AssessmentModel.DoesNotExist:
            # Caso não exista, você pode retornar uma mensagem de erro ou redirecionar para outra página
            return redirect('assessment_not_found')  # Crie uma view para tratar esse caso, se desejar

        # Processar as ações com base no botão clicado
        action = request.POST.get('action')

        # Se a ação for "Salvar"
        if action == 'save':
            process_save_cis(request, assessment) 

        elif action == 'submit':
            process_submit_cis(request, assessment) 

        return redirect('assessment')
# Função para renderizar a página assess_cis.html
class AssessCis(View):
    template_name = 'paginas/assess_cis.html'

    def get(self, request, id):

        assessment = AssessmentModel.objects.get(id=id)
        cis_models = CisModel.objects.filter(assessment=assessment)

        return render(request, self.template_name, {
            'assessment': assessment,
            'cis_models': cis_models,
            'assessment_id': id
        })

    def post(self, request, id):
        try:
            assessment = AssessmentModel.objects.get(id=id)   
        except AssessmentModel.DoesNotExist:
            # Caso não exista, você pode retornar uma mensagem de erro ou redirecionar para outra página
            return redirect('assessment_not_found')  # Crie uma view para tratar esse caso, se desejar

        # Processar as ações com base no botão clicado
        action = request.POST.get('action')

        # Se a ação for "Salvar"
        if action == 'save':
            process_save_cis(request, assessment) 

        elif action == 'submit':
            process_submit_cis(request, assessment) 

        return redirect('assessment')


# Função para renderizar a página assess_nist_up.html
class AssessNistUpload(View):
    template_name = 'paginas/assess_nist_up.html'

    def get(self, request, id):
        # Obtém o framework (FrameworkModel) específico com base no ID
        framework = FrameworkModel.objects.get(id=id)

        # Cria um novo AssessmentModel
        assessment = AssessmentModel.objects.create(
            framework=framework,
            nome=framework.nome,
            status=AssessmentModel.ANDAMENTO,
            resultado="",
            meta=""
        )
        # Atualiza o AssessmentModel com o arquivo enviado, se houver
        if request.FILES.get('excel_file'):
            assessment.excel_file = request.FILES.get('excel_file')
            assessment.save()
        
        nist_models = []
        # Cria novas instâncias de NistModel com base no template
        nist_uploads = NistModelTemplate.objects.filter(framework=framework)
        for upload in nist_uploads:
            nist = NistModel.objects.create(
                assessment=assessment,
                categoria=upload.categoria,
                funcao=upload.funcao,
                codigo=upload.codigo,
                subcategoria=upload.subcategoria,
                informacao=upload.informacao,
                notaCss=upload.notaCss,
                notaCl=upload.notaCl,
                comentarios=upload.comentarios,
                meta=upload.meta,
            )
            nist_models.append(nist)
        # Notas disponíveis para selecionar
        notas = range(0, 6)

        return render(request, self.template_name, {
            'assessment': assessment,
            'nist_models': nist_models,
            'notas': notas,
            'assessment_id': assessment.id
        })

    def post(self, request, id):
        try:
            assessment = AssessmentModel.objects.get(id=id)
        except AssessmentModel.DoesNotExist:
            # Caso não exista, você pode retornar uma mensagem de erro ou redirecionar para outra página
            return redirect('assessment_not_found')  # Crie uma view para tratar esse caso, se desejar

        # Processar as ações com base no botão clicado
        action = request.POST.get('action')

        # Se a ação for "Salvar"
        if action == 'save':
            process_save_nist(request, assessment) 

        elif action == 'submit':
            process_submit_nist(request, assessment) 

        return redirect('assessment')
# Função para renderizar a página assess_nist.html
class AssessNist(View):
    template_name = 'paginas/assess_nist.html'

    def get(self, request, id):
        assessment = AssessmentModel.objects.get(id=id)
        nist_models = NistModel.objects.filter(assessment=assessment)
        notas = range(0, 6)

        return render(request, self.template_name, {
            'assessment': assessment,
            'nist_models': nist_models,
            'notas': notas,
            'assessment_id': assessment.id
        })

    def post(self, request, id):
        try:
            assessment = AssessmentModel.objects.get(id=id)
        except AssessmentModel.DoesNotExist:
            # Caso não exista, você pode retornar uma mensagem de erro ou redirecionar para outra página
            return redirect('assessment_not_found')  # Crie uma view para tratar esse caso, se desejar

        # Processar as ações com base no botão clicado
        action = request.POST.get('action')

        # Se a ação for "Salvar"
        if action == 'save':
            process_save_nist(request, assessment) 

        elif action == 'submit':
            process_submit_nist(request, assessment) 

        return redirect('assessment')


# Função para renderizar a página assess_iso_up.html
class AssessIsoUpload(View):
    template_name = 'paginas/assess_iso_up.html'

    def get(self, request, id):
        # Obtém o framework específico
        framework = FrameworkModel.objects.get(id=id)

        # Cria um novo AssessmentModel
        assessment = AssessmentModel.objects.create(
            framework=framework,
            nome=framework.nome,
            status=AssessmentModel.ANDAMENTO,
            resultado="",
            meta=""
        )
        # Atualiza o AssessmentModel com o arquivo enviado, se houver
        if request.FILES.get('excel_file'):
            assessment.excel_file = request.FILES.get('excel_file')
            assessment.save()

        iso_models = []
        # Cria novas instâncias de IsoModel com base no template
        iso_uploads = IsoModelTemplate.objects.filter(framework=framework)
        for upload in iso_uploads:
            iso = IsoModel.objects.create(
                assessment=assessment, 
                secao=upload.secao,
                codCatecoria=upload.codCatecoria,
                categoria=upload.categoria,
                controle=upload.controle,
                diretrizes=upload.diretrizes,
                prioControle=upload.prioControle,
                notaCss=upload.notaCss,
                notaCl=upload.notaCl,
                comentarios=upload.comentarios,
                meta=upload.meta,
            )
            iso_models.append(iso)

        return render(request, self.template_name, {
            'assessment': assessment,
            'iso_models': iso_models,
            'assessment_id': assessment.id  # Passa o ID do assessment
        })

    def post(self, request, id):
        try:
            assessment = AssessmentModel.objects.get(id=id)
        except AssessmentModel.DoesNotExist:
            print(f"AssessmentModel com ID {id} não existe")
            return redirect('assessment_not_found')

        # Processar as ações com base no botão clicado
        action = request.POST.get('action')

        # Se a ação for "Salvar"
        if action == 'save':
            process_save_iso(request, assessment) 
        # Se a ação for "Enviar"
        elif action == 'submit':
            process_submit_iso(request, assessment) 

        return redirect('assessment')
# Função para renderizar a página assess_iso.html
class AssessIso(View):
    template_name = 'paginas/assess_iso.html'

    def get(self, request, id):
        # Obtém o framework específico 
        assessment = AssessmentModel.objects.get(id=id)
        # Cria novas instâncias de IsoModel com base no template
        iso_models = IsoModel.objects.filter(assessment=assessment)
        # Cria uma lista de notas para preencher os campos de notas CSS e CL

        return render(request, self.template_name, {
            'assessment': assessment,
            'iso_models': iso_models,
            'assessment_id': id  # Passa o ID do framework
        })

    def post(self, request, id):
        try:
            # Tenta buscar a instância de AssessmentModel com base no id fornecido
            assessment = AssessmentModel.objects.get(id=id)
        except AssessmentModel.DoesNotExist:
            # Caso não exista, você pode retornar uma mensagem de erro ou redirecionar para outra página
            return redirect('assessment_not_found')  # Crie uma view para tratar esse caso, se desejar

        # Processar as ações com base no botão clicado
        action = request.POST.get('action')

        # Se a ação for "Salvar"
        if action == 'save':
            process_save_iso(request, assessment) 

        elif action == 'submit':
            process_submit_iso(request, assessment) 

        return redirect('assessment')
   

# Função para renderizar a página assess_prop_up.html
class AssessPropUpload(View):
    template_name = 'paginas/assess_prop_up.html'

    def get(self, request, id):
        # # Obtém o framework específico
        framework = FrameworkModel.objects.get(id=id)

        # Cria um novo AssessmentModel
        assessment = AssessmentModel.objects.create(
            framework=framework,
            nome=framework.nome,
            status=AssessmentModel.ANDAMENTO,
            resultado="",
            meta=""
        )
        # Atualiza o AssessmentModel com o arquivo enviado, se houver
        if request.FILES.get('excel_file'):
            assessment.excel_file = request.FILES.get('excel_file')
            assessment.save()

        prop_models = []
        prop_uploads = PlanilhaGenericaTemplate.objects.filter(framework=framework)
        for upload in prop_uploads:
            prop = PlanilhaGenericaModel.objects.create(
                assessment=assessment,
                idControle=upload.idControle,
                controle=upload.controle,
                idSubControle=upload.idSubControle,
                subControle=upload.subControle,
                funcaoSeguranca=upload.funcaoSeguranca,
                tipoAtivo=upload.tipoAtivo,
                informacoesAdicionais=upload.informacoesAdicionais,
                resultadoCss=upload.resultadoCss,
                resultadoCl=upload.resultadoCl,
                comentarios=upload.comentarios,
                meta=upload.meta,
            )
            prop_models.append(prop)

        return render(request, self.template_name, {
            'assessment': assessment,
            'prop_models': prop_models,
            'assessment_id': assessment.id
        })

    def post(self, request, id):
        try:
            # Tenta buscar a instância de AssessmentModel com base no id fornecido
            assessment = AssessmentModel.objects.get(id=id)
        except AssessmentModel.DoesNotExist:
            # Caso não exista, você pode retornar uma mensagem de erro ou redirecionar para outra página
            return redirect('assessment_not_found')  # Crie uma view para tratar esse caso, se desejar

        # Processar as ações com base no botão clicado
        action = request.POST.get('action')

        # Se a ação for "Salvar"
        if action == 'save':
            process_save_prop(request, assessment) 

        elif action == 'submit':
            process_submit_prop(request, assessment) 

        return redirect('assessment')
# Função para renderizar a página assess_prop.html
class AssessProp(View):
    template_name = 'paginas/assess_prop_up.html'

    def get(self, request, id):
        # Obtém o framework específico
        assessment = AssessmentModel.objects.get(id=id)
        prop_models = PlanilhaGenericaModel.objects.filter(assessment=assessment)

        return render(request, self.template_name, {
            'assessment': assessment,
            'prop_models': prop_models,
            'assessment_id': id
        })

    def post(self, request, id):
        try:
            # Tenta buscar a instância de AssessmentModel com base no id fornecido
            assessment = AssessmentModel.objects.get(id=id)
        except AssessmentModel.DoesNotExist:
            # Caso não exista, você pode retornar uma mensagem de erro ou redirecionar para outra página
            return redirect('assessment_not_found')  # Crie uma view para tratar esse caso, se desejar

        # Processar as ações com base no botão clicado
        action = request.POST.get('action')

        # Se a ação for "Salvar"
        if action == 'save':
            self.process_save(request, assessment) 

        elif action == 'submit':
            self.process_submit(request, assessment) 

        return redirect('assessment')


    def process_save(self, request, assessment):

        prop_models = PlanilhaGenericaModel.objects.filter(assessment=assessment)

        for key, value in request.POST.items():
            if key.startswith('resultadoCss_'):
                prop_id = key.split('_')[1]
                prop = PlanilhaGenericaModel.objects.filter(id=prop_id).first()
                if prop:
                    if value in ['Sim', 'Não']:
                        prop.resultadoCss = value
                        prop.save()
            elif key.startswith('resultadoCl_'):
                prop_id = key.split('_')[1]
                prop = PlanilhaGenericaModel.objects.filter(id=prop_id).first()
                if prop:
                    if value in ['Sim', 'Não']:
                        prop.resultadoCl = value
                        prop.save()
            elif key.startswith('comentarios_'):
                prop_id = key.split('_')[1]
                prop = PlanilhaGenericaModel.objects.filter(id=prop_id).first()
                if prop:
                    prop.comentarios = value
                    prop.save()
            elif key.startswith('meta_'):
                prop_id = key.split('_')[1]
                prop = PlanilhaGenericaModel.objects.filter(id=prop_id).first()
                if prop:
                    if value in ['Sim', 'Não']:
                        prop.meta = value
                        prop.save()
        # Atualiza o campo excel_file do AssessmentModel com os dados atualizados
        self.update_assessment_file(assessment)

    def process_submit(self, request, assessment):
        prop_generica = PlanilhaGenericaModel.objects.filter(assessment=assessment)

        total_css_sim = 0
        total_css_count = 0
        total_meta_sim = 0
        total_meta_count = 0

        for key, value in request.POST.items():
            if key.startswith('resultadoCss_'):
                prop_id = key.split('_')[1]
                prop = PlanilhaGenericaModel.objects.filter(id=prop_id).first()
                if prop:
                    if value in ['Sim', 'Não']:
                        prop.resultadoCss = value
                        prop.save()
                        # Contagem para o resultado CSS
                        if value == 'Sim':
                            total_css_sim += 1
                        total_css_count += 1
            elif key.startswith('resultadoCl_'):
                prop_id = key.split('_')[1]
                prop = PlanilhaGenericaModel.objects.filter(id=prop_id).first()
                if prop:
                    if value in ['Sim', 'Não']:
                        prop.resultadoCl = value
                        prop.save()
            elif key.startswith('comentarios_'):
                prop_id = key.split('_')[1]
                prop = PlanilhaGenericaModel.objects.filter(id=prop_id).first()
                if prop:
                    prop.comentarios = value
                    prop.save()
            elif key.startswith('meta_'):
                prop_id = key.split('_')[1]
                prop = PlanilhaGenericaModel.objects.filter(id=prop_id).first()
                if prop:                
                    if value in ['Sim', 'Não']:
                        prop.meta = value
                        prop.save()
                        # Contagem para a meta
                        if value == 'Sim':
                            total_meta_sim += 1
                        total_meta_count += 1
    
        if (total_css_sim and total_css_count) > 0:
            resultado_css_percent = (total_css_sim / total_css_count) * 100
        else:
            resultado_css_percent = 0

        if (total_meta_sim and total_meta_count) > 0:
            meta_percent = (total_meta_sim / total_meta_count) * 100
        else:
            meta_percent = 0

        # Atualiza o AssessmentModel com os novos dados
        assessment.status = AssessmentModel.CONCLUIDO  
        assessment.resultado = f"{resultado_css_percent:.2f}%" 
        assessment.meta = f"{meta_percent:.2f}%"  

        self.update_assessment_file(assessment)

    def update_assessment_file(self, assessment):
        prop_generica = PlanilhaGenericaModel.objects.filter(assessment=assessment)
        data = []
        for prop in prop_generica:
            data.append({
                'Id Controle': prop.idControle,
                'Controle': prop.controle,
                'Id Subconjunto': prop.idSubControle,
                'Subconjunto': prop.subControle,
                'Função de Segurança': prop.funcaoSeguranca,
                'Tipo de Ativo': prop.tipoAtivo,
                'Informações Adicionais': prop.informacoesAdicionais,
                'Resultado CSS': prop.resultadoCss,
                'Resultado CL': prop.resultadoCl,
                'Comentários': prop.comentarios,
                'Meta': prop.meta
            })
        df = pd.DataFrame(data)
        data_atual = date.today()
        excel_file_path = f'media/assessments/{assessment.nome}_{data_atual}.xlsx'  # Define o caminho do arquivo
        df.to_excel(excel_file_path, index=False)

        # Atualiza o campo excel_file do AssessmentModel
        with open(excel_file_path, 'rb') as excel_file:
            assessment.excel_file.save(f'{assessment.nome}_{data_atual}.xlsx', excel_file)

        # Remove o arquivo temporário após o upload
        os.remove(excel_file_path)
        
        # Salva a instância de AssessmentModel
        assessment.save()


# Função para renderizar a página planodeacao.html
class PlanodeAcao(View):
    template_name = 'paginas/plano_acao.html'

    def get(self, request):
        return render(request, self.template_name)


# Função para renderizar a página painelderesultados.html
class PaineldeResultados(View):
    template_name = 'paginas/painel_result.html'
    # Grafico de linha
    def get(self, request):
        # Dados de exemplo
        velocidade = [10, 15, 20, 25, 30, 35, 40]
        tempo = [0, 1, 2, 3, 4, 5, 6]

        # Criar o gráfico de linha eixos x e y
        fig_linha = go.Figure(data=go.Scatter(x=velocidade, y=tempo, mode='lines+markers'))
        fig_linha.update_layout(title='Gráfico de linha',
                            xaxis_title='Velocidade (km/h)',
                            yaxis_title='Tempo (s)')

        # Converter o gráfico para HTML
        grafico_linha_html = fig_linha.to_html(full_html=False)
        
        # Grafico velocimetro
        fig_velocimetro = go.Figure(go.Indicator( 
            mode="gauge+number",
            value=70,  
            title={'text': "Velocimetro"},
            number={'font': {'color': "blue", 'size': 30}},
            gauge={ 
                'axis': {'range': [0, 100], 'tickcolor': "blue"},
                'bar': {'color': "darkblue"},
                'bordercolor': "white",
                'steps': [  # partes
                    {'range': [0, 50], 'color': "LightBlue"},
                    {'range': [50, 100], 'color': "RoyalBlue"}
                ],
                'threshold': {  # limiar
                    'line': {'color': "red", 'width': 4},
                    'thickness': 0.80,
                    'value': 90}
            }
        ))

        # Converter o gráfico para HTML
        grafico_velocimetro_html = fig_velocimetro.to_html(full_html=False)

        # Grafico pizza
        regioes = ['norte', 'sul', 'leste', 'oeste']
        populacao = [1000, 20000, 50000, 100000]
        cormarcador = ["DarkBlue", "RoyalBlue", "blue", "LightBlue"]

        fig_pizza = go.Figure(data=go.Pie(labels=regioes,
                                      values=populacao,
                                      marker_colors=cormarcador,
                                      hole=0.5, # furo do centro do grafico
                                      pull=[0, 0, 0.15, 0])) # distancia entre fatias

        # Rótulos
        fig_pizza.update_traces(textposition="outside", textinfo="percent+label")

        # Legenda
        fig_pizza.update_layout(legend_title_text="Regiões brasileiras",
                            legend=dict(orientation="h",
                                        xanchor="center",
                                        x=0.5))

        # Texto
        fig_pizza.update_layout(annotations=[dict(text="População",
                                              x=0.5,
                                              y=0.5,
                                              font_size=18,
                                              showarrow=False)])

        # Converter o gráfico para HTML
        grafico_pizza_html = fig_pizza.to_html(full_html=False)
        #fig.show() 

        context = {
            'grafico_linha': grafico_linha_html,
            'grafico_velocimetro': grafico_velocimetro_html,
            'grafico_pizza': grafico_pizza_html,
        }

        return render(request, self.template_name, context)


# Função dedicada pra realizar os downloads dos arquivos
def download_file(request, filename):
    file_path = os.path.join(settings.MEDIA_ROOT, filename)
    if os.path.exists(file_path):
        with open(file_path, 'rb') as fh:
            response = HttpResponse(fh.read(), content_type="application/vnd.ms-excel")
            response['Content-Disposition'] = f'attachment; filename={os.path.basename(file_path)}'
            return response
    raise Http404