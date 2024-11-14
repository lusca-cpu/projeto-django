from django.db.models import Sum, Count, Q
from django.http import HttpResponse, JsonResponse
from django.shortcuts import render, redirect
from django.utils import timezone
from django.views import View

from ..forms import MeuModeloAcaoForm, MeuModeloAcaoEditForm 
from ..models import AssessmentModel,PlanoAcaoModel, CadPlanodeAcaoModel, NistModel, IsoModel, CisModel, PlanilhaGenericaModel

import pandas as pd

def get_subcontrole_choices(assessment):
    if NistModel.objects.filter(assessment=assessment).exists():
        return NistModel.objects.filter(assessment=assessment).values_list('id', 'subcategoria')
    elif IsoModel.objects.filter(assessment=assessment).exists():
        return IsoModel.objects.filter(assessment=assessment).values_list('id', 'categoria')
    elif CisModel.objects.filter(assessment=assessment).exists():
        return CisModel.objects.filter(assessment=assessment).values_list('id', 'subConjunto')
    elif PlanilhaGenericaModel.objects.filter(assessment=assessment).exists():
        return PlanilhaGenericaModel.objects.filter(assessment=assessment).values_list('id', 'subControle')
    return []

class CadPlanodeAcao(View):
    template_name = 'paginas/cad_plano_acao.html'

    def get(self, request, id):
        acao = PlanoAcaoModel.objects.get(id=id)
        cad_acoes = CadPlanodeAcaoModel.objects.filter(planoacao=acao)
        form1 = MeuModeloAcaoForm()
        form2 = MeuModeloAcaoEditForm()

        # Obtenha as escolhas de subcontrole
        assessment = acao.assessment
        subcontrole_choices = get_subcontrole_choices(assessment)

        # Atribua as opções aos dois formulários
        form1.fields['subcontrole'].choices = subcontrole_choices
        form2.fields['subcontrole'].choices = subcontrole_choices

        return render(request, self.template_name, {    
            'acao': acao,
            'cad_acoes': cad_acoes,
            'acao_id': id,
            'form1': form1,
            'form2': form2
        })

    def post(self, request, id):
        form1 = MeuModeloAcaoForm(request.POST, request.FILES)
        acao = PlanoAcaoModel.objects.get(id=id)
        
        # Obtenha as escolhas de subcontrole
        assessment = acao.assessment
        subcontrole_choices = get_subcontrole_choices(assessment)
        
        # Atribua as opções ao formulário de adição
        form1.fields['subcontrole'].choices = subcontrole_choices

        if form1.is_valid():
            cad_acao_instance = form1.save(commit=False)
            
            # Obter o ID do subcontrole e buscar o texto
            subcontrole_id = form1.cleaned_data['subcontrole']
            subcontrole_text = dict(subcontrole_choices).get(int(subcontrole_id), "")
            
            # Substituir o ID do subcontrole pelo texto
            cad_acao_instance.subcontrole = subcontrole_text
            cad_acao_instance.planoacao = acao
            cad_acao_instance.save()

            # Atualizar o custo estimado do plano de ação
            custo_total = CadPlanodeAcaoModel.objects.filter(planoacao=acao).aggregate(total_custo=Sum('quanto'))['total_custo'] or 0
            acao.custo_estimado = custo_total
            acao.save()

            # Lógica para definir o status da nova instância
            now = timezone.now().date()
            inicio_pla = cad_acao_instance.inicio_pla
            fim_pla = cad_acao_instance.fim_pla
            inicio_real = cad_acao_instance.inicio_real
            fim_real = cad_acao_instance.fim_real

            if fim_real and fim_real <= now:  # Concluído quando fim_real é hoje ou anterior
                cad_acao_instance.status = "Concluído"
            elif inicio_real and (not fim_real or fim_real > now):  # Em andamento se existe inicio_real mas não fim_real ou fim_real no futuro
                cad_acao_instance.status = "Em andamento"
            elif fim_pla and fim_pla < now and not fim_real:  # Atrasado se fim_pla passou e fim_real não existe
                cad_acao_instance.status = "Atrasado"
            elif inicio_pla and not inicio_real:  # A iniciar ou Início atrasado dependendo da data
                if inicio_pla >= now:
                    cad_acao_instance.status = "A iniciar"
                else:
                    cad_acao_instance.status = "Início atrasado"
            else:
                cad_acao_instance.status = ""

            # Salvar o status atualizado
            cad_acao_instance.save()

            # Atualizar o campo `acoes_cad` e `conclusao` para o plano de ação
            acao.acoes_cad = CadPlanodeAcaoModel.objects.filter(planoacao=acao).count()
            total_acoes = acao.acoes_cad
            concluidas = CadPlanodeAcaoModel.objects.filter(planoacao=acao, status="Concluído").count()
            acao.conclusao = (concluidas / total_acoes) * 100 if total_acoes > 0 else 0

            # Atualizar o campo `status` baseado na conclusão
            if acao.conclusao == 0:
                acao.status = "A iniciar"
            elif 0 < acao.conclusao < 100:
                acao.status = "Em andamento"
            elif acao.conclusao == 100:
                acao.status = "Concluído"

            # Atualizar a data de upload do plano de ação
            acao.data_upload = timezone.now()
            acao.save()

            return redirect('cad_planodeacao', id=acao.id)

        else:
            print("Formulário inválido", form1.errors)

        return render(request, self.template_name, {
            'form1': form1,
            'cad_acoes': CadPlanodeAcaoModel.objects.filter(planoacao_id=id),
            'acao_id': id
        })

    # Excluir Plano de Ação
    def delete(self, request, id):
        try:
            cad_acao = CadPlanodeAcaoModel.objects.get(id=id)
            plano_acao = cad_acao.planoacao  # Obtém a instância do PlanoAcaoModel associada
        
            # Armazenar o custo da instância a ser excluída para atualizar o custo_estimado
            custo_instancia = float(cad_acao.quanto) if cad_acao.quanto else 0
            
            # Exclui a instância de CadPlanodeAcaoModel
            cad_acao.delete()
            
            # Atualizar o campo `acoes_cad` no PlanoAcaoModel
            plano_acao.acoes_cad = CadPlanodeAcaoModel.objects.filter(planoacao=plano_acao).count()
            
            # Atualizar o custo_estimado, subtraindo o custo da instância excluída
            custo_total = CadPlanodeAcaoModel.objects.filter(planoacao=plano_acao).aggregate(total_custo=Sum('quanto'))['total_custo'] or 0
            plano_acao.custo_estimado = custo_total
            
            # Recalcular a conclusão
            total_acoes = plano_acao.acoes_cad
            concluidas = CadPlanodeAcaoModel.objects.filter(planoacao=plano_acao, status="Concluído").count()
            plano_acao.conclusao = (concluidas / total_acoes) * 100 if total_acoes > 0 else 0
        
            # Atualizar o campo `status` baseado na conclusão
            if plano_acao.conclusao == 0:
                plano_acao.status = "A iniciar"
            elif 0 < plano_acao.conclusao < 100:
                plano_acao.status = "Em andamento"
            elif plano_acao.conclusao == 100:
                plano_acao.status = "Concluído"

            # Atualizar a data de upload
            plano_acao.data_upload = timezone.now()
            
            # Salva as atualizações no PlanoAcaoModel
            plano_acao.save()
            
            return JsonResponse({'success': True})
        except PlanoAcaoModel.DoesNotExist:
            return JsonResponse({'success': False, 'error': 'Item não encontrado'})

