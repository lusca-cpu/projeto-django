from django.db.models import Count, Sum, Q
from django.http import JsonResponse
from django.shortcuts import render
from django.views import View

from datetime import date

from ..models import AssessmentModel, CadPlanodeAcaoModel, CisModel, PlanoAcaoModel

import plotly.graph_objects as go
import re

# Função para renderizar a página painelderesultados.html
class PaineldeResultadosCis(View):
    template_name = 'paginas/painel_result_cis.html'

    # Responsável por abreviar a categoria
    def abreviar_categoria(self, cat):
        # Remover o texto entre parênteses e os próprios parênteses
        cat_sem_parenteses = re.sub(r"\s*\(.*?\)", "", cat).strip()
        palavras = cat_sem_parenteses.split()

        # Se a categoria tiver até 3 palavras, retornamos como está
        if len(palavras) <= 3:
            if len(palavras) > 1 and palavras[1].lower() == "de":
                return " ".join(palavras[:2]) + "<br>" + " ".join(palavras[2:])
            else:    
                return palavras[0] + "<br>" + " ".join(palavras[1:])
        # Se tiver mais de 3 palavras, pegamos apenas as 3 primeiras
        else:
            if palavras[0:3] == ['Inventário', 'e', 'controle']:
                return " ".join(palavras[-3:])
            elif len(palavras) > 1 and palavras[1].lower() == "de":
                return " ".join(palavras[:2]) + "<br>" + " ".join(palavras[2:3])
            else:
                return palavras[0] + "<br>" + " ".join(palavras[1:3])

    # INÍCIO GRÁFICOS DO ASSESSMENT ########################################################
    # Responsável pela criação do gráfico de velocímetro
    def view_grafico_velocimetro(self, framework_id):
        # Filtrar apenas as instâncias relacionadas ao CisModel e ao framework específico
        assessments_cis = AssessmentModel.objects.filter(
            framework__id=framework_id,
            framework__nome__icontains='cis',
            status='Concluído'
        )

        # Calcular soma de meta e resultado
        soma_meta = assessments_cis.aggregate(Sum('meta'))['meta__sum'] or 0
        soma_resultado = assessments_cis.aggregate(Sum('resultado'))['resultado__sum'] or 0

        total_instancias = AssessmentModel.objects.filter(framework__id=framework_id, framework__nome__icontains='cis', status='Concluído').count()

        soma_meta = soma_meta/total_instancias
        soma_resultado = soma_resultado/total_instancias

        # Dados para o gráfico
        valores = [soma_resultado, soma_meta]
        cormarcador = ["darkblue", "RoyalBlue", "LightBlue"]

        # Criar o gráfico velocímetro
        fig_velocimetro = go.Figure(go.Indicator(
            mode="gauge+number",
            value=valores[1],
            number={
                'font': {'color': "red", 'size': 16},
                'suffix': '%'
            },
            gauge={
                'axis': {
                    'range': [0, 100],
                    'tickcolor': "blue",
                    'ticks': "inside",
                    'tickfont': dict(size=10),
                },
                'bar': {'color': 'rgba(0, 0, 0, 0)'},
                'bordercolor': "white",
                'steps': [
                    {'range': [0, valores[0]], 'color': cormarcador[0]},
                    {'range': [valores[0], 100], 'color': cormarcador[2]}
                ],
                'threshold': {
                    'line': {'color': "red", 'width': 3},
                    'thickness': 0.80,
                    'value': valores[1]
                }
            },
        ))

        # Ajustar o layout
        fig_velocimetro.update_layout(
            margin=dict(l=10, r=22, t=20, b=0),
            width=None,
            height=230,
            showlegend=True,
            legend=dict(
                orientation="h",
                yanchor="bottom",
                x=0.5,
                y=1.1,
                font_size=10,
            ),
            paper_bgcolor='rgba(0, 0, 0, 0)',
            plot_bgcolor='rgba(0, 0, 0, 0)',
        )

        # Adicionar legenda
        fig_velocimetro.add_trace(go.Scatter(
            x=[""], y=[""],
            mode='lines',
            line=dict(color='DarkBlue', width=3),
            name='Aderente',
        ))

        fig_velocimetro.add_trace(go.Scatter(
            x=[""], y=[""],
            mode='lines',
            line=dict(color='red', width=3),
            name='Meta',
        ))

        # Converter o gráfico para HTML
        return fig_velocimetro.to_html(full_html=False)

    # Responsável por cacular a porcentagem do IGS
    def view_percentuais_igs(self, framework_id):
        # Total de registros no AssessmentModel relacionados ao CisModel
        total_cis = CisModel.objects.filter(assessment__framework_id=framework_id).count()

        if total_cis == 0:  # Evitar divisão por zero
            return {
                'IG1': 0,
                'IG2': 0,
                'IG3': 0,
            }
        
        counts_sim = (
            CisModel.objects
            .filter(assessment__framework_id=framework_id, resultadoCss='Aderente')  # Filtrar apenas registros com meta "Aderente"
            .values('nivel')
            .annotate(count=Count('nivel'))
        )

        igs_count = {item['nivel']: item['count'] for item in counts_sim}

        # Contar instâncias de cada nível IG
        counts = (
            CisModel.objects
            .filter(assessment__framework_id=framework_id)
            .values('nivel')
            .annotate(count=Count('nivel'))
        )

        total = {item['nivel']: item['count'] for item in counts}

        # Inicializar dicionário com zero
        percentuais = {'IG1': 0, 'IG2': 0, 'IG3': 0}

        # Calcular porcentagens para cada nível
        for item in counts:
            nivel = item['nivel']
            count = item['count']
            if nivel in percentuais:
                percentuais[nivel] = round((count / total_cis) * 100, 2)

        return percentuais, igs_count, total
    # Responsável por cacular a porcentagem dos metas dos níveis IGS
    def calcular_percentual_meta(self, framework_id):
        # Total de registros no CisModel
        total_cis = CisModel.objects.filter(assessment__framework_id=framework_id).count()

        if total_cis == 0:  # Evitar divisão por zero
            return {
                'IG1': 0,
                'IG2': 0,
                'IG3': 0,
            }

        # Contar "Aderente" para cada nível
        counts_sim = (
            CisModel.objects
            .filter(assessment__framework_id=framework_id, meta='Aderente')  # Filtrar apenas registros com meta "Aderente"
            .values('nivel')
            .annotate(count=Count('nivel'))
        )

        # Contar total de instâncias para cada nível
        counts_total = (
            CisModel.objects
            .filter(assessment__framework_id=framework_id)
            .values('nivel')
            .annotate(count=Count('nivel'))
        )

        # Criar dicionário com totais por nível
        total_por_nivel = {item['nivel']: item['count'] for item in counts_total}

        # Criar dicionário com contagem de "Sim" por nível
        sim_por_nivel = {item['nivel']: item['count'] for item in counts_sim}

        # Calcular porcentagens
        percentuais = {}
        for nivel, total in total_por_nivel.items():
            sim_count = sim_por_nivel.get(nivel, 0)  # Contagem de "Sim" ou 0
            percentuais[nivel] = round((sim_count / total) * 100, 2) if total > 0 else 0

        return percentuais

    # Respoosanvel porr calcular a porcentagem e por retornar o gráfico de radar
    def view_grafico_radar(self, framework_id):
        # Total de registros no CisModel
        total_cis = CisModel.objects.filter(assessment__framework_id=framework_id).count()

        if total_cis == 0:  # Evitar divisão por zero
            return {
                'Recover': 0,
                'Govern': 0,
                'Detect': 0,
                'Identify': 0,
                'Protect': 0,
                'Respond': 0
            }

        # Contar "Aderente" para cada função
        counts_sim_result = (
            CisModel.objects
            .filter(assessment__framework_id=framework_id, resultadoCss='Aderente')  # Filtrar apenas registros com resultado(CSS) "Aderente"
            .values('funcao')
            .annotate(count=Count('funcao'))
        )
        # Contar "Aderente" para cada meta
        counts_sim_meta = (
            CisModel.objects
            .filter(assessment__framework_id=framework_id, meta='Aderente')  # Filtrar apenas registros com meta "Aderente"
            .values('funcao')
            .annotate(count=Count('funcao'))
        )
        # Contar total de instâncias para cada nível
        counts_total = (
            CisModel.objects
            .filter(assessment__framework_id=framework_id)
            .values('funcao')
            .annotate(count=Count('funcao'))
        )
        # Criar dicionário com totais por nível
        total_por_nivel = {item['funcao']: item['count'] for item in counts_total}

        # Criar dicionário com contagem de "Sim" por nível
        sim_por_funcao_result = {item['funcao']: item['count'] for item in counts_sim_result}

        # Criar dicionário com contagem de "Sim" por nível
        sim_por_funcao_meta = {item['funcao']: item['count'] for item in counts_sim_meta}

        # Calcular porcentagens da meta 
        percentuais_meta = {}
        for funcao, total in total_por_nivel.items():
            sim_count = sim_por_funcao_meta.get(funcao, 0)  # Contagem de "Sim" ou 0
            percentuais_meta[funcao] = round((sim_count / total) * 100, 2) if total > 0 else 0

        # Calcular porcentagens do resultado
        percentuais_result = {}
        for funcao, total in total_por_nivel.items():
            sim_count = sim_por_funcao_result.get(funcao, 0)  # Contagem de "Sim" ou 0
            percentuais_result[funcao] = round((sim_count / total) * 100, 2) if total > 0 else 0  

        categorias = ['Recover','Govern','Detect', 'Identify', 'Protect', 'Respond']

        # Organizar os valores na ordem das categorias
        r_meta = [percentuais_meta.get(cat, 0) for cat in categorias]
        r_result = [percentuais_result.get(cat, 0) for cat in categorias]

        # Criar o gráfico
        fig_radar = go.Figure()

        fig_radar.add_trace(go.Scatterpolar(r=r_result,
            theta=categorias,fill='toself', name='Aderente'
        ))
       
        fig_radar.add_trace(go.Scatterpolar(r=r_meta,
            theta=categorias, fill='toself', name='Meta'
        ))

        fig_radar.update_layout(
                                polar=dict(
                                radialaxis=dict(
                                visible=True,
                                range=[0, 100]
                                )),
                                showlegend=True,
                                      font=dict(
                                            family="Arial",
                                            size=10,
                                            color='#000000'
                                ),
                                )
        # Ajustar o layout para tamanho definido
        fig_radar.update_layout(
                margin=dict(l=60, r=0, t=0, b=0),  # Margens
                width=None,
                height=230             
        )

        # Converter o gráfico para HTML 
        return fig_radar.to_html(full_html=False)
    
    # Responsavel por calcular a porcentagem e por retornar o gráfico de barra
    def view_grafico_barra_linha(self, framework_id):
        # Total de registros no CisModel
        total_cis = CisModel.objects.filter(assessment__framework_id=framework_id).count()

        if total_cis == 0:  # Evitar divisão por zero
            return {
                'Inventário e controle de ativos corporativos': 0,
                'Inventário e controle de ativos de software': 0,
                'Proteção de Dados': 0,
                'Configuração segura de ativos corporativos e software': 0,
                'Gestão de Contas': 0,
                'Gestão do Controle de Acessos': 0,
                'Gestão contínua de vulnerabilidades': 0,
                'Gestão de registros de auditoria': 0,
                'Proteções de e-mail e navegador Web': 0,
                'Defesas contra Malware': 0,
                'Recuperação de Dados': 0,
                'Gestão da Infraestrutura de Rede': 0,
                'Monitoramento e defesa da Rede': 0,
                'Conscientização sobre segurança e treinamento de competências': 0,
                'Gestão de provedor de serviços': 0,
                'Segurança de Aplicações': 0,
                'Gestão de respostas a incidentes': 0,
                'Testes de invasão': 0
            }

        # Contar "Aderente" para cada função
        counts_sim_controle = (
            CisModel.objects
            .filter(assessment__framework_id=framework_id, resultadoCss='Aderente')  # Filtrar apenas registros com resultado(CSS) "Aderente"
            .values('controle')
            .annotate(count=Count('controle'))
        )

        # Contar "Aderente" para cada meta
        counts_sim_meta = (
            CisModel.objects
            .filter(assessment__framework_id=framework_id, meta='Aderente')  # Filtrar apenas registros com meta "Aerente"
            .values('controle')
            .annotate(count=Count('controle'))
        )

        # Contar total de instâncias para cada nível
        counts_total = (
            CisModel.objects
            .filter(assessment__framework_id=framework_id)
            .values('controle')
            .annotate(count=Count('controle'))
        )      

        # Criar dicionário com totais por nível
        total_por_nivel = {item['controle']: item['count'] for item in counts_total}

        # Criar dicionário com contagem de "Sim" por nível
        sim_por_funcao_controle = {item['controle']: item['count'] for item in counts_sim_controle}

        # Criar dicionário com contagem de "Sim" por nível
        sim_por_funcao_meta = {item['controle']: item['count'] for item in counts_sim_meta}

        categorias = ["Inventário e controle <br>de ativos corporativos",
                        "Inventário e controle de <br>ativos de software",
                        "Proteção de Dados",
                        "Configuração segura de <br>ativos corporativos e software",
                        "Gestão de Contas",
                        "Gestão do Controle <br>de Acessos",
                        "Gestão contínua <br>de vulnerabilidades",
                        "Gestão de registros <br>de xauditoria",
                        "Proteções de e-mail <br>e navegador Web",
                        "Defesas contra Malware",
                        "Recuperação de Dados",
                        "Gestão da <br>Infraestrutura de Rede",
                        "Monitoramento e <br>defesa da Rede",
                        "Conscientização sobre segurança <br>e treinamento de competências",
                        "Gestão de provedor <br>de serviços",
                        "Segurança de Aplicações",
                        "Gestão de respostas <br>a incidentes",
                        "Testes de invasão"]
        categorias_limpa = [re.sub(r"<br>", "", cat).strip() for cat in categorias] # Versão limpa das categorias (removendo as tags <br>)

        y_meta = [sim_por_funcao_meta.get(cat, 0) for cat in categorias_limpa]
        y_result = [sim_por_funcao_controle.get(cat, 0) for cat in categorias_limpa]

        # Ordenar as categorias com base nos valores das barras (y_result) em ordem decrescente
        sorted_data = sorted(zip(y_result, y_meta, categorias), key=lambda x: x[0], reverse=True)
        y_result_sorted, y_meta_sorted, categorias_sorted = zip(*sorted_data)

        rodape = [self.abreviar_categoria(cat) for cat in categorias_sorted]

        fig_serie = go.Figure()

        # Adicionando o gráfico de barras
        fig_serie.add_trace(go.Bar(
                x=rodape,
                y=y_result_sorted,
                hovertemplate="%{y} em %{x}<extra></extra>",
                name='Aderente',
                text=y_result_sorted,
                textposition='inside',  # Posição do texto
                marker=dict(color='RoyalBlue')  # Define a cor das barras
        ))

        # Adicionando o gráfico de linha
        fig_serie.add_trace(go.Scatter(
            x=rodape[:len(y_result_sorted)],  # Ajustar o x para corresponder ao comprimento dos y
            y=y_meta_sorted,
            name='Meta',
            hovertemplate="%{customdata} de %{y}<extra></extra>",
            customdata=y_result_sorted,  # Valores da barra associados aos pontos da linha
            text=y_meta_sorted,
            textposition='top center',  # Posição do texto
            mode='lines+markers+text', 
            line=dict(color='darkblue'),
            yaxis='y2'
        ))

        # Configurações adicionais do layout
        fig_serie.update_layout(
                plot_bgcolor='rgba(0, 0, 0, 0)',  # Fundo do gráfico transparente
                margin=dict(l=0, r=0, t=0, b=0),  # Margens
                height=300,
                width=None,
                font=dict(
                    family="Arial",
                    size=9,
                    color='#000000'
                ),
                yaxis=dict(
                    visible=False,      # Oculta o eixo Y
                    range=[0, (max(y_meta_sorted)+10)],  # Ajusta o intervalo do eixo Y
                    dtick=1.0                # Define o intervalo dos ticks
                ),
                yaxis2=dict(
                    range=[0, (max(y_meta_sorted)+20)],  # Ajusta o intervalo do eixo Y para a linha
                    overlaying='y',  # Sobrepõe ao eixo Y primário
                    side='right'     # Coloca o eixo Y2 do lado direito
                ),
                showlegend=True,
                legend=dict(
                        yanchor="top",         # Ancoragem na parte inferior
                        x=0,                # Orientação horizontal
                        y=0.9,                 # Ajusta a posição vertical da legenda
                )
        )

        # Converter o gráfico para HTML
        return fig_serie.to_html(full_html=False)

    # Responsável por criar o gráfico de linha
    def view_grafico_linha(self, request, framework_id):
        # Obter o parâmetro 'limite' da requisição (padrão para 3 se não fornecido)
        limite = int(request.GET.get('limite', 12))
        # Filtrar apenas as instâncias relacionadas ao CisModel com status 'Concluído'
        assessments_cis = AssessmentModel.objects.filter(framework__id=framework_id, framework__nome__icontains='cis', status='Concluído').order_by('-data_upload')[:limite]
        # Total de registros filtrados
        total_cis = assessments_cis.count()

        if total_cis > 0:
            # Calcular os percentuais de meta e resultado (remover o % e converter para float)
            percentual_meta = [float(value.replace('%', '')) for value in assessments_cis.values_list('meta', flat=True)]
            percentual_resultado = [float(value.replace('%', '')) for value in assessments_cis.values_list('resultado', flat=True)]
            percentual_meta.reverse()
            percentual_resultado.reverse()


            # Coletar as datas de upload no formato desejado
            data_meta = [data.strftime("%d/%m/%Y") for data in assessments_cis.values_list('data_upload', flat=True)]
            data_meta.reverse()
            data_resultado = data_meta.copy()
        else:
            percentual_meta = []
            percentual_resultado = []
            data_meta = []
            data_resultado = []

        # Criar o gráfico
        fig_linha = go.Figure()
        fig_linha.add_trace(go.Scatter(
            x=data_meta,
            y=percentual_meta,
            name='Meta',
            hovertemplate="%{y}<extra></extra>",
            text=[f"{p}%" for p in percentual_meta],
            textposition='top center',
            mode='lines+markers+text',
            line=dict(color='darkblue')
        ))
        fig_linha.add_trace(go.Scatter(
            x=data_resultado,
            y=percentual_resultado,
            name='Nota',
            hovertemplate="%{y}<extra></extra>",
            text=[f"{p}%" for p in percentual_resultado],
            textposition='top center',
            mode='lines+markers+text',
            line=dict(color='RoyalBlue')
        ))

        # Atualizar o layout
        fig_linha.update_layout(
            plot_bgcolor='rgba(0, 0, 0, 0)',
            xaxis=dict(visible=True),
            yaxis_title='CIS Controls v8.1',
            yaxis=dict(visible=True, showticklabels=False, range=[0, 200], tick0=1, dtick=10),
            margin=dict(l=0, r=0, t=1, b=0),
            height=200,
            font=dict(family="Arial", size=9),
            legend=dict(yanchor="top", x=0.9, y=1.0),
        )

        # Converter o gráfico para HTML
        return fig_linha.to_html(full_html=False, config={'responsive': True})
    
    # Responsável por contar os tipor de ativos
    def view_card_tipo_ativo(self, framework_id):
        total_cis = CisModel.objects.filter(assessment__framework_id=framework_id).count()

        if total_cis == 0:  # Evitar divisão por zero
            return {
                'Applications': 0,
                'Data': 0,
                'Devices': 0,
                'Users': 0,
                'Network': 0,
                'nan': 0
            }

        # Contar "Aderente" para cada função
        counts_sim = (
            CisModel.objects
            .filter(assessment__framework_id=framework_id, resultadoCss='Aderente')  # Filtrar apenas registros com resultado(CSS) "Aderente"
            .values('tipoAtivo')
            .annotate(count=Count('tipoAtivo'))
        )

        # Contar total de instâncias para cada nível
        counts_total = (
            CisModel.objects
            .filter(assessment__framework_id=framework_id)
            .values('tipoAtivo')
            .annotate(count=Count('tipoAtivo'))
        )

        # Criar dicionário com totais por nível
        total_por_nivel = {item['tipoAtivo']: item['count'] for item in counts_total}

        # Criar dicionário com contagem de "Sim" por nível
        sim_por_ativo = {item['tipoAtivo']: item['count'] for item in counts_sim}

        return total_por_nivel, sim_por_ativo
    # FIM DOS GRÁFICOS DO ASSESSMENT ##############################################################

    # INÍCIO DAS DOS GRÁFICOS DO PLANO DE AÇÃO ################################################
    # Responsável por mostra os quantidades de ações cadastradas do plano de ação
    def view_qtd_acoes_cad(self, framework_id, assessment_id):
        plano_acao = PlanoAcaoModel.objects.filter(assessment_id=assessment_id, assessment__framework_id=framework_id, nome__icontains='cis')

        # Soma os valores de 'acoes_cad' das instâncias filtradas
        total_acoes_cad = plano_acao.aggregate(total=Sum('acoes_cad'))['total'] or 0

        return total_acoes_cad

    # Responsável por mostra o percentual de ações cadastradas do plano de ação já concluidas
    def view_porcentagem_acoes_cad(self, framework_id, assessment_id):
        plano_acao = PlanoAcaoModel.objects.filter(assessment_id=assessment_id, assessment__framework_id=framework_id, nome__icontains='cis')

        qtn_plano_acao = PlanoAcaoModel.objects.filter(assessment_id=assessment_id, assessment__framework_id=framework_id, nome__icontains='cis').count()

        por_plano_acao = plano_acao.aggregate(total=Sum('conclusao'))['total']

        percentual_concluido = (por_plano_acao / qtn_plano_acao)
        
        return percentual_concluido

    # Responsável por mostra o gráfico de pizza do status do plano de ação
    def view_grafico_pizza_conclusao(self, framework_id, assessment_id):
        plano_acao = PlanoAcaoModel.objects.filter(assessment_id=assessment_id, assessment__framework_id=framework_id, nome__icontains='cis')

        cad_planos = CadPlanodeAcaoModel.objects.filter(planoacao__in=plano_acao)

        # Conta os registros para cada status
        total_nao_iniciado = cad_planos.filter(status='A iniciar').count()
        total_andamento = cad_planos.filter(status='Em andamento').count()
        total_finalizado = cad_planos.filter(status='Concluído').count()
        total_atrasado = cad_planos.filter(status='Atrasado').count()

        # Verifica para evitar divisão por zero
        total_plano_acao = plano_acao.count()
        if total_plano_acao == 0:
            return {
                'A iniciar': 0,
                'Em andamento': 0,
                'Concluído': 0,
                'Atrasado': 0
            }

        status = ['Não iniciado', 'Em andamento', 'Atrasado', 'Finalizado']
        valores = [total_nao_iniciado, total_andamento, total_atrasado, total_finalizado]
        cormarcador = ["#F4a460","#fffacd", "#d3d3d3", "#90ee90"]
        
        fig_roda = go.Figure(data=go.Pie(labels=status,
                                       values=valores, 
                                       marker_colors=cormarcador,
                                       hole=0.5, # furo do centro do grafico
                                       pull=[0, 0, 0, 0])) # distancia entre fatias

        # Rótulos
        fig_roda.update_traces(textposition="inside", textinfo="percent")

        # Legenda
        fig_roda.update_layout(
                        legend=dict(
                        orientation="h",          # Orientação horizontal
                        yanchor="bottom",         # Ancoragem na parte inferior
                        x=0.1,                    # Posiciona no centro
                        y=-0.4,                   # Ajusta a posição vertical da legenda
                        font_size=10,
                    )
        )

        # Ajustar o layout para tamanho definido. testes: autosize=True/height='50%',
        fig_roda.update_layout(
               margin=dict(l=0, r=0, t=2, b=0),  # Margens
               height=200,
               width=None
        )

        # Converter o gráfico para HTML
        return fig_roda.to_html(full_html=False, config={'responsive': True})
    # FIM DAS DOS GRÁFICOS DO PLANO DE AÇÃO ################################################

    # INÍCIO DOS GRÁFICOS DE CUSTO DO PLANO DE AÇÃO ############################################
    # Resposánvel por somar todos os valores no cuso estimado do plano de ação
    def view_custo_estimado(self, framework_id, assessment_id):
        plano_acao = PlanoAcaoModel.objects.filter(assessment_id=assessment_id, assessment__framework_id=framework_id, nome__icontains='cis')

        # Soma os valores de 'custo_estimado' das instâncias filtradas
        total_custo_estimado = plano_acao.aggregate(total=Sum('custo_estimado'))['total'] or 0

        return total_custo_estimado
    
    # Responsável por mostra o gráfico de pizza do custo estimado por função do plano de ação
    def view_grafico_pizza_custo_estimado(self, framework_id, assessment_id):
        funcoes = [
            'Govern', 
            'Identify', 
            'Protect', 
            'Detect', 
            'Respond', 
            'Recovery'
        ]

        subcontrole_somas = CadPlanodeAcaoModel.objects.filter(planoacao__assessment__id=assessment_id, planoacao__assessment__framework_id=framework_id).values('subcontrole').annotate(total=Sum('quanto'))

        controle_subcontrole_map = {
            funcao: list(CisModel.objects.filter(funcao=funcao).values_list('subConjunto', flat=True))
            for funcao in funcoes
        }

        controle_somas = {funcao: 0 for funcao in funcoes}
        for item in subcontrole_somas:
            subcontrole = item['subcontrole']
            total = item['total']

            for funcao, subcontroles in controle_subcontrole_map.items():
                if subcontrole in subcontroles:
                    controle_somas[funcao] += total
                    break

        valores = [controle_somas[funcao] for funcao in funcoes]

        cormarcador = ["DarkBlue", "RoyalBlue", "blue", "LightBlue", "SteelBlue", "SkyBlue"]
        
        # Combinar status e valores para exibição
        labels = [f"{s}<br>R$ {v:,.0f}" for s, v in zip(funcoes, valores)]  # Formatação dos valores

         # Criação do gráfico de pizza
        fig_pizza = go.Figure(data=go.Pie(
            labels=labels,  # Rótulos fora do gráfico
            values=valores,  # Valores a serem utilizados
            marker_colors=cormarcador,
            hole=0,  # Furo do centro do gráfico
            pull=[0, 0, 0, 0, 0, 0],  # Distância entre fatias
            textinfo='value',  # Exibir valores dentro das fatias
            textposition='inside',  # Posição do texto dentro das fatias
        ))
    
        # Ajustar rótulos e valores
        fig_pizza.update_traces(
            textposition='outside',  # Rótulos fora do gráfico
            textinfo='label',  # Exibir de fora das fatias
            textfont=dict(size=8)  # Tamanho da fonte dos rótulos
        )
    
        # Ajustar o layout
        fig_pizza.update_layout(
            margin=dict(l=0, r=0, t=2, b=0),  # Margens
            height=300,
            width=None
        )       
                                
        # Ajustar o layout para tamanho definido. testes: autosize=True/height='50%',
        fig_pizza.update_layout(
               showlegend=False,  # não mostrar legenda
               margin=dict(l=0, r=0, t=2, b=0),  # Margens
               height=200,
               width=None
        )

        # Converter o gráfico para HTML
        return fig_pizza.to_html(full_html=False, config={'responsive': True})
    
    # Resposável por calcular a soma de custos de cada projeto
    def calcular_soma_custos_de_cada_projeto(self, framework_id, assessment_id):
        categorias = ["Governança e <br>Estratégia",
                        "Gestão de Riscos",
                        "Gestão de Terceiros",
                        "Privacidade",
                        "Gestão de Identidade <br>e Acessos",
                        "Gestão de Ativos",
                        "Security Mobile <br>(computadores e <br>celulares)",
                        "Cloud Security",
                        "Proteção da <br>Infraestrutura",
                        "Gestão de <br>Conformidades",
                        "Gestão de <br>Vulnerabilidades",
                        "Gestão de Patch",
                        "Desenvolvimento <br>Seguro",
                        "Gestão de Crise e <br>Continuidade do Negócio",
                        "Gestão de Incidentes",
                        "Plano de Backup e <br>Recuperação",
                        "SOC",
                        "Conscientização"
                    ]
        categorias_limpa = [re.sub(r"<br>", "", cat).strip() for cat in categorias]
        
        projetos_somas = (
            CadPlanodeAcaoModel.objects.filter(planoacao__assessment__id=assessment_id, planoacao__assessment__framework_id=framework_id)
            .values('projeto')
            .annotate(total=Sum('quanto'))
        )

        controle_somas = {controle: 0 for controle in categorias_limpa}
        for item in projetos_somas:
            projeto_nome = item['projeto']  # Nome do projeto
            total = item['total']          # Total associado ao projeto


            for controle, soma_atual in controle_somas.items():
                # Verifica se o nome do controle está no nome do projeto
                if controle in projeto_nome:  # Agora 'controle' e 'projeto_nome' são strings
                    controle_somas[controle] += total  # Atualiza o total para o controle
                    break

        valores_barra = [controle_somas[controle] for controle in categorias_limpa]

        return categorias, categorias_limpa, controle_somas, valores_barra
    
    # Responsanvel por somar todos os valores no cuso estimado do plano de ação por projeto
    def view_grafico_barra_acao_projeto(self, framework_id, assessment_id):
        categorias, categorias_limpa, controle_somas, valores_barra = self.calcular_soma_custos_de_cada_projeto(framework_id, assessment_id)

        valores_barra_e_categorias = sorted(
            zip(categorias, controle_somas.values()), 
            key=lambda x: x[1], 
            reverse=True
        )

        categorias_ordenadas, valores_barra_ordenados = zip(*valores_barra_e_categorias)

        fig_barra = go.Figure()

        # Adicionando o gráfico de barras
        fig_barra.add_trace(go.Bar(
                x=categorias_ordenadas,
                y=valores_barra_ordenados,
                hovertemplate="%{y} em %{x}<extra></extra>",
                name='Custo',
                text=valores_barra_ordenados,
                textposition='outside',  # Posição do texto
                marker=dict(color='RoyalBlue')  # Define a cor das barras
        ))

        
        # Configurações adicionais do layout
        fig_barra.update_layout(
                plot_bgcolor='rgba(0, 0, 0, 0)',  # Fundo do gráfico transparente
                margin=dict(l=0, r=0, t=0, b=0),  # Margens
                height=260,
                width=None,
                font=dict(
                    family="Arial",
                    size=9,
                    color='#000000'
                ),
                yaxis=dict(
                    visible=False,  # Oculta o eixo Y  
                    range=[0, 100000],  # O GRÁFICO FOI PLOTADO PENSANDO NOS VALORES ENTRE R$0,00 A R$100.000,00
                    dtick=0.5                # Define o intervalo dos ticks
                ),
                showlegend=True,
                legend=dict(
                        yanchor="top",         # Ancoragem na parte superior
                        x=0,                # Orientação horizontal
                        y=0.9,                 # Ajusta a posição vertical da legenda
                )
        )

        # Converter o gráfico para HTML 
        return fig_barra.to_html(full_html=False)
    # FIM DOS GRÁFICOS DE CUSTO DO PLANO DE AÇÃO ############################################

    def get(self, request, framework_id, assessment_id):
        assessments = AssessmentModel.objects.all()

        # INÍCIO GRÁFICOS DO ASSESSMENT ######################################################     
        # Gráfico de velocímetro
        grafico_velocimetro_html = self.view_grafico_velocimetro(framework_id)

        # Percentuais IGs
        percentuais_igs, count_igs, total_igs = self.view_percentuais_igs(framework_id)
        percentuais_meta = self.calcular_percentual_meta(framework_id)
        
        # Gráfico Radar ref:https://plotly.com/python/radar-chart/
        grafico_radar_html = self.view_grafico_radar(framework_id)
        
        # Gráfico serie temporal com histograma 
        grafico_barra_linha_html = self.view_grafico_barra_linha(framework_id)

        # Gráfico de linha
        grafico_linha_html = self.view_grafico_linha(request, framework_id)

        # Card do tipo de ativo
        total_tipo_ativo, card_tipo_ativo = self.view_card_tipo_ativo(framework_id)
        # FIM GRÁFICOS DO ASSESSMENT ######################################################

        # INÍCIO GRÁFICOS DO PLANO DE AÇÃO ##################################################
        # Quantidade de ações cadastradas
        qtd_acoes_cad = self.view_qtd_acoes_cad(framework_id, assessment_id)

        # Porcentagem de ações cadastradas concluidas
        percentual_acoes_cad = self.view_porcentagem_acoes_cad(framework_id, assessment_id)

        # Gráfico de pizza dos status do Plano de ação 
        grafico_pizza_conclusao_html = self.view_grafico_pizza_conclusao(framework_id, assessment_id)
        # FIM GRÁFICOS DO PLANO DE AÇÃO ################################################

        # INÍCIO GRÁFICOS DE CUSTO DO PLANO DE AÇÃO #######################################
        soma_custo_estimado = self.view_custo_estimado(framework_id, assessment_id)

        # Gráfico de pizza custos do Plano de ação
        grafico_pizza_custo_estimado_html = self.view_grafico_pizza_custo_estimado(framework_id, assessment_id)

        # Gráfico de barra de custo estimado das ações por controle
        grafico_barra_acao_projeto_html = self.view_grafico_barra_acao_projeto(framework_id, assessment_id)
        # FIM GRÁFICOS DE CUSTO DO PLANO DE AÇÃO #######################################
              
        ##Grafico Barra Responsavel
        x = ['João', 'Luis', 'Jose', 'Maria', 'Pedro']
        status_r = ['não iniciado', 'andamento', 'atrasado', 'finalizado']
        fig_barra_r = go.Figure()
        
        # Adiciona as barras
        fig_barra_r.add_trace(go.Bar(x=x, y=[2, 5, 1, 9, 1], text=[2, 5, 1, 9, 1], textposition='inside', marker=dict(color='#F4a460'),  name=status_r[0] ))
        fig_barra_r.add_trace(go.Bar(x=x, y=[1, 4, 9, 16, 1], text=[1, 4, 9, 12, 1], textposition='inside', marker=dict(color='#fffacd'),  name=status_r[1] ))  # Cor da quarta série
        fig_barra_r.add_trace(go.Bar(x=x, y=[6, 8, 4.5, 8, 1], text=[6, 8, 4.5, 8, 1], textposition='inside', marker=dict(color='#d3d3d3'), name=status_r[2] ))
        fig_barra_r.add_trace(go.Bar(x=x, y=[2, 4, 8, 1, 1], text=[2, 4, 8, 1, 1], textposition='inside', marker=dict(color='#90ee90'), name=status_r[3] ))
   
       
        # Configuração do layout
        fig_barra_r.update_layout(
            barmode='stack',
            xaxis={'categoryorder': 'category ascending'},
            yaxis={'showticklabels': False},  # Oculta os rótulos do eixo Y
            showlegend=True,            
            legend=dict(
                        orientation="h",          # Orientação horizontal
                        yanchor="bottom",         # Ancoragem na parte inferior
                        x=0,                    # Posiciona no centro
                        y=1.0,                   # Ajusta a posição vertical da legenda
                        font_size=10,
            ),
            margin=dict(l=5, r=0, t=2, b=2),  # Margens
            height=260,        # Ajusta a altura do gráfico
            width=None,        # Ajusta a largura do gráfico
            font=dict(
                    family="Arial",
                    size=10
               ),
            plot_bgcolor='rgba(0, 0, 0, 0)'  # Fundo do gráfico transparente
        )

        # Converter o gráfico para HTML
        grafico_barra_r_html = fig_barra_r.to_html(full_html=False,config={'responsive': True})
    
        context = {
            'assessments': assessments,
            # INÍCIO GRÁFICOS DO ASSESSMENT 
            'grafico_velocimetro_html': grafico_velocimetro_html,
            'percentuais_igs': percentuais_igs,
            'count_igs': count_igs,
            'total_igs': total_igs,
            'percentuais_meta': percentuais_meta,
            'grafico_radar_html': grafico_radar_html,
            'grafico_linha_html': grafico_linha_html,
            'grafico_barra_linha_html': grafico_barra_linha_html,
            'card_tipo_ativo': card_tipo_ativo,
            'total_tipo_ativo': total_tipo_ativo,
            # FIM GRÁFICOS DO ASSESSMENT 
            # INÍCIO GRÁFICOS DO PLANO DE AÇÃO 
            'qtd_acoes_cad': qtd_acoes_cad,
            'percentual_acoes_cad': percentual_acoes_cad,
            'grafico_pizza_conclusao_html': grafico_pizza_conclusao_html,
            # FIM GRÁFICOS DO PLANO DE AÇÃO
            # INÍCIO GRÁFICOS DE CUSTO DO PLANO DE AÇÃO
            'soma_custo_estimado': soma_custo_estimado,
            'grafico_pizza_custo_estimado_html': grafico_pizza_custo_estimado_html,
            'grafico_barra_acao_projeto_html': grafico_barra_acao_projeto_html,
            # FIM GRÁFICOS DO PLANO DE AÇÃO
            'grafico_barra_r': grafico_barra_r_html,         
        }

        return render(request, self.template_name, context)
