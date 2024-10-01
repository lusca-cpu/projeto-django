from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver

# Modelo para o Assessment
class FrameworkModel(models.Model):
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

    def __str__(self):
        return self.nome

# Modelo para o Assessment
class AssessmentModel(models.Model):
    CONCLUIDO = 'Concluído'
    ANDAMENTO = 'Andamento'
    
    CRITERIO_CHOICES = [
        (CONCLUIDO, 'Concluído'),
        (ANDAMENTO, 'Andamento'),
    ]

    framework = models.ForeignKey(FrameworkModel, on_delete=models.CASCADE)
    nome = models.CharField(max_length=255)
    status = models.CharField(max_length=20, choices=CRITERIO_CHOICES)
    data_upload = models.DateField(auto_now_add=True) 
    excel_file = models.FileField(upload_to='assessments/')
    resultado = models.CharField(max_length=255)
    meta = models.CharField(max_length=255)

    def __str__(self):
        return self.nome

# Modelo da Framework Planilha Generica Template
class PlanilhaGenericaTemplate(models.Model):
    framework = models.ForeignKey(FrameworkModel, on_delete=models.CASCADE, related_name='planilhas_genericas_templates')  # Relacionamento
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

    def __str__(self):
        return self.controle
# Modelo da Framework Planilha Generica
class PlanilhaGenericaModel(models.Model):
    assessment = models.ForeignKey(AssessmentModel, on_delete=models.CASCADE, related_name='planilhas_genericas_model')
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

    def __str__(self):
        return self.controle


# Modelo do Framework CIS Template
class CisModelTemplate(models.Model):
    framework = models.ForeignKey(FrameworkModel, on_delete=models.CASCADE, related_name='cis_templates')  # Relacionado ao Framework
    idControle = models.CharField(max_length=255, blank=True)
    controle = models.CharField(max_length=255, blank=True)
    tipoAtivo = models.CharField(max_length=255, blank=True)
    funcao = models.CharField(max_length=255, blank=True)
    idSubConjunto = models.CharField(max_length=255, blank=True)
    subConjunto = models.CharField(max_length=255, blank=True)
    nivel = models.CharField(max_length=255, blank=True)
    resultadoCss = models.CharField(max_length=255, blank=True)
    resultadoCl = models.CharField(max_length=255, blank=True)
    comentarios = models.TextField(blank=True)
    meta = models.CharField(max_length=255, blank=True)

    def __str__(self):
        return self.controle
# modelos do Fraework CIS
class CisModel(models.Model):
    assessment = models.ForeignKey(AssessmentModel, on_delete=models.CASCADE, related_name='cis_models')
    idControle = models.CharField(max_length=255)
    controle = models.CharField(max_length=255)
    tipoAtivo = models.CharField(max_length=255)
    funcao = models.CharField(max_length=255)
    idSubConjunto = models.CharField(max_length=255)
    subConjunto = models.CharField(max_length=255)
    nivel = models.CharField(max_length=255)
    resultadoCss = models.CharField(max_length=255)
    resultadoCl = models.CharField(max_length=255)
    comentarios = models.TextField()
    meta = models.CharField(max_length=255)

    def __str__(self):
        return self.controle


# Modelo do Framework Iso template
class IsoModelTemplate(models.Model):
    framework = models.ForeignKey(FrameworkModel, on_delete=models.CASCADE, related_name='iso_templates')
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

    def __str__(self):
        return f"{self.secao} - {self.codCatecoria}"
# Modelos do Framework Iso
class IsoModel(models.Model):
    assessment = models.ForeignKey(AssessmentModel, on_delete=models.CASCADE, related_name='iso_models')
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

    def __str__(self):
        return f"{self.secao} - {self.codCatecoria}"


# Modelo do Framework NIST Template
class NistModelTemplate(models.Model):
    framework = models.ForeignKey(FrameworkModel, on_delete=models.CASCADE, related_name='nist_templates')
    categoria = models.CharField(max_length=255)
    funcao = models.CharField(max_length=255)
    codigo = models.CharField(max_length=255)
    subcategoria = models.CharField(max_length=255)
    informacao = models.TextField()
    notaCss = models.CharField(max_length=255)
    notaCl = models.CharField(max_length=255)
    comentarios = models.TextField()
    meta = models.CharField(max_length=255)

    def __str__(self):
        return f"{self.categoria} - {self.codigo}"
# Modelos do Framework NIST
class NistModel(models.Model):
    assessment = models.ForeignKey(AssessmentModel, on_delete=models.CASCADE, related_name='nist_model')
    categoria = models.CharField(max_length=255)
    funcao = models.CharField(max_length=255)
    codigo = models.CharField(max_length=255)
    subcategoria = models.CharField(max_length=255)
    informacao = models.TextField()
    notaCss = models.CharField(max_length=255)
    notaCl = models.CharField(max_length=255)
    comentarios = models.TextField()
    meta = models.CharField(max_length=255)

    def __str__(self):
        return f"{self.categoria} - {self.codigo}"
