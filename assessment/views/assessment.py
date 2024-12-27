from django.conf import settings
from django.http import HttpResponse, JsonResponse
from django.shortcuts import render, redirect
from django.utils import timezone
from django.views import View

from datetime import date

from ..forms import NovoAssessmentForm
from ..models import FrameworkModel, AssessmentModel, CisModel, IsoModel, NistModel, PlanilhaGenericaModel, PlanoAcaoModel

import os
import pandas as pd

# -------- CIS -------- #
# Função para processar o arquivo Excel Cis
def andamento_excel_cis(excel_file, assessment):
    df = pd.read_excel(excel_file)

    # Filtra os CisModel que estão associados ao assessment atual
    cis_models = CisModel.objects.filter(assessment=assessment)

    for cis, (_, row) in zip(cis_models, df.iterrows()):
        # Processa resultado CSS
        if 'ResultadoCss' in row and pd.notna(row['ResultadoCss']):
            cis.resultadoCss = row['ResultadoCss'] if row['ResultadoCss'] in ['Aderente', 'Não Aderente'] else cis.resultadoCss

        # Processa resultado CL
        if 'ResultadoCl' in row and pd.notna(row['ResultadoCl']):
            cis.resultadoCl = row['ResultadoCl'] if row['ResultadoCl'] in ['Aderente', 'Não Aderente'] else cis.resultadoCl

        # Processa comentários
        if 'Comentários' in row and pd.notna(row['Comentários']):
            cis.comentarios = row['Comentários']

        # Processa meta
        if 'Meta' in row and pd.notna(row['Meta']):
            cis.meta = row['Meta'] if row['Meta'] in ['Aderente', 'Não Aderente'] else cis.meta

        # Atualizar a data de upload para a data atual
        assessment.data_upload = timezone.now().date()
        assessment.save()

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
        if resultado_css in ['Aderente', 'Não Aderente']:
            if resultado_css == 'Aderente':
                total_css_sim += 1
            total_css_count += 1

        # Processa resultado CL
        if 'ResultadoCl' in row and pd.notna(row['ResultadoCl']):
            cis.resultadoCl = row['ResultadoCl'] if row['ResultadoCl'] in ['Aderente', 'Não Aderente'] else cis.resultadoCl

        # Processa comentários
        if 'Comentários' in row and pd.notna(row['Comentários']):
            cis.comentarios = row['Comentários']    
        
        # Processar meta
        meta = row['Meta'] 
        if meta in ['Aderente', 'Não Aderente']:
            if meta == 'Aderente':
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
# Função para processar o arquivo excel do Nist
def andamento_excel_nist(excel_file, assessment):
    df = pd.read_excel(excel_file)

    # Filtra os CisModel que estão associados ao assessment atual
    nist_models = NistModel.objects.filter(assessment=assessment)

    for nist, (_, row) in zip(nist_models, df.iterrows()):
        # Processar nota Css
        if 'NotaCss' in row and pd.notna(row['NotaCss']):
            nist.notaCss = row['NotaCss']  # Atualizar o campo notaCss no modelo

        # Processar nota Cl
        if 'NotaCl' in row and pd.notna(row['NotaCl']):
            nist.notaCl = row['NotaCl']  # Atualizar o campo notaCl no modelo

        # Processar comentários
        if 'Comentários' in row and pd.notna(row['Comentários']):
            nist.comentarios = row['Comentários']  # Atualizar o campo comentarios no modelo

        # Processar nota Meta
        if 'Meta' in row and pd.notna(row['Meta']):
            nist.meta = row['Meta']  # Atualizar o campo meta no modelo

        # Atualizar a data de upload para a data atual
        assessment.data_upload = timezone.now().date()
        assessment.save()

        # Salva as alterações no banco de dados
        assessment.data_upload = timezone.now().date()
        nist.save()

    # Atualiza o arquivo do assessment
    update_assessment_file_nist(assessment)
