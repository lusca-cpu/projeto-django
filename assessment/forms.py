from django import forms
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Submit, Button, Div, Field
from crispy_forms.bootstrap import FormActions
from .models import MeuModelo

class MeuModeloForm(forms.ModelForm):
    class Meta:
        model = MeuModelo
        fields = ['nome', 'descricao', 'criterio', 'is_proprio', 'excel_file']
        widgets = {
            'nome': forms.TextInput(attrs={'class': 'form-control font-small'}),
            'descricao': forms.Textarea(attrs={'class': 'form-control', 'style': 'font-size: 11px;', 'rows': 3}),
            'criterio': forms.Select(attrs={'class': 'form-select font-small', 'style': 'font-size: 9px;'}),
            'is_proprio': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'excel_file': forms.ClearableFileInput(attrs={'class': 'form-control form-control-sm me-2 font-small'}),
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

        self.helper.layout = Layout(
            'nome',
            'descricao',
            'criterio',
            'is_proprio',
            Div(
                Div(
                    Field('excel_file', css_class='form-control form-control-sm me-2 font-small'),
                    css_class='d-flex flex-column align-items-start'
                ),
                Div(
                    """
                    <span id="infoicon" class="d-flex align-items-center mt-2">
                        <svg class="bi-gear-fill" viewBox="0 0 16 16" width="16" height="16">
                            <path d="M8 16A8 8 0 1 0 8 0a8 8 0 0 0 0 16m.93-9.412-1 4.705c-.07.34.029.533.304.533.194 0 .487-.07.686-.246l-.088.416c-.287.346-.92.598-1.465.598-.703 0-1.002-.422-.808-1.319l.738-3.468c.064-.293.006-.399-.287-.47l-.451-.081.082-.381 2.29-.287zM8 5.5a1 1 0 1 1 0-2 1 1 0 0 1 0 2"/>
                        </svg>
                        <div class="infobubble">
                            <b>Instruções para planilha </b><br>
                            O cabeçalho NÃO pode ser alterado <br>
                            O número de colunas NÃO pode ser alterado <br>
                            As colunas "Id Controle" e "Controle" são OBRIGATÓRIAS e devem ser PREENCHIDAS <br>
                            Linhas e colunas NÃO devem ser mescladas <br>
                            NÃO saltar linhas entre os dados <br>
                            NÃO começar o preenchimento por uma linha aleatória <br>
                        </div>
                    </span>
                    """,
                    css_class="position-relative"
                ),
                css_class='mb-2'
            ),
            FormActions(
                Submit('submit', 'Upload', css_class='btn btn-primary btn-sm font-small')
            )
        )

class MeuModeloEditForm(forms.ModelForm):
    class Meta:
        model = MeuModelo
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

        # Configurando Crispy Forms Helper
        self.helper = FormHelper()
        self.helper.form_method = 'post'
        self.helper.form_class = 'needs-validation'
        self.helper.attrs = {'novalidate': ''}

        # Layout com botões
        self.helper.layout = Layout(
            'nome',
            'descricao',
            'criterio',
            'excel_file',
            Div(
                Submit('submit', 'Salvar', css_class='btn btn-success btn-sm font-small'),
                Button('cancel', 'Cancelar', css_class='btn btn-primary btn-sm font-small', 
                       onclick="$('#editarFrameworkModal').modal('hide');"),
                css_class='d-flex justify-content-end'  # Para alinhar os botões à direita
            )
        )

        # Atualizações dos placeholders e classes dos inputs
        self.fields['nome'].widget.attrs.update({'class': 'form-control', 'placeholder': 'Nome do framework'})
        self.fields['descricao'].widget.attrs.update({'class': 'form-control', 'placeholder': 'Descrição'})
        self.fields['criterio'].widget.attrs.update({'class': 'form-select'})
        self.fields['excel_file'].widget.attrs.update({'class': 'form-control form-control-sm me-2 font-small'})

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
        