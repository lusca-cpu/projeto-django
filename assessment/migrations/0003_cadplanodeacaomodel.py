# Generated by Django 5.0.6 on 2024-10-22 17:39

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('assessment', '0002_planoacaomodel'),
    ]

    operations = [
        migrations.CreateModel(
            name='CadPlanodeAcaoModel',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('projeto', models.CharField(max_length=255)),
                ('subcontrole', models.CharField(max_length=255)),
                ('acao', models.CharField(max_length=255)),
                ('onde', models.CharField(max_length=255)),
                ('responsavel', models.CharField(max_length=255)),
                ('quanto', models.CharField(max_length=255)),
                ('inicio_pla', models.DateField()),
                ('fim_pla', models.DateField()),
                ('inicio_real', models.DateField()),
                ('fim_real', models.DateField()),
                ('status', models.CharField(max_length=20)),
                ('observacao', models.TextField(blank=True, null=True)),
                ('planoacao', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='cad_planode_acao_model', to='assessment.planoacaomodel')),
            ],
        ),
    ]