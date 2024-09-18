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
    path('assessment/<int:id>/redirecionar/', views.Assessment().redirecionar_framework, name='redirecionar_framework'),

    path('assess_nist/', views.AssessNist.as_view(), name='assess_nist'),
    path('assess_cis/', views.AssessCis.as_view(), name='assess_cis'),
    path('assess_iso/', views.AssessIso.as_view(), name='assess_iso'),
    path('assess_prop/', views.AssessProp.as_view(), name='assess_prop'),

]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)