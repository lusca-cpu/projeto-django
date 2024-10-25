from django.shortcuts import redirect, render
from django.views import View

from ..models import FrameworkModel, AssessmentModel, PlanoAcaoModel, CadPlanodeAcaoModel

# Redirecionar para o Framework para fazer a primeira avaliação
class RedirecionarFramework(View):
    def get(self, request, id):
        try:
            # Obtém o framework específico
            framework = FrameworkModel.objects.get(id=id)
        except FrameworkModel.DoesNotExist:
            # Se o framework não for encontrado, redireciona para a página de assessment
            return redirect('assessment')

        # Verifica o nome do arquivo Excel
        excel_name = framework.excel_file.name.lower()

        # Redireciona para a página de avaliação correta
        if 'nist' in excel_name:
            return redirect('assess_nist_up', id=framework.id)
        elif 'cis' in excel_name:
            return redirect('assess_cis_up', id=framework.id)
        elif 'iso' in excel_name:
            return redirect('assess_iso_up', id=framework.id)
        elif framework.is_proprio:
            return redirect('assess_prop_up', id=framework.id)
        else:
            # Se nenhuma condição for atendida, retorna para a página principal de assessment
            return redirect('assessment')
# Redirecionar para o Framework para vizualizar 
class RedirecionarFramework2(View):
    def get(self, request, id):
        try:
            # Obtém o assessment específico
            assessment = AssessmentModel.objects.get(id=id)
        except AssessmentModel.DoesNotExist:
            # Se o assessment não for encontrado, redireciona para a página de assessment
            return redirect('assessment')

        # Verifica o nome do arquivo Excel
        excel_name = assessment.excel_file.name.lower()

        # Redireciona para a página de avaliação correta
        if 'nist' in excel_name:
            return redirect('assess_nist', id=assessment.id)
        elif 'cis' in excel_name:
            return redirect('assess_cis', id=assessment.id)
        elif 'iso' in excel_name:
            return redirect('assess_iso', id=assessment.id)
        elif assessment.framework.is_proprio:
            return redirect('assess_prop', id=assessment.id)
        else:
            # Se nenhuma condição for atendida, retorna para a página principal de assessment
            return redirect('assessment')

class RedirecionarPlanoAcao(View):
    def get(self, request, id):
        return redirect('cad_planodeacao', id=id)