from django.conf import settings
from django.shortcuts import render, redirect
from django.utils import timezone
from django.views import View

from datetime import date 

from ..models import FrameworkModel, AssessmentModel, CisModelTemplate, CisModel, PlanoAcaoModel

import os
import pandas as pd

# Função quando a pessoa aperta o botão "Salvar" do Cis
def process_save_cis(request, assessment):
    # Filtra os CisModel que estão associados ao assessment atual
    cis_models = CisModel.objects.filter(assessment=assessment)

    # Itera sobre os CisModels filtrados e atualiza os campos
    for key, value in request.POST.items():
        if key.startswith('resultadoCss_'):
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
            cis_id = key.split('_')[1]
            cis = CisModel.objects.filter(id=cis_id).first()
            if cis:
                comentario = value.strip()

                # Se o comentário for vazio, salve uma string vazia
                cis.comentarios = comentario if comentario else ''
                cis.save()
        elif key.startswith('meta_'):
            cis_id = key.split('_')[1]
            cis = CisModel.objects.filter(id=cis_id).first()
            if cis:
                if value in ['Sim', 'Não']:
                    cis.meta = value
                    cis.save()

    # Atualizar a data de upload para a data atual
    assessment.data_upload = timezone.now().date()
    assessment.save()
    
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
                comentario = value.strip()

                # Se o comentário for vazio, salve uma string vazia
                cis.comentarios = comentario if comentario else ''
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

    # Atualizar a data de upload para a data atual
    assessment.data_upload = timezone.now().date()

    # Salva a instância de AssessmentModel
    assessment.save()

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
        # Se a ação for "Enviar"
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
        # Se a ação for "Enviar"
        elif action == 'submit':
            process_submit_cis(request, assessment) 

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