def editar_cad_plano_acao(request, id):
    cad_acao = CadPlanodeAcaoModel.objects.get(id=id)
    acao = cad_acao.planoacao
    assessment = acao.assessment

    if request.method == 'POST':
        form = MeuModeloAcaoEditForm(request.POST, request.FILES, instance=cad_acao)

        if form.is_valid():
            cad_acao_instance = form.save(commit=False)

            # Atualizar a data de upload para o plano de ação e instância
            current_time = timezone.now()
            acao.data_upload = current_time
            acao.save()
            cad_acao_instance.data_upload = current_time

            # Atualizar o campo custo_estimado no plano de ação
            custo_total = CadPlanodeAcaoModel.objects.filter(planoacao=acao).aggregate(total_custo=Sum('quanto'))['total_custo'] or 0
            acao.custo_estimado = custo_total
            acao.save()

            # Definir o status com base nas datas
            now = current_time.date()
            inicio_pla = cad_acao_instance.inicio_pla
            fim_pla = cad_acao_instance.fim_pla
            inicio_real = cad_acao_instance.inicio_real
            fim_real = cad_acao_instance.fim_real

            if fim_real and fim_real <= now:  # Concluído quando fim_real é hoje ou anterior
                cad_acao_instance.status = "Concluído"
            elif inicio_real and (not fim_real or fim_real > now):  # Em andamento se existe inicio_real mas não fim_real ou fim_real no futuro
                cad_acao_instance.status = "Em andamento"
            elif fim_pla and fim_pla < now and not fim_real:  # Atrasado se fim_pla passou e fim_real não existe
                cad_acao_instance.status = "Atrasado"
            elif inicio_pla and not inicio_real:  # A iniciar ou Início atrasado dependendo da data
                if inicio_pla >= now:
                    cad_acao_instance.status = "A iniciar"
                else:
                    cad_acao_instance.status = "Início atrasado"
            else:
                cad_acao_instance.status = ""

            # Salvar todas as alterações no banco
            cad_acao_instance.save()

            # Atualizar o campo `acoes_cad` e `conclusao` para o plano de ação
            acao.acoes_cad = CadPlanodeAcaoModel.objects.filter(planoacao=acao).count()
            total_acoes = acao.acoes_cad
            concluidas = CadPlanodeAcaoModel.objects.filter(planoacao=acao, status="Concluído").count()
            acao.conclusao = (concluidas / total_acoes) * 100 if total_acoes > 0 else 0

            # Atualizar o campo `status` baseado na conclusão
            if acao.conclusao == 0:
                acao.status = "A iniciar"
            elif 0 < acao.conclusao < 100:
                acao.status = "Em andamento"
            elif acao.conclusao == 100:
                acao.status = "Concluído"

            # Atualizar a data de upload do plano de ação
            acao.data_upload = timezone.now()
            acao.save()

            return redirect('cad_planodeacao', id=acao.id)

    else:
        form = MeuModeloAcaoEditForm(instance=cad_acao)

    # Verificação via AJAX
    if request.headers.get('x-requested-with') == 'XMLHttpRequest':
        response_data = {
            'projeto': cad_acao.projeto,
            'subcontrole': cad_acao.subcontrole,
            'acao': cad_acao.acao,
            'onde': cad_acao.onde,
            'responsavel': cad_acao.responsavel,
            'inicio_pla': cad_acao.inicio_pla,
            'fim_pla': cad_acao.fim_pla,
            'inicio_real': cad_acao.inicio_real,
            'fim_real': cad_acao.fim_real,
            'quanto': cad_acao.quanto,
            'observacao': cad_acao.observacao,
            'status': cad_acao.status  # Aqui pegamos o status diretamente de cad_acao, não de cad_acao_instance
        }
        return JsonResponse(response_data)

    return render(request, 'paginas/cad_plano_acao.html', {'form2': form, 'cad_acao': cad_acao})

