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
    path('delete-framework/<int:id>/', views.Framework.as_view(), name='delete_framework'),  # Para exclusão

    path('download/<str:filename>/', views.download_file, name='download_file'),
    
    path('assessment/', views.assessment, name='assessment'),
    path('assess_nist/', views.assess_nist, name='assess_nist'),
    path('assess_cis/', views.assess_cis, name='assess_cis'),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)