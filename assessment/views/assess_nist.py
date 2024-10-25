from django.conf import settings
from django.shortcuts import render, redirect
from django.utils import timezone
from django.views import View

from datetime import date 

from ..models import FrameworkModel, AssessmentModel, NistModelTemplate, NistModel, PlanoAcaoModel

import os
import pandas as pd

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
                    comentario = value.strip()

                    # Se o comentário for vazio, salve uma string vazia
                    nist.comentarios = comentario if comentario else ''
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
                nist.notaCl = int(value)
                nist.save()
        elif key.startswith('comentarios_'):
            nist_id = key.split('_')[1]
            nist = NistModel.objects.filter(id=nist_id).first()
            if nist:
                comentario = value.strip()

                # Se o comentário for vazio, salve uma string vazia
                nist.comentarios = comentario if comentario else ''
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

    # Atualizar a data de upload para a data atual
    assessment.data_upload = timezone.now().date()
    assessment.save()

    plano_acao = PlanoAcaoModel.objects.create(
        assessment=assessment,  # ForeignKey para AssessmentModel
        data_assess=assessment.data_upload,  # Usar a data do AssessmentModel
        nome=assessment.nome,  # Mesmo nome do Assessment
        acoes_cad=0,  # Valor inicial
        custo_estimado=0,  # Valor inicial
        conclusao=0,  # Valor inicial
        status=PlanoAcaoModel.INICIAR  # Definindo o status como "Iniciar"
    )

    # Atualiza o campo excel_file do AssessmentModel
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

    # Atualizar a data de upload para a data atual
    assessment.data_upload = timezone.now().date()

    # Salva a instância de AssessmentModel
    assessment.save()

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
        # Se a ação for "Enviar"
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
        # Se a ação for "Enviar"
        elif action == 'submit':
            process_submit_nist(request, assessment) 

        return redirect('assessment')

# Função dedicada pra realizar os downloads dos arquivos
def download_file(request, filename):
    file_path = os.path.join(settings.MEDIA_ROOT, filename)
    if os.path.exists(file_path):
        with open(file_path, 'rb') as fh:
            response = HttpResponse(fh.read(), content_type="application/vnd.ms-excel")
            response['Content-Disposition'] = f'attachment; filename={os.path.basename(file_path)}'
            return response
    raise Http404