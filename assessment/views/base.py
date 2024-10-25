from django.views import View
from django.shortcuts import render

def index(request):
    return render(request, 'paginas/index.html')

def security_assessment(request):
    return render(request, 'paginas/security.html')
