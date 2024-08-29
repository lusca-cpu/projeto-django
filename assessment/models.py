from django.db import models

# Modelo para o formulário de upload
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

    def __str__(self):
        return self.nome

