from .base import index, security_assessment
from .framework import Framework, editar_framework, download_file
from .redirecionar import RedirecionarFramework, RedirecionarFramework2, RedirecionarPlanoAcao, RedirecionarPainelResultados, RedirecionarPainelResultados2
from .assessment import Assessment, download_file
from .assess_cis import AssessCisUpload, AssessCis, download_file 
from .assess_nist import AssessNistUpload, AssessNist, download_file
from .assess_iso import AssessIsoUpload, AssessIso, download_file
from .assess_prop import AssessPropUpload, AssessProp, download_file
from .plano_acao import PlanodeAcao
from .cad_plano_acao import CadPlanodeAcao, editar_cad_plano_acao, exportar_para_excel, download_file
from .painel_result_cis import PaineldeResultadosCis
from .painel_result_nist import PaineldeResultadosNist
from .painel_result_iso import PaineldeResultadosIso