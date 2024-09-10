from django.db import models

class MeuModelo(models.Model):
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
    excel_file = models.FileField()  # Define para salvar na pasta media
    data_upload = models.DateField(auto_now_add=True)

    def __str__(self):
        return self.nome

#modelo da Framework_Planilha Generica
class PlanilhaGenerica(models.Model):
    idControle = models.IntegerField()
    controle = models.CharField(max_length=255)
    idSubControle = models.IntegerField()
    subControle = models.CharField(max_length=255)
    funcaoSeguranca = models.CharField(max_length=255)
    tipoAtivo = models.CharField(max_length=255)
    informacoesAdicionais = models.TextField()

    def __str__(self):
        return self.controle

#modelo do Assessment CIS Control V8.1
class CisControl(models.Model):
    idControle = models.IntegerField()
    controle = models.CharField(max_length=255)
    tipoAtivo = models.CharField(max_length=255)
    funcao = models.CharField(max_length=255)
    idSubControle = models.IntegerField()
    subControle = models.CharField(max_length=255)
    nivel = models.CharField(max_length=255)
    resultado = models.CharField(max_length=255)
    comentarios = models.TextField()
    meta = models.CharField(max_length=255)

    def __str__(self):
        return self.controle

#modelo do Assessment ISO 27000
class Iso(models.Model):
    secao = models.CharField(max_length=255)
    codCatecoria = models.CharField(max_length=255)
    categoria = models.CharField(max_length=255)
    controle = models.CharField(max_length=255)
    diretrizes = models.TextField()
    nota = models.CharField(max_length=255)
    comentarios = models.TextField()
    meta = models.CharField(max_length=255)

    def __str__(self):
        return f"{self.secao} - {self.codCatecoria}"

#modelo do Assessment NIST CSF 2.0
class NistCsf(models.Model):
    categoria = models.CharField(max_length=255)
    funcao = models.CharField(max_length=255)
    codigo = models.CharField(max_length=255)
    subcategoria = models.CharField(max_length=255)
    informacao = models.TextField()
    nota = models.CharField(max_length=255)
    comentarios = models.TextField()
    meta = models.CharField(max_length=255)

    def __str__(self):
        return f"{self.categoria} - {self.codigo}"
        