from django.shortcuts import render, redirect
from .forms import MeuModeloForm, MeuModeloEditForm, NovoAssessmentForm
from django.views.generic import TemplateView
from django.conf import settings
from django.http import HttpResponse
import os

from django.http import HttpResponse
import os
def index(request):
    return render(request, 'paginas/index.html')

def security_assessment(request):
    return render(request, 'paginas/security.html')

# Função para renderizar a página framework.html
def framework(request):
    form1 = MeuModeloForm()  # Formulário de adicionar framework
    form2 = MeuModeloEditForm()  # Formulário de editar framework
    return render(request, 'paginas/framework.html', {'form1': form1, 'form2': form2})

def adicionar_framework(request):
    if request.method == 'POST':
        form1 = MeuModeloForm(request.POST)
        if form1.is_valid():
            form1.save()
            return redirect('success') # Substitua 'success' pela URL desejada após a adição
    else:
        form1 = MeuModeloForm()
    return render(request, 'paginas/framework.html', {'form': form1})

def editar_framework(request, pk):
    instancia = get_object_or_404(MeuModelo, pk=pk)
    if request.method == 'POST':
        form2 = MeuModeloEditForm(request.POST, instance=instancia)
        if form2.is_valid():
            form2.save()
            return redirect('success')  # Substitua 'success' pela URL desejada após a edição
    else:
        form2 = MeuModeloEditForm(instance=instancia)
    return render(request, 'paginas/framework.html', {'form': form2})

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
    # Caminho completo para o arquivo
    file_path = os.path.normpath(os.path.join(settings.MEDIA_ROOT, filename))
    print(f"Caminho do arquivo: {file_path}") # Para testar, deve mostrar: C:\Users\danie\projetos\media\teste.txt
    
    # Verificação da existência do arquivo
    if os.path.exists(file_path):
        with open(file_path, 'rb') as f:
            response = HttpResponse(f.read(), content_type="application/force-download")
            response['Content-Disposition'] = f'attachment; filename={filename}'
            return response
    else:
        return HttpResponse("Arquivo não encontrado.", status=404)