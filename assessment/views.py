from django.shortcuts import render, redirect, get_object_or_404
from .forms import MeuModeloForm, MeuModeloEditForm, NovoAssessmentForm
from .models import TipoModelo, PlanilhaGenerica, CisControl, Iso, NistCsf, AssessmentModel

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
        frameworks = TipoModelo.objects.all()
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
                            notaCss=row['Nota (Css)'],
                            notaCl=row['Nota (Cl.)'],
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
                            notaCss=row['Nota (Css)'],
                            notaCl=row['Nota (Cl.)'],
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
                            resultadoCss=row['Resultado (Css)'],
                            resultadoCl=row['Resultado (Cl.)'],
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
                            resultadoCss=row['Resultado (Css)'],
                            resultadoCl=row['Resultado (Cl.)'],
                            comentarios=row['Comentários'],
                            meta=row['Meta'],
                            upload_id=upload_id  # Adiciona o upload_id único
                        )

            # Redireciona para evitar o reenvio do formulário ao atualizar a página
            return HttpResponseRedirect(reverse('framework'))

        # Se o formulário não for válido, renderiza a página novamente com o erro
        return render(request, self.template_name, {
            'form1': form1,
            'frameworks': TipoModelo.objects.all()
        })


    # Excluir Framework
    def delete(self, request, id):
        try:
            framework = TipoModelo.objects.get(id=id)
            
            # Exclui a instância correspondente em AssessmentModel
            assessment = AssessmentModel.objects.filter(nome=framework.nome).first()
            if assessment:
                if assessment.excel_file:
                    file_path = os.path.join(settings.MEDIA_ROOT, assessment.excel_file.name)
                    if os.path.isfile(file_path):
                        os.remove(file_path)
                assessment.delete()

            # Exclui o arquivo relacionado ao framework
            if framework.excel_file: 
                file_path = os.path.join(settings.MEDIA_ROOT, framework.excel_file.name)
                if os.path.isfile(file_path):
                    os.remove(file_path)

            # Exclui o framework
            framework.delete()
            return JsonResponse({'success': True})
        except TipoModelo.DoesNotExist:
            return JsonResponse({'success': False, 'error': 'Item não encontrado'})

def editar_framework(request, id):
    framework = get_object_or_404(TipoModelo, id=id)
    assessment = get_object_or_404(AssessmentModel, framework=framework)
    
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
            
            # Atualizar o AssessmentModel
            assessment.nome = framework.nome
            assessment.excel_file = framework.excel_file
            assessment.save()

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
        })
    else:
        return render(request, 'paginas/framework.html', {'form2': form, 'framework': framework})


# Função para renderizar a página assessment.html
class Assessment(View):
    template_name = 'paginas/assessment.html'

    def get(self, request):
        frameworks = TipoModelo.objects.all()  # Obtém todos os objetos de TipoModelo
        assessments = AssessmentModel.objects.all()  # Altera para assessments
        form1 = NovoAssessmentForm()

        return render(request, self.template_name, {
            'form1': form1, 
            'frameworks': frameworks, 
            'assessments': assessments  # Altera para assessments
        })

    def post(self, request):
        form1 = NovoAssessmentForm(request.POST, request.FILES)
        if form1.is_valid():
            form1.save()
            return redirect('assessment')

        assessments = AssessmentModel.objects.all()  # Inclui novamente os modelos no caso de erro no formulário
        return render(request, self.template_name, {
            'form1': form1, 
            'assessments': assessments  # Altera para assessments
        })

    # Excluir Framework
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

# Redirecionar para o Framework
class RedirecionarFramework(View):
    def get(self, request, id):
        framework = get_object_or_404(TipoModelo, id=id)
        excel_name = framework.excel_file.name.lower()

        if 'nist' in excel_name:
            return redirect('assess_nist', id=framework.id)  # Passa o id do framework para a view
        elif 'cis' in excel_name:
            return redirect('assess_cis', id=framework.id)
        elif 'iso' in excel_name:
            return redirect('assess_iso', id=framework.id)
        elif framework.is_proprio:
            return redirect('assess_prop', id=framework.id)
        else:
            return redirect('assessment')


