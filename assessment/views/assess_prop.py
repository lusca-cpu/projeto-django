from django.conf import settings
from django.shortcuts import render, redirect
from django.utils import timezone
from django.views import View

from datetime import date 

from ..models import FrameworkModel, AssessmentModel, PlanilhaGenericaTemplate, PlanilhaGenericaModel, PlanoAcaoModel

import os
import pandas as pd

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
                comentario = value.strip()

                # Se o comentário for vazio, salve uma string vazia
                prop.comentarios = comentario if comentario else ''
                prop.save()
        elif key.startswith('meta_'):
            prop_id = key.split('_')[1]
            prop = PlanilhaGenericaModel.objects.filter(id=prop_id).first()
            if prop:
                if value in ['Sim', 'Não']:
                    prop.meta = value
                    prop.save()

    # Atualizar a data de upload para a data atual
    assessment.data_upload = timezone.now().date()
    assessment.save()

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
                comentario = value.strip()

                # Se o comentário for vazio, salve uma string vazia
                prop.comentarios = comentario if comentario else ''
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

    update_assessment_file_prop(assessment)
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

    # Atualizar a data de upload para a data atual
    assessment.data_upload = timezone.now().date()
    
    # Salva a instância de AssessmentModel
    assessment.save()

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
        # Se a ação for "Enviar"
        elif action == 'submit':
            process_submit_prop(request, assessment) 

        return redirect('assessment')
# Função para renderizar a página assess_prop.html
class AssessProp(View):
    template_name = 'paginas/assess_prop.html'

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
            process_save_prop(request, assessment) 
        # Se a ação for "Enviar"
        elif action == 'submit':
            process_submit_prop(request, assessment) 

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