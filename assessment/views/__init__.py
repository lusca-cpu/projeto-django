from .base import index, security_assessment
from .framework import Framework, editar_framework, download_file
from .redirecionar import RedirecionarFramework, RedirecionarFramework2, RedirecionarPlanoAcao
from .assessment import Assessment, download_file
from .assess_cis import AssessCisUpload, AssessCis, download_file 
from .assess_nist import AssessNistUpload, AssessNist, download_file
from .assess_iso import AssessIsoUpload, AssessIso, download_file
from .assess_prop import AssessPropUpload, AssessProp, download_file
from .plano_acao import PlanodeAcao
from .painel_result import PaineldeResultados
from .cad_plano_acao import CadPlanodeAcao, editar_cad_plano_acao, download_file