class AssessCis(View):
    template_name = 'paginas/assess_cis.html'

    def get(self, request, id):
        assessment = get_object_or_404(AssessmentModel, id=id)
        # Filtra os frameworks relacionados ao assessment
        frameworks = TipoModelo.objects.filter(assessments=assessment)  # Usando relacionamento direto
        # Filtra os dados CisControl relacionados ao framework
        cis = CisControl.objects.filter(framework__in=frameworks)

        return render(request, self.template_name, {
            'frameworks': frameworks,
            'assessment': assessment,
            'cis': cis,
            'assessment_id': id
        })

    def post(self, request, id):
        # Obtém o AssessmentModel
        assessment = get_object_or_404(AssessmentModel, id=id)

        # Atualiza os CisControls com os dados do formulário
        for key, value in request.POST.items():
            if key.startswith('resultadoCss_'):
                cis_id = key.split('_')[1]
                cis = get_object_or_404(CisControl, id=cis_id)
                if value in ['Sim', 'Não']:
                    cis.resultadoCss = value
                    cis.save()
            elif key.startswith('resultadoCl_'):
                cis_id = key.split('_')[1]
                cis = get_object_or_404(CisControl, id=cis_id)
                if value in ['Sim', 'Não']:
                    cis.resultadoCl = value
                    cis.save()
            elif key.startswith('comentarios_'):
                cis_id = key.split('_')[1]
                cis = get_object_or_404(CisControl, id=cis_id)
                cis.comentarios = value
                cis.save()
            elif key.startswith('meta_'):
                cis_id = key.split('_')[1]
                cis = get_object_or_404(CisControl, id=cis_id)
                if value in ['Sim', 'Não']:
                    cis.meta = value
                    cis.save()

        # Redireciona de volta para a página de avaliação
        return redirect('assess_cis', id=id)



class AssessNist(View):
    template_name = 'paginas/assess_nist.html'

    def get(self, request, id):
        assessment = get_object_or_404(AssessmentModel, id=id)
        # Filtra os frameworks relacionados ao assessment
        frameworks = TipoModelo.objects.filter(assessments=assessment)  # Usando relacionamento direto
        # Filtra os dados NIST relacionados ao framework
        nists = NistCsf.objects.filter(framework__in=frameworks)
        notas = range(0, 6)

        return render(request, self.template_name, {
            'frameworks': frameworks,
            'assessment': assessment,
            'nists': nists,
            'notas': notas,
            'assessment_id': id
        })

    def post(self, request, id):
        # Obtém o AssessmentModel
        assessment = get_object_or_404(AssessmentModel, id=id)
        
        # Atualiza os NistCsf com os dados do formulário
        for key, value in request.POST.items():
            if key.startswith('notaCss_'):
                nist_id = key.split('_')[1]
                nist = get_object_or_404(NistCsf, id=nist_id)
                nist.notaCss = value
                nist.save()
            elif key.startswith('notaCl_'):
                nist_id = key.split('_')[1]
                nist = get_object_or_404(NistCsf, id=nist_id)
                nist.notaCl = value
                nist.save()
            elif key.startswith('comentarios_'):
                nist_id = key.split('_')[1]
                nist = get_object_or_404(NistCsf, id=nist_id)
                nist.comentarios = value
                nist.save()
            elif key.startswith('meta_'):
                nist_id = key.split('_')[1]
                nist = get_object_or_404(NistCsf, id=nist_id)
                nist.meta = value
                nist.save()

        # Redireciona de volta para a página de avaliação
        return redirect('assess_nist', id=id)

class AssessIso(View):
    template_name = 'paginas/assess_iso.html'

    def get(self, request, id):
        assessment = get_object_or_404(AssessmentModel, id=id)
        # Filtra os frameworks relacionados ao assessment
        frameworks = TipoModelo.objects.filter(assessments=assessment)  # Usando relacionamento direto
        # Filtra os dados NIST relacionados ao framework
        isos = Iso.objects.filter(framework__in=frameworks)
        notas = range(0, 6)

        return render(request, self.template_name, {
            'frameworks': frameworks,
            'assessment': assessment,
            'isos': isos,
            'notas': notas,
            'assessment_id': id
        })

    def post(self, request, id):
        # Obtém o AssessmentModel
        assessment = get_object_or_404(AssessmentModel, id=id)
        
        # Atualiza os Iso com os dados do formulário
        for key, value in request.POST.items():
            if key.startswith('notaCss_'):
                iso_id = key.split('_')[1]
                iso = get_object_or_404(Iso, id=iso_id)
                iso.notaCss = value
                iso.save()
            elif key.startswith('notaCl_'):
                iso_id = key.split('_')[1]
                iso = get_object_or_404(Iso, id=iso_id)
                iso.notaCl = value
                iso.save()
            elif key.startswith('comentarios_'):
                iso_id = key.split('_')[1]
                iso = get_object_or_404(Iso, id=iso_id)
                iso.comentarios = value
                iso.save()
            elif key.startswith('meta_'):
                iso_id = key.split('_')[1]
                iso = get_object_or_404(Iso, id=iso_id)
                iso.meta = value
                iso.save()

        # Redireciona de volta para a página de avaliação
        return redirect('assess_iso', id=id)

class AssessProp(View):
    template_name = 'paginas/assess_prop.html'

    def get(self, request, id):
        assessment = get_object_or_404(AssessmentModel, id=id)
        # Filtra os frameworks relacionados ao assessment
        frameworks = TipoModelo.objects.filter(assessments=assessment)  # Usando relacionamento direto
        # Filtra os dados CisControl relacionados ao framework
        props = PlanilhaGenerica.objects.filter(framework__in=frameworks)

        return render(request, self.template_name, {
            'frameworks': frameworks,
            'assessment': assessment,
            'props': props,
            'assessment_id': id
        })

    def post(self, request, id):
        # Obtém o AssessmentModel
        assessment = get_object_or_404(AssessmentModel, id=id)

        # Atualiza os CisControls com os dados do formulário
        for key, value in request.POST.items():
            if key.startswith('resultadoCss_'):
                prop_id = key.split('_')[1]
                prop = get_object_or_404(PlanilhaGenerica, id=prop_id)
                if value in ['Sim', 'Não']:
                    prop.resultadoCss = value
                    prop.save()
            elif key.startswith('resultadoCl_'):
                prop_id = key.split('_')[1]
                prop = get_object_or_404(PlanilhaGenerica, id=prop_id)
                if value in ['Sim', 'Não']:
                    prop.resultadoCl = value
                    prop.save()
            elif key.startswith('comentarios_'):
                prop_id = key.split('_')[1]
                prop = get_object_or_404(PlanilhaGenerica, id=prop_id)
                prop.comentarios = value
                prop.save()
            elif key.startswith('meta_'):
                prop_id = key.split('_')[1]
                prop = get_object_or_404(PlanilhaGenerica, id=prop_id)
                if value in ['Sim', 'Não']:
                    prop.meta = value
                    prop.save()

        # Redireciona de volta para a página de avaliação
        return redirect('assess_prop', id=id)


class PlanodeAcao(View):
    template_name = 'paginas/planodeacao.html'

    def get(self, request):
        return render(request, self.template_name)

class PaineldeResultados(View):
    template_name = 'paginas/painelderesultados.html'

    def get(self, request):
        return render(request, self.template_name)

# Função dedicada pra realizar os downloads dos arquivos
def download_file(request, filename):
    file_path = os.path.join(settings.MEDIA_ROOT, filename)
    if os.path.exists(file_path):
        with open(file_path, 'rb') as fh:
            response = HttpResponse(fh.read(), content_type="application/vnd.ms-excel")
            response['Content-Disposition'] = f'attachment; filename={os.path.basename(file_path)}'
            return response
    raise Http404