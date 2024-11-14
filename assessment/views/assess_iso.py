from django.conf import settings
from django.shortcuts import render, redirect
from django.utils import timezone
from django.views import View

from datetime import date 

from ..models import FrameworkModel, AssessmentModel, IsoModelTemplate, IsoModel, PlanoAcaoModel

import os
import pandas as pd

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
                comentario = value.strip()

                # Se o comentário for vazio, salve uma string vazia
                iso.comentarios = comentario if comentario else ''
                iso.save()
        elif key.startswith('meta_'):
            iso_id = key.split('_')[1]
            iso = IsoModel.objects.filter(id=iso_id).first()
            if iso:   
                if value in ['Conforme', 'Parcialmente','Não']:
                    iso.meta = value
                    iso.save()

    # Atualizar a data de upload para a data atual
    assessment.data_upload = timezone.now().date()
    assessment.save()

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
                comentario = value.strip()

                # Se o comentário for vazio, salve uma string vazia
                iso.comentarios = comentario if comentario else ''
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

    # Atualizar a data de upload para a data atual
    assessment.data_upload = timezone.now().date()

    # Salva a instância de AssessmentModel
    assessment.save()

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
        # Se a ação for "Enviar"
        elif action == 'submit':
            process_submit_iso(request, assessment) 

        return redirect('assessment')

# Função dedicada pra realizar os downloads dos arquivos
def download_file(request, filename):
    file_path = os.path.join(settings.MEDIA_ROOT, filename)
    if os.path.exists(file_path):
        with open(file_path, 'rb') as fh:
            response = HttpResponse(fh.read(), content_type="application/vnd.ms-excel")
            response['Content-Disposition'] = f'attachment; filename={os.path.basename(file_path)}'
            return response
    raise Http404v