def exportar_para_excel(request, id):
    # Filtra as ações para o plano de ação específico
    acao = PlanoAcaoModel.objects.get(id=id)
    cad_acoes = CadPlanodeAcaoModel.objects.filter(planoacao=acao)

    # Formata as datas no formato desejado (Exemplo: 'YYYY-MM-DD')
    data = [{
        'Projeto': acao.projeto,
        'Controle de FMK': acao.subcontrole,
        'Ação': acao.acao,
        'Onde': acao.onde,
        'Responsável': acao.responsavel,
        'Quanto': acao.quanto,
        'Início Planejado': acao.inicio_pla.strftime('%Y-%m-%d') if acao.inicio_pla else '',
        'Fim Planejado': acao.fim_pla.strftime('%Y-%m-%d') if acao.fim_pla else '',
        'Início Real': acao.inicio_real.strftime('%Y-%m-%d') if acao.inicio_real else '',
        'Fim Real': acao.fim_real.strftime('%Y-%m-%d') if acao.fim_real else '',
        'Status': acao.status,
        'Observações': acao.observacao,
    } for acao in cad_acoes]

    df = pd.DataFrame(data)

    # Cria o response como um arquivo Excel
    response = HttpResponse(content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
    
    # Formata o nome do arquivo com o nome do projeto e a data_assess
    file_name = f"{acao.nome}_{acao.data_assess.strftime('%Y-%m-%d')}.xlsx"  # Ajuste conforme o nome e formato desejado
    response['Content-Disposition'] = f'attachment; filename={file_name}'
    
    # Escreve o DataFrame no response (Excel)
    df.to_excel(response, index=False, engine='openpyxl')

    return response


# Função dedicada pra realizar os downloads dos arquivos
def download_file(request, filename):
    file_path = os.path.join(settings.MEDIA_ROOT, filename)
    if os.path.exists(file_path):
        with open(file_path, 'rb') as fh:
            response = HttpResponse(fh.read(), content_type="application/vnd.ms-excel")
            response['Content-Disposition'] = f'attachment; filename={os.path.basename(file_path)}'
            return response
    raise Http404
