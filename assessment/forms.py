from django import forms
from crispy_forms.helper import FormHelper
from crispy_forms.bootstrap import FormActions
from .models import TipoModelo, AssessmentModel
import datetime

class MeuModeloForm(forms.ModelForm):
    class Meta:
        model = TipoModelo
        fields = ['nome', 'descricao', 'criterio', 'is_proprio', 'excel_file']
        widgets = {
            'nome': forms.TextInput(attrs={'class': 'form-control font-small'}),
            'descricao': forms.Textarea(attrs={'class': 'form-control', 'style': 'font-size: 11px;', 'rows': 3}),
            'criterio': forms.Select(attrs={'class': 'form-select font-small', 'style': 'font-size: 9px;'}),
            'is_proprio': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'excel_file': forms.ClearableFileInput(attrs={'class': 'form-control form-control-sm font-small'}),
        }
        labels = {
            'nome': 'Nome',
            'descricao': 'Descrição',
            'criterio': 'Critério',
            'is_proprio': 'Framework próprio?',
            'excel_file': 'Arquivo',
        }

    def __init__(self, *args, **kwargs):
        super(MeuModeloForm, self).__init__(*args, **kwargs)

        self.helper = FormHelper()
        self.helper.form_class = 'form-horizontal'
        self.helper.label_class = 'col-md-3 mb-0'
        self.helper.field_class = 'col-md-9'

class MeuModeloEditForm(forms.ModelForm):
    class Meta:
        model = TipoModelo
        fields = ['nome', 'descricao', 'criterio', 'excel_file']
        widgets = {
            'nome': forms.TextInput(attrs={'class': 'form-control font-small', 'style': 'font-size: 11px;'}),
            'descricao': forms.Textarea(attrs={'class': 'form-control', 'style': 'font-size: 11px;', 'rows': 3}),
            'criterio': forms.Select(attrs={'class': 'form-select', 'style': 'font-size: 9px;'}),
            'excel_file': forms.ClearableFileInput(attrs={'class': 'form-control form-control-sm me-2 font-small'}),
        }
        labels = {
            'nome': 'Nome',
            'descricao': 'Descrição',
            'criterio': 'Critério',
            'excel_file': 'Arquivo Excel',
        }

    def __init__(self, *args, **kwargs):
        super(MeuModeloEditForm, self).__init__(*args, **kwargs)

        # Atualizações dos placeholders e classes dos inputs
        self.fields['nome'].widget.attrs.update({'class': 'form-control', 'placeholder': 'Nome do framework'})
        self.fields['descricao'].widget.attrs.update({'class': 'form-control', 'placeholder': 'Descrição'})
        self.fields['criterio'].widget.attrs.update({'class': 'form-select'})
        self.fields['excel_file'].widget.attrs.update({'class': 'form-control form-control-sm me-2 font-small'})

class NovoAssessmentForm(forms.ModelForm):
    class Meta:
        model = AssessmentModel
        fields = ['nome', 'status', 'excel_file']
        widgets = {
            'nome': forms.TextInput(attrs={'class': 'form-control', 'style': 'font-size: 11px;'}),
            'status': forms.Select(attrs={'class': 'form-select font-small', 'style': 'font-size: 9px;'}),
            'excel_file': forms.ClearableFileInput(attrs={'class': 'form-control form-control-sm font-small'}),
        }
        labels = {
            'nome': 'Tipo de Assessment',
            'status': 'Status',
            'excel_file': 'Arquivo Excel',
        }

    def __init__(self, *args, **kwargs):
        super(NovoAssessmentForm, self).__init__(*args, **kwargs)
        self.fields['data_upload_display'] = forms.DateField(
            initial=datetime.date.today,  # Preenche com a data atual
            widget=forms.DateInput(attrs={
                'class': 'form-control',
                'style': 'font-size: 11px;',
                'type': 'date',
                'readonly': True  # Desabilita a edição
            })
        )
        self.helper = FormHelper()
        self.helper.form_class = 'form-horizontal'
        self.helper.label_class = 'col-md-3 mb-0'
        self.helper.field_class = 'col-md-9'
        