# Generated by Django 5.0.6 on 2024-10-22 17:50

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('assessment', '0003_cadplanodeacaomodel'),
    ]

    operations = [
        migrations.AlterField(
            model_name='cadplanodeacaomodel',
            name='fim_pla',
            field=models.DateField(blank=True),
        ),
        migrations.AlterField(
            model_name='cadplanodeacaomodel',
            name='fim_real',
            field=models.DateField(blank=True),
        ),
        migrations.AlterField(
            model_name='cadplanodeacaomodel',
            name='inicio_pla',
            field=models.DateField(blank=True),
        ),
        migrations.AlterField(
            model_name='cadplanodeacaomodel',
            name='inicio_real',
            field=models.DateField(blank=True),
        ),
        migrations.AlterField(
            model_name='cadplanodeacaomodel',
            name='onde',
            field=models.CharField(blank=True, max_length=255),
        ),
        migrations.AlterField(
            model_name='cadplanodeacaomodel',
            name='quanto',
            field=models.CharField(blank=True, max_length=255),
        ),
        migrations.AlterField(
            model_name='cadplanodeacaomodel',
            name='status',
            field=models.CharField(blank=True, max_length=20),
        ),
    ]
