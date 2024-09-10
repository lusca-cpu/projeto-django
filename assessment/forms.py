from django import forms
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout
from .models import MeuModelo

class MeuModeloForm(forms.ModelForm):
    class Meta:
        model = MeuModelo
        fields = ['nome', 'descricao', 'criterio', 'excel_file']  # Inclua o campo excel_file aqui
        widgets = {
            'nome': forms.TextInput(attrs={'class': 'form-control font-small',}),
            'descricao': forms.Textarea(attrs={'class': 'form-control', 'style': 'font-size: 11px;', 'rows': 3}),
            'criterio': forms.Select(attrs={'class': 'select font-small', 'style': 'font-size: 8px;'}),
            'excel_file': forms.ClearableFileInput(attrs={'class': 'form-control form-control-sm me-2 font-small'}),  # Adiciona o widget do arquivo
        }    
        labels = {
            'nome': 'Nome',
            'descricao': 'Descrição',
            'criterio': 'Critério',
        }
 
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_class = 'form-horizontal'
        self.helper.label_class = 'col-md-3 mb-0'
        self.helper.field_class = 'col-md-9'
       # self.helper.add_input(Submit('submit', 'Enviar'))

class MeuModeloEditForm(forms.ModelForm):
    class Meta:
        model = MeuModelo
        fields = ['nome', 'descricao', 'criterio', 'excel_file']  # Inclua o campo excel_file aqui
        widgets = {
            'nome': forms.TextInput(attrs={'class': 'form-control font-small', 'style': 'font-size: 11px;'}),
            'descricao': forms.Textarea(attrs={'class': 'form-control', 'style': 'font-size: 11px;', 'rows': 3}),
            'criterio': forms.Select(attrs={'class': 'form-select', 'style': 'font-size: 11px;'}),
            'excel_file': forms.ClearableFileInput(attrs={'class': 'form-control form-control-sm me-2 font-small'}),  # Adiciona o widget do arquivo
        }   
        labels = {
            'nome': 'Nome',
            'descricao': 'Descrição',
            'criterio': 'Critério',
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_class = 'form-horizontal'
        self.helper.label_class = 'col-md-3 mb-0'
        self.helper.field_class = 'col-md-9'


class NovoAssessmentForm(forms.ModelForm):
    tipo_assessment = forms.CharField(
        label="Tipo do Assessment",
        max_length=100,
        widget=forms.TextInput(attrs={'class': 'form-control', 'style': 'font-size: 11px;'})
    )
    status = forms.CharField(
        label="Status",
        max_length=100,
        widget=forms.TextInput(attrs={'class': 'form-control', 'style': 'font-size: 11px;'})
    )
    data_atualizacao = forms.DateField(
        label="Data de Atualização",
        widget=forms.DateInput(attrs={'class': 'form-control', 'style': 'font-size: 11px;', 'type': 'date'})
    )

    class Meta:
        model = MeuModelo
        fields = ['tipo_assessment', 'status', 'data_atualizacao']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_class = 'form-horizontal'
        self.helper.label_class = 'col-md-3 mb-0'
        self.helper.field_class = 'col-md-9'
        