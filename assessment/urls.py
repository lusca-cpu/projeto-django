from django.urls import path
from . import views
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('', views.index, name='index'),
    path('security/', views.security_assessment, name='security'),

    # urls para a pagina framework.html 
    path('framework/', views.Framework.as_view(), name='framework'),
    path('adicionar-framework/', views.Framework.as_view(), name='adicionar_framework'),
    path('frameworks/', views.Framework.as_view(), name='listar_frameworks'),  # Para listagem
    path('editar-framework/<int:id>/', views.editar_framework, name='edit_framework'),  # Para edição
    path('deletar-framework/<int:id>/', views.Framework.as_view(), name='deletar_framework'),  # Para exclusão

    path('download/<str:filename>/', views.download_file, name='download_file'),
    
    # urls para a pagina assessment.html 
    path('assessment/', views.Assessment.as_view(), name='assessment'),
    path('deletar-assessment/<int:id>/', views.Assessment.as_view(), name='deletar_assess'),  # Para exclusão
    path('assessment/<int:id>/redirecionar/', views.RedirecionarFramework.as_view(), name='redirecionar_framework'),
    path('assessment/<int:id>/redirecionar2/', views.RedirecionarFramework2.as_view(), name='redirecionar_framework2'), 

    # urls para a pagina assess_nist_up.html
    path('assess_nist_up/<int:id>/', views.AssessNistUpload.as_view(), name='assess_nist_up'),
    # urls para a pagina assess_nist.html
    path('assess_nist/<int:id>/', views.AssessNist.as_view(), name='assess_nist'),

    
    # urls para a pagina assess_cis_up.html
    path('assess_cis_up/<int:id>/', views.AssessCisUpload.as_view(), name='assess_cis_up'),
    # urls para a pagina assess_cis.html
    path('assess_cis/<int:id>/', views.AssessCis.as_view(), name='assess_cis'),
    

    # urls para a pagina assess_iso_up.html
    path('assess_iso_up/<int:id>/', views.AssessIsoUpload.as_view(), name='assess_iso_up'),
    # urls para a pagina assess_iso.html
    path('assess_iso/<int:id>/', views.AssessIso.as_view(), name='assess_iso'),

    
    # urls para a pagina assess_prop_up.html
    path('assess_prop_up/<int:id>/', views.AssessPropUpload.as_view(), name='assess_prop_up'),
    # urls para a pagina assess_prop.html
    path('assess_prop/<int:id>/', views.AssessProp.as_view(), name='assess_prop'),

    # urls para a pagina planodeacao.html
    path('planodeacao/', views.PlanodeAcao.as_view(), name='planodeacao'),
    path('deletar-planodeacao/<int:id>/', views.PlanodeAcao.as_view(), name='deletar_planodeacao'),  # Para exclusão
    path('planodeacao/<int:id>/redirecionarplano/', views.RedirecionarPlanoAcao.as_view(), name='redirecionar_planodeacao'),
    path('exportar/excel/<int:id>/', views.exportar_para_excel, name='exportar_excel'), # Para exportação

    # urls para a pagina cad_planodeacao.html
    path('cad_planodeacao/<int:id>/', views.CadPlanodeAcao.as_view(), name='cad_planodeacao'),
    path('deletar-cad-planodeacao/<int:id>/', views.CadPlanodeAcao.as_view(), name='deletar_cad_planodeacao'),  # Para exclusão
    path('editar-cad-planodeacao/<int:id>/', views.editar_cad_plano_acao, name='editar_cad_plano_acao'), # Para edição

    # urls para a pagina painel_result.html
    path('painel_result/', views.PaineldeResultados.as_view(), name='painelderesultados')
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)