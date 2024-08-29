from django.urls import path
from . import views
from django.conf import settings

urlpatterns = [
    path('', views.index, name='index'),
    path('security/', views.security_assessment, name='security'),
    path('framework/', views.framework, name='framework'),
    path('framework/adicionar/', views.adicionar_framework, name='adicionar_framework'),
    path('framework/editar/<int:pk>/', views.editar_framework, name='editar_framework'),
    path('/<str:filename>/', views.download_file, name='download_file'),
    path('assessment/', views.assessment, name='assessment'),
    path('assess_nist/', views.assess_nist, name='assess_nist'),
    path('assess_cis/', views.assess_cis, name='assess_cis'),

    

    #path('framework/', views.formulario_add, name='formulario_add'),
    #path('framework/', views.formulario_edit, name='formulario_edit'),
]