# Função para processar o arquivo excel do Nist
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

        # Processar nota Cl
        if 'NotaCl' in row and pd.notna(row['NotaCl']):
            nist.notaCl = row['NotaCl']  # Atualizar o campo notaCl no modelo
        
        # Processar comentários
        if 'Comentários' in row and pd.notna(row['Comentários']):
            nist.comentarios = row['Comentários']  # Atualizar o campo comentarios no modelo
        
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
# Função para criar um arquivo excel do Iso
def andamento_excel_iso(excel_file, assessment):
    df = pd.read_excel(excel_file)

    # Filtra os IsoModel que estão associados ao assessment atual
    iso_models = IsoModel.objects.filter(assessment=assessment)
    
    for iso, (_, row) in zip(iso_models, df.iterrows()):
        # Precessa prioridade do controle
        if 'Prioridade do controle' in row and pd.notna(row['Prioridade do controle']):
            iso.prioControle = row['Prioridade do controle'] if row['Prioridade do controle'] in ['Conforme', 'Parcialmente', 'Não'] else iso.prioControle

        # Processa nota CSS
        if 'NotaCss' in row and pd.notna(row['NotaCss']):
            iso.notaCss = row['NotaCss'] if row['NotaCss'] in ['Conforme', 'Parcialmente Conforme', 'Não conforme'] else iso.notaCss

        # Processa nota CL
        if 'NotaCl' in row and pd.notna(row['NotaCl']):
            iso.notaCl = row['NotaCl'] if row['NotaCl'] in ['Conforme', 'Parcialmente Conforme', 'Não conforme'] else iso.notaCl

        # Processa comentários
        if 'Comentários' in row and pd.notna(row['Comentários']):
            iso.comentarios = row['Comentários']

        # Processa meta
        if 'Meta' in row and pd.notna(row['Meta']):
            iso.meta = row['Meta'] if row['Meta'] in ['Conforme', 'Parcialmente Conforme', 'Não conforme'] else iso.meta

        # Atualizar a data de upload para a data atual
        assessment.data_upload = timezone.now().date()
        assessment.save()

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
        if nota_css in ['Conforme', 'Parcialmente Conforme', 'Não conforme']:
            if nota_css == 'Conforme':
                total_css_conf += 1
            total_css_count += 1

        # Processa nota CL
        if 'NotaCl' in row and pd.notna(row['NotaCl']):
            iso.notaCl = row['NotaCl'] if row['NotaCl'] in ['Conforme', 'Parcialmente Conforme', 'Não conforme'] else iso.notaCl

        # Processa comentários
        if 'Comentários' in row and pd.notna(row['Comentários']):
            iso.comentarios = row['Comentários']
        
        # Processar meta
        meta = row['Meta']  
        if meta in ['Conforme', 'Parcialmente Conforme', 'Não conforme']:
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

    # Salva a instância de AssessmentModel
    assessment.save()


# -------- Framework Proprio -------- #
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

        # Atualizar a data de upload para a data atual
        assessment.data_upload = timezone.now().date()
        assessment.save()

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

        # Processa resultado CL
        if 'ResultadoCl' in row and pd.notna(row['ResultadoCl']):
            prop.resultadoCl = row['ResultadoCl'] if row['ResultadoCl'] in ['Sim', 'Não'] else prop.resultadoCl

        # Processa comentários
        if 'Comentários' in row and pd.notna(row['Comentários']):
            prop.comentarios = row['Comentários']
        
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
            form1.save()
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


# Função dedicada pra realizar os downloads dos arquivos
def download_file(request, filename):
    file_path = os.path.join(settings.MEDIA_ROOT, filename)
    if os.path.exists(file_path):
        with open(file_path, 'rb') as fh:
            response = HttpResponse(fh.read(), content_type="application/vnd.ms-excel")
            response['Content-Disposition'] = f'attachment; filename={os.path.basename(file_path)}'
            return response
    raise Http404
