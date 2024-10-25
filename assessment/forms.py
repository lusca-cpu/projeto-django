from django import forms
from crispy_forms.helper import FormHelper
from crispy_forms.bootstrap import FormActions
from crispy_forms.layout import Layout, Submit, Div, Field, Row, Column
from .models import FrameworkModel, AssessmentModel, CadPlanodeAcaoModel
import datetime

class MeuModeloForm(forms.ModelForm):
    class Meta:
        model = FrameworkModel
        fields = ['nome', 'descricao', 'criterio', 'is_proprio', 'excel_file']
        widgets = {
            'nome': forms.TextInput(attrs={'class': 'form-control font-small'}),
            'descricao': forms.Textarea(attrs={'class': 'form-control', 'style': 'font-size: 11px;', 'rows': 3}),
            'criterio': forms.Select(attrs={'class': 'form-select font-small', 'style': 'font-size: 10px;'}),
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
        model = FrameworkModel
        fields = ['nome', 'descricao', 'criterio', 'excel_file']
        widgets = {
            'nome': forms.TextInput(attrs={'class': 'form-control font-small', 'style': 'font-size: 11px;'}),
            'descricao': forms.Textarea(attrs={'class': 'form-control', 'style': 'font-size: 11px;', 'rows': 3}),
            'criterio': forms.Select(attrs={'class': 'form-select', 'style': 'font-size: 10px;'}),
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
        fields = ['framework', 'status', 'excel_file']  # 'nome' será atribuído manualmente
        widgets = {
            'framework': forms.Select(attrs={'class': 'form-control', 'style': 'font-size: 11px;'}),
            'status': forms.Select(attrs={'class': 'form-select font-small', 'style': 'font-size: 10px;'}),
            'excel_file': forms.ClearableFileInput(attrs={'class': 'form-control form-control-sm font-small'}),
        }
        labels = {
            'framework': 'Tipo de Framework',
            'status': 'Status',
            'excel_file': 'Arquivo Excel',
        }

    def __init__(self, *args, **kwargs):
        super(NovoAssessmentForm, self).__init__(*args, **kwargs)

        # Carregar frameworks no campo 'framework'
        self.fields['framework'] = forms.ModelChoiceField(
            queryset=FrameworkModel.objects.all(),
            widget=forms.Select(attrs={'class': 'form-control', 'style': 'font-size: 10px;'}),
            label='Tipo de Framework'
        )
        
        # Campo para exibir a data atual
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

    def save(self, commit=True):
        # Sobrescreve o método de salvamento
        assessment = super(NovoAssessmentForm, self).save(commit=False)
        
        # Atribuir o nome do framework ao campo nome
        framework_selecionado = self.cleaned_data['framework']
        assessment.nome = framework_selecionado.nome  # Assume que 'nome' é o campo do FrameworkModel
        
        # Salvar a instância do assessment
        if commit:
            assessment.save()
        
        return assessment

class MeuModeloAcaoForm(forms.ModelForm):
    class Meta:
        model = CadPlanodeAcaoModel
        fields = ['projeto', 'subcontrole', 'acao', 'onde', 'responsavel', 'inicio_pla', 'fim_pla', 'inicio_real', 'fim_real', 'quanto', 'observacao']
        widgets = {
            'projeto': forms.TextInput(attrs={'class': 'form-control', 'style': 'font-size: 10px;', 'required': True}),
            'subcontrole': forms.TextInput(attrs={'class': 'form-control', 'style': 'font-size: 10px;', 'required': True}),
            'acao': forms.TextInput(attrs={'class': 'form-control', 'style': 'font-size: 10px;', 'required': True}),
            'onde': forms.TextInput(attrs={'class': 'form-control', 'style': 'font-size: 10px; width: 40%;'}),
            'responsavel': forms.TextInput(attrs={'class': 'form-control', 'style': 'font-size: 10px; width: 40%;', 'required': True}),
            'inicio_pla': forms.DateInput(attrs={'type': 'date', 'class': 'form-control', 'style': 'font-size: 10px; width: 40%;'}),
            'fim_pla': forms.DateInput(attrs={'type': 'date', 'class': 'form-control', 'style': 'font-size: 10px; width: 40%;'}),
            'inicio_real': forms.DateInput(attrs={'type': 'date', 'class': 'form-control', 'style': 'font-size: 10px; width: 40%;'}),
            'fim_real': forms.DateInput(attrs={'type': 'date', 'class': 'form-control', 'style': 'font-size: 10px; width: 40%;'}),
            'quanto': forms.NumberInput(attrs={'class': 'form-control', 'style': 'font-size: 10px;'}),
            'observacao': forms.Textarea(attrs={'class': 'form-control', 'style': 'font-size: 10px;'}),
        }
        labels = {
            'projeto': 'Projeto',
            'subcontrole': 'Subcontrole',
            'acao': 'Ação',
            'onde': 'Onde (escopo)',
            'responsavel': 'Responsável',
            'inicio_pla': 'Início Planejado',
            'fim_pla': 'Fim Planejado',
            'inicio_real': 'Início Real',
            'fim_real': 'Fim Real',
            'quanto': 'Quanto',
            'observacao': 'Observações',
        }

    def __init__(self, *args, **kwargs):
        super(MeuModeloAcaoForm, self).__init__(*args, **kwargs)

        self.helper = FormHelper()
        self.helper.layout = Layout(
            Row(
                Column('projeto', css_class='col-12'),
            ),
            Row(
                Column('subcontrole', css_class='col-12'),
            ),
            Row(
                Column('acao', css_class='col-12'),
            ),
            Row(
                Column('onde', css_class='col-6'),
                Column('responsavel', css_class='col-6'),
            ),
            Row(
                Column('inicio_pla', css_class='col-6'),
                Column('fim_pla', css_class='col-6'),
            ),
            Row(
                Column('inicio_real'),
                Column('fim_real'),
            ),
            Row(
                Column('quanto', css_class='col-12'),
            ),
            Row(
                Column('observacao', css_class='col-12'),
            ),
        )


class MeuModeloAcaoEditForm(forms.ModelForm):
    class Meta:
        model = CadPlanodeAcaoModel
        fields = ['projeto', 'subcontrole', 'acao', 'onde', 'responsavel', 'inicio_pla', 'fim_pla', 'inicio_real', 'fim_real', 'quanto', 'observacao']
        widgets = {
            'projeto': forms.TextInput(attrs={'class': 'form-control', 'style': 'font-size: 10px;', 'required': True}),
            'subcontrole': forms.TextInput(attrs={'class': 'form-control', 'style': 'font-size: 10px;', 'required': True}),
            'acao': forms.TextInput(attrs={'class': 'form-control', 'style': 'font-size: 10px;', 'required': True}),
            'onde': forms.TextInput(attrs={'class': 'form-control', 'style': 'font-size: 10px; width: 40%;'}),
            'responsavel': forms.TextInput(attrs={'class': 'form-control', 'style': 'font-size: 10px; width: 40%;', 'required': True}),
            'inicio_pla': forms.DateInput(attrs={'type': 'date', 'class': 'form-control', 'style': 'font-size: 10px; width: 40%;'}),
            'fim_pla': forms.DateInput(attrs={'type': 'date', 'class': 'form-control', 'style': 'font-size: 10px; width: 40%;'}),
            'inicio_real': forms.DateInput(attrs={'type': 'date', 'class': 'form-control', 'style': 'font-size: 10px; width: 40%;'}),
            'fim_real': forms.DateInput(attrs={'type': 'date', 'class': 'form-control', 'style': 'font-size: 10px; width: 40%;'}),
            'quanto': forms.NumberInput(attrs={'class': 'form-control', 'style': 'font-size: 10px;'}),
            'observacao': forms.Textarea(attrs={'class': 'form-control', 'style': 'font-size: 10px;'}),
        }
        labels = {
            'projeto': 'Projeto',
            'subcontrole': 'Subcontrole',
            'acao': 'Ação',
            'onde': 'Onde (escopo)',
            'responsavel': 'Responsável',
            'inicio_pla': 'Início Planejado',
            'fim_pla': 'Fim Planejado',
            'inicio_real': 'Início Real',
            'fim_real': 'Fim Real',
            'quanto': 'Quanto',
            'observacao': 'Observações',
        }

    def __init__(self, *args, **kwargs):
        super(MeuModeloAcaoEditForm, self).__init__(*args, **kwargs)

        # Atualizações dos placeholders e classes dos inputs
        self.fields['projeto'].widget.attrs.update({'class': 'form-control', 'placeholder': 'Projeto'})
        self.fields['subcontrole'].widget.attrs.update({'class': 'form-control', 'placeholder': 'Subcontrole'})
        self.fields['acao'].widget.attrs.update({'class': 'form-control', 'placeholder': 'Ação'})
        self.fields['onde'].widget.attrs.update({'class': 'form-control', 'placeholder': 'Onde (escopo)'})
        self.fields['responsavel'].widget.attrs.update({'class': 'form-control', 'placeholder': 'Responsável'})
        self.fields['inicio_pla'].widget.attrs.update({'class': 'form-control', 'placeholder': 'Início Planejado'})
        self.fields['fim_pla'].widget.attrs.update({'class': 'form-control', 'placeholder': 'Fim Planejado'})
        self.fields['inicio_real'].widget.attrs.update({'class': 'form-control', 'placeholder': 'Início Real'})
        self.fields['fim_real'].widget.attrs.update({'class': 'form-control', 'placeholder': 'Fim Real'})
        self.fields['quanto'].widget.attrs.update({'class': 'form-control', 'placeholder': 'Quanto'})
        self.fields['observacao'].widget.attrs.update({'class': 'form-control', 'placeholder': 'Observações'})
