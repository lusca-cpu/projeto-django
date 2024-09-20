from django.db import models
import uuid  # Para gerar IDs únicos para cada upload
from django.db.models.signals import post_save
from django.dispatch import receiver

class TipoModelo(models.Model):
    BINARIO = 'Binário'
    CMMI = 'CMMI'
    CONFORMIDADE = 'Conformidade'

    CRITERIO_CHOICES = [
        (BINARIO, 'Binário'),
        (CMMI, 'CMMI'),
        (CONFORMIDADE, 'Conformidade'),
    ]

    nome = models.CharField(max_length=100)
    descricao = models.TextField()
    criterio = models.CharField(max_length=20, choices=CRITERIO_CHOICES)
    excel_file = models.FileField(upload_to='uploads/')# Define para salvar na pasta media
    data_upload = models.DateField(auto_now_add=True)
    is_proprio = models.BooleanField(default=False)  # Campo booleano para checkbox
    upload_id = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)  # ID único para cada upload

    def __str__(self):
        return self.nome


# Modelo da Framework_Planilha Generica
class PlanilhaGenerica(models.Model):
    framework = models.ForeignKey(TipoModelo, on_delete=models.CASCADE, related_name='planilhas_genericas')  # Relacionamento
    idControle = models.IntegerField()
    controle = models.CharField(max_length=255)
    idSubControle = models.IntegerField()
    subControle = models.CharField(max_length=255)
    funcaoSeguranca = models.CharField(max_length=255)
    tipoAtivo = models.CharField(max_length=255)
    informacoesAdicionais = models.TextField()
    resultadoCss = models.CharField(max_length=255)
    resultadoCl = models.CharField(max_length=255)
    comentarios = models.TextField()
    meta = models.CharField(max_length=255)
    upload_id = models.UUIDField(default=uuid.uuid4)  # Associa cada linha de dados ao upload específico

    def __str__(self):
        return self.controle


# Modelo do Assessment CIS Control V8.1
class CisControl(models.Model):
    framework = models.ForeignKey(TipoModelo, on_delete=models.CASCADE, related_name='cis_controls')  # Relacionamento
    idControle = models.IntegerField()
    controle = models.CharField(max_length=255)
    tipoAtivo = models.CharField(max_length=255)
    funcao = models.CharField(max_length=255)
    idSubConjunto = models.IntegerField()
    subConjunto = models.CharField(max_length=255)
    nivel = models.CharField(max_length=255)
    resultadoCss = models.CharField(max_length=255)
    resultadoCl = models.CharField(max_length=255)
    comentarios = models.TextField()
    meta = models.CharField(max_length=255)
    upload_id = models.UUIDField(default=uuid.uuid4)  # Associa cada linha de dados ao upload específico

    def __str__(self):
        return self.controle


# Modelo do Assessment ISO 27000
class Iso(models.Model):
    framework = models.ForeignKey(TipoModelo, on_delete=models.CASCADE, related_name='isos')  # Relacionamento
    secao = models.CharField(max_length=255)
    codCatecoria = models.CharField(max_length=255)
    categoria = models.CharField(max_length=255)
    controle = models.CharField(max_length=255)
    diretrizes = models.TextField()
    prioControle = models.CharField(max_length=255)
    notaCss = models.CharField(max_length=255)
    notaCl = models.CharField(max_length=255)
    comentarios = models.TextField()
    meta = models.CharField(max_length=255)
    upload_id = models.UUIDField(default=uuid.uuid4)  # Associa cada linha de dados ao upload específico

    def __str__(self):
        return f"{self.secao} - {self.codCatecoria}"


# Modelo do Assessment NIST CSF 2.0
class NistCsf(models.Model):
    framework = models.ForeignKey(TipoModelo, on_delete=models.CASCADE, related_name='nist_csfs')  # Relacionamento
    categoria = models.CharField(max_length=255)
    funcao = models.CharField(max_length=255)
    codigo = models.CharField(max_length=255)
    subcategoria = models.CharField(max_length=255)
    informacao = models.TextField()
    notaCss = models.CharField(max_length=255)
    notaCl = models.CharField(max_length=255)
    comentarios = models.TextField()
    meta = models.CharField(max_length=255)
    upload_id = models.UUIDField(default=uuid.uuid4)  # Associa cada linha de dados ao upload específico

    def __str__(self):
        return f"{self.categoria} - {self.codigo}"

class AssessmentModel(models.Model):
    CONCLUIDO = 'Concluído'
    ANDAMENTO = 'Em andamento'
    
    CRITERIO_CHOICES = [
        (CONCLUIDO, 'Concluído'),
        (ANDAMENTO, 'Em andamento'),
    ]

    framework = models.ForeignKey(TipoModelo, on_delete=models.CASCADE, related_name='assessments')
    nome = models.CharField(max_length=255)
    status = models.CharField(max_length=20, choices=CRITERIO_CHOICES)
    data_upload = models.DateField(auto_now_add=True) 
    excel_file = models.FileField(upload_to='assessments/')
    resultado = models.CharField(max_length=255)
    meta = models.CharField(max_length=255)
    upload_id = models.UUIDField(default=uuid.uuid4)  # Associa cada linha de dados ao upload específico

    def __str__(self):
        return self.nome

@receiver(post_save, sender=TipoModelo)
def criar_assessment_model(sender, instance, created, **kwargs):
    if created:
        AssessmentModel.objects.create(
            nome=instance.nome,
            framework=instance,  # Relaciona diretamente com o TipoModelo
            status=AssessmentModel.ANDAMENTO,
            data_upload=instance.data_upload,
            excel_file=instance.excel_file,
            resultado='',
            meta=''
        )
