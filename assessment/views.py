from django.shortcuts import render, redirect, get_object_or_404
from .forms import MeuModeloForm, MeuModeloEditForm, NovoAssessmentForm
from .models import MeuModelo

from django.views import View
from django.views.generic import TemplateView
from django.views.generic.edit import UpdateView
from django.conf import settings
from django.http import HttpResponse, JsonResponse
from django.template.loader import render_to_string
from django.contrib import messages
import os
import pandas as pd

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
        form1 = MeuModeloForm(request.POST, request.FILES)  # Aqui você precisa do request.FILES para arquivos
        if form1.is_valid():
            framework = form1.save()  # Salva o formulário e o arquivo no banco de dados
            if framework.excel_file:  # Verifica se o arquivo foi corretamente associado
                uploaded_file_url = framework.excel_file.url  # Obtém a URL do arquivo salvo
                return render(request, self.template_name, {
                    'form1': MeuModeloForm(),  # Limpa o formulário após o upload
                    'uploaded_file_url': uploaded_file_url,  # Passa a URL do arquivo enviado
                    'frameworks': MeuModelo.objects.all()  # Atualiza a lista de frameworks
                })
            else:
                return render(request, self.template_name, {
                    'form1': form1,
                    'error_message': 'Nenhum arquivo foi associado ao framework.',  # Mensagem de erro
                    'frameworks': MeuModelo.objects.all()
                })
        else:
            return render(request, self.template_name, {
                'form1': form1,
                'frameworks': MeuModelo.objects.all()  # Recarrega a lista de frameworks em caso de erro
            })

    # Excluir Framework
    def delete(self, request, id):
        try:
            framework = MeuModelo.objects.get(id=id)
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
            form.save()
            return redirect('sucesso')  # Redirecione para a página de sucesso ou qualquer outra página desejada
    else:
        form = MeuModeloEditForm(instance=framework)
    return render(request, 'editar_framework.html', {'edit_form': form, 'framework': framework})  


def assessment(request):
    if request.method == 'POST':
        form1 = NovoAssessmentForm(request.POST, request.FILES)
        if form1.is_valid():
            form1.save()
            return redirect('success')
    else:
        form1 = NovoAssessmentForm()

    return render(request, 'paginas/assessment.html', {'form1': form1})

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