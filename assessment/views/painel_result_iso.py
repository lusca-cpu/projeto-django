from django.db.models import Count, Sum, Q
from django.shortcuts import render
from django.views import View

from ..models import AssessmentModel, CadPlanodeAcaoModel, IsoModel, PlanoAcaoModel

import plotly.graph_objects as go

# Função para renderizar a página painel de resultados ISO 'paginas/painel_result_iso.html
class PaineldeResultadosIso(View):
    template_name = 'paginas/painel_result_iso.html'

    # INÍCIO GRÁFICOS DO ASSESSMENT ########################################################
    # Responsável pela criação do gráfico de velocímetro
    def view_grafico_velocimetro(self, framework_id):
        # Filtrar apenas as instâncias relacionadas ao IsoModel
        acao_iso = IsoModel.objects.filter(assessment__framework_id=framework_id).count()

        soma_meta = IsoModel.objects.filter(assessment__framework_id=framework_id, meta="Conforme").count()
        soma_resultado = IsoModel.objects.filter(assessment__framework_id=framework_id, notaCss="Conforme").count()

        # Dados para o gráfico
        valores = [soma_resultado, soma_meta]
        cormarcador = ["darkblue", "RoyalBlue", "LightBlue"]    
        
        fig_velocimetro = go.Figure(go.Indicator(
            mode="gauge+number",
            value=valores[1],
            number={
                'font': {'color': "red", 'size': 16},
            },
            gauge={
                'axis': {
                    'range': [0, acao_iso],
                    'tickcolor': "blue",
                    'ticks': "inside",
                    'tickfont': dict(size=10),
                },
                'bar': {'color': 'rgba(0, 0, 0, 0)'},
                'bordercolor': "white",
                'steps': [
                    {'range': [0, valores[0]], 'color': cormarcador[0]},
                    {'range': [valores[0], acao_iso], 'color': cormarcador[2]}
                ],
                'threshold': {
                    'line': {'color': "red", 'width': 3},
                    'thickness': 0.80,
                    'value': valores[1]
                }
            },
        ))

        # Ajustar o layout para tamanho definido
        fig_velocimetro.update_layout(
                 margin=dict(l=15, r=0, t=5, b=0),  # Margens
                 width=255,
                 height=200, 
                 showlegend=True,
                 legend=dict(
                        orientation="v",          # Orientação vertical
                        x=0.8,                    # Posiciona no centro
                        y=1.0,                    # Ajusta a posição vertical da legenda
                        font_size=10,
                    ),
                 paper_bgcolor='rgba(0, 0, 0, 0)',  # Fundo transparente
                 plot_bgcolor='rgba(0, 0, 0, 0)',    # Fundo do gráfico transparente
        )
     
        # Adicionar traces invisíveis para a legenda
        fig_velocimetro.add_trace(go.Scatter(
            x=[""], y=[""],
            mode='lines',
            line=dict(color='DarkBlue', width=3),
            name='Conforme',
            
        ))

        fig_velocimetro.add_trace(go.Scatter(
            x=[""], y=[""],
            mode='lines',
            line=dict(color='red', width=3),
            name='Meta',
        ))

        # Converter o gráfico para HTML
        return fig_velocimetro.to_html(full_html=False)
    
    # Reponsável por contar quantos controles Parcialmente conforme e Não conforme 
    def view_count_parcial_nao_conformes(self, framework_id):
        # Total de registros no AssessmentModel relacionados ao IsoModel
        total_iso = IsoModel.objects.filter(assessment__framework_id=framework_id).count()

        if total_iso == 0:  # Evitar divisão por zero
            return {
                'Parcialmente': 0,
                'Não': 0,
            }

        # Contar "Parcialmente" e "Não" na coluna notaCss
        parcial_notaCss = IsoModel.objects.filter(assessment__framework_id=framework_id, notaCss="Parcialmente Conforme").count()
        nao_notaCss = IsoModel.objects.filter(assessment__framework_id=framework_id,notaCss="Não conforme").count()

        # Contar "Parcialmente" e "Não" na coluna meta
        parcial_meta = IsoModel.objects.filter(meta="Parcialmente Conforme").count()
        nao_meta = IsoModel.objects.filter(meta="Não conforme").count()

        # Retornar os resultados separados
        return {
            'Total': total_iso,
            'Parcialmente_notaCss': parcial_notaCss,
            'Nao_notaCss': nao_notaCss,
            'Parcialmente_meta': parcial_meta,
            'Nao_meta': nao_meta,
        }
    
    # Reponsável por contar quantos controles Parcialmente
    def view_count_prioridade_controle(self, framework_id):
        # Total de registros no AssessmentModel relacionados ao IsoModel
        total_iso = IsoModel.objects.filter(assessment__framework_id=framework_id).count()

        if total_iso == 0:  # Evitar divisão por zero
            return {
                'Mandatório': 0,
                'Good to have': 0,
                'Não': 0,
            }

        # Contar "Parcialmente" e "Não" na coluna notaCss
        mandatorio = IsoModel.objects.filter(assessment__framework_id=framework_id,prioControle="Mandatório").count()
        good_to_have = IsoModel.objects.filter(assessment__framework_id=framework_id, prioControle="Good to have").count()
        nao = IsoModel.objects.filter(assessment__framework_id=framework_id, prioControle="Não").count()

        # Retornar os resultados separados
        return {
            'Total': total_iso,
            'Mandatório': mandatorio,
            'Good_to_have': good_to_have,
            'Não': nao,
        }

    # Responsável por mostrar no grafico de quantos resultados possuem 
    def view_grafico_barra_nota_secao(self, framework_id):
        ##Grafico Barra Nota seção
        x = ['Política de Segurança <br>da informação', 
                'Organizando a Segurança <br>da informação',
                'Gestão de ativos', 
                'Segurança de <br>recursos humanos', 
                'Áreas seguras', 
                'Procedimentos e <br>responsabilidades operacionais', 
                'Requisitos do <br>negócio', 
                'Requisitos de <br>segurança de sistemas', 
                'Notificação', 
                'Aspectos da gestão <br>de continuidade',
                'Conformidade com <br>requisitos legais']

        status_r = ['Conforme', 'Conforme parcialmente', 'Não conforme', 'Total']
        fig_barra_nota = go.Figure()
        
        # Adiciona as barras
        fig_barra_nota.add_trace(go.Bar(x=x, y=[2, 5, 1, 9, 2, 5, 1, 9, 2, 5, 1], text=[2, 5, 1, 9, 2, 5, 1, 9, 2, 5, 1], textposition='inside', marker=dict(color='DarkBlue'),  name=status_r[0] ))
        fig_barra_nota.add_trace(go.Bar(x=x, y=[1, 4, 9, 15, 1, 4, 9, 15, 1, 4, 9], text=[1, 4, 9, 15, 1, 4, 9, 15, 1, 4, 9], textposition='inside', marker=dict(color='RoyalBlue'),  name=status_r[1] ))  
        fig_barra_nota.add_trace(go.Bar(x=x, y=[6, 8, 4.5, 8, 6, 8, 4.5, 8, 6, 8, 4.5], text=[6, 8, 4.5, 8, 6, 8, 4.5, 8, 6, 8, 4.5], textposition='inside', marker=dict(color='LightBlue'), name=status_r[2] ))
                
        # Configuração do layout
        fig_barra_nota.update_layout(
            barmode='stack',
            xaxis={'categoryorder': 'category descending'},  #Ordem do maior para o menor
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
        return fig_barra_nota.to_html(full_html=False,config={'responsive': True})

    # Responsável por criar o gráfico de linha
    def view_grafico_linha(self, request, framework_id):
        limite = int(request.GET.get('limite', 12))
        # Filtrar apenas as instâncias relacionadas ao CisModel
        assessments_iso = AssessmentModel.objects.filter(assessment__framework_id=framework_id, framework__nome__icontains='iso', status='Concluído').order_by('-data_upload')[:limite]

        # Total de registros filtrados
        total_iso = assessments_iso.count()

        if total_iso > 0:
            # Calcular os percentuais de meta e resultado (remover o % e converter para float)
            percentual_meta = [float(value.replace('%', '')) for value in assessments_iso.values_list('meta', flat=True)]
            percentual_resultado = [float(value.replace('%', '')) for value in assessments_iso.values_list('resultado', flat=True)]
            percentual_meta.reverse()
            percentual_resultado.reverse()


            # Coletar as datas de upload no formato desejado
            data_meta = [data.strftime("%d/%m/%Y") for data in assessments_iso.values_list('data_upload', flat=True)]
            data_meta.reverse()
            data_resultado = data_meta.copy()  # Supondo que as datas sejam as mesmas
        else:
            percentual_meta = []
            percentual_resultado = []
            data_meta = []
            data_resultado = []

        # Criar o gráfico eixos x e y
        fig_linha = go.Figure()
        
        fig_linha.add_trace(go.Scatter(
                        x=data_meta, 
                        y=percentual_meta,
                        name='Meta',
                        hovertemplate="%{y}<extra></extra>",
                        text=[f"{p}%" for p in percentual_meta],  # Adiciona o símbolo de % aos rótulos
                        textposition='top center',  # Posição do texto
                        mode='lines+markers+text',
                        line=dict(color='darkblue')
        ))
        fig_linha.add_trace(go.Scatter(
                        x=data_resultado, 
                        y=percentual_resultado,
                        name='Nota',
                        hovertemplate="%{y}<extra></extra>",
                        text=[f"{p}%" for p in percentual_resultado],
                        textposition='top center',  # Posição do texto
                        mode='lines+markers+text',
                        line=dict(color='RoyalBlue')
        ))
        # Atualizar o layout
        fig_linha.update_layout(
            plot_bgcolor='rgba(0, 0, 0, 0)',  # Fundo do gráfico transparente
            
            xaxis=dict(
                visible=True,# Oculta o eixo x
            ),
            yaxis_title='ISO 27000',  # Título do eixo Y
            yaxis=dict(
                visible=True,   # Oculta o eixo Y
                showticklabels=False,   # Oculta os valores dos ticks
                range=[0, 200],        # Ajuste os valores conforme necessário
                tick0=1,  # Valor inicial para os ticks
                dtick=10   # Espaçamento entre os ticks
            ),
            margin=dict(l=0, r=0, t=1, b=0),
            height=200,
            width=None,
            font=dict(
                family="Arial",
                size=9
            ),
            legend=dict(
                yanchor="top",         # Ancoragem na parte inferior
                x=0.9,                # Orientação horizontal
                y=1.0,                 # Ajusta a posição vertical da legenda
            )
        )
        
        # Converter o gráfico para HTML
        return fig_linha.to_html(full_html=False, config={'responsive': True})
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
        plano_acao = PlanoAcaoModel.objects.filter(assessment_id=assessment_id, assessment__framework_id=framework_id, nome__icontains='iso')

        qtn_plano_acao = PlanoAcaoModel.objects.filter(assessment_id=assessment_id, assessment__framework_id=framework_id, nome__icontains='iso').count()

        por_plano_acao = plano_acao.aggregate(total=Sum('conclusao'))['total']

        percentual_concluido = (por_plano_acao / qtn_plano_acao)
        
        return percentual_concluido

    # Responsável por mostra o gráfico de pizza do status do plano de ação
    def view_grafico_pizza_conclusao(self, framework_id, assessment_id):
        plano_acao = PlanoAcaoModel.objects.filter(assessment_id=assessment_id, assessment__framework_id=framework_id, nome__icontains='iso')

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
        plano_acao = PlanoAcaoModel.objects.filter(assessment_id=assessment_id, assessment__framework_id=framework_id, nome__icontains='iso')

        # Soma os valores de 'custo_estimado' das instâncias filtradas
        total_custo_estimado = plano_acao.aggregate(total=Sum('custo_estimado'))['total'] or 0

        return total_custo_estimado
    # FIM DOS GRÁFICOS DE CUSTO DO PLANO DE AÇÃO ############################################
    
    def get(self, request, framework_id, assessment_id):
        assessments = AssessmentModel.objects.all()

        # INÍCIO GRÁFICOS DO ASSESSMENT ######################################################     
        # Gráfico de velocímetro
        grafico_velocimetro_html = self.view_grafico_velocimetro(framework_id)

        # Gráfico de parcialmente e não conformes
        cont_parcial_nao_conformes = self.view_count_parcial_nao_conformes(framework_id)

        # Gráfico de prioridade de controle
        cont_prioridade_controle = self.view_count_prioridade_controle(framework_id)

        # Gráfico de barra de nota 
        grafico_barra_nota_secao_html = self.view_grafico_barra_nota_secao(framework_id)

        # Gráfico de linha
        grafico_linha_html = self.view_grafico_linha(request, framework_id)
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
        # FIM GRÁFICOS DE CUSTO DO PLANO DE AÇÃO #########################################

        ## Grafico pizza
        # Dados
        status = [
            'Resposta<br>Incidentes', 
            'SOC', 
            'GVUL', 
            'Proteção<br>Dados', 
            'Gestão<br>Riscos', 
            'Treinamento<br>Segurança'
         ]
        valores = [67000, 85000, 65000, 58000, 50000, 48000]  
        cormarcador = ["DarkBlue", "RoyalBlue", "blue", "LightBlue", "SteelBlue", "SkyBlue"]
        
        # Combinar status e valores para exibição
        labels = [f"{s}<br>R$ {v:,.0f}" for s, v in zip(status, valores)]  # Formatação dos valores

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
    
        # Converter o gráfico para HTML
        grafico_pizza_html = fig_pizza.to_html(full_html=False, config={'responsive': True})            
                                
        # Ajustar o layout para tamanho definido. testes: autosize=True/height='50%',
        fig_pizza.update_layout(
               showlegend=False,  # não mostrar legenda
               margin=dict(l=0, r=0, t=2, b=0),  # Margens
               height=200,
               width=None
        )

        # Converter o gráfico para HTML
        grafico_pizza_html = fig_pizza.to_html(full_html=False, config={'responsive': True})
        
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
        
        ## Gráfico de Barras
        categoriasb = ["Contexto organizacional", 
                        "Estratégia de <br> gerenciamento de riscos", 
                        "Papéis,responsabilidades,<br>autoridades", 
                        "Política", 
                        "Supervisão", 
                        "Gestão de riscos <br> cadeia suprimentos", 
                        "Gestão de <br>ativos", 
                        "Avaliação de Riscos", 
                        "Melhoria", 
                        "Gestão de <br>identidade",
                        "Concientização", 
                        "Segurança de <br> dados",
                        "Segurança de <br> plataforma",
                        "Resiliência da <br> infraestrutura",
                        "Monitoramento", 
                        "Análise de eventos", 
                        "Gestão de <br>incidentes", 
                        "Análise de incidentes", 
                        "Relatório de incidentes", 
                        "Mitigação", 
                        "Plano de incidentes", 
                        "Comunicação de <br> Recuperação"]
        valores_barrab = [100, 200, 300, 400, 500, 600, 70, 800, 900, 200, 500, 100, 200, 300, 30, 30, 30, 30, 300, 300, 300, 300]
        fig_barra = go.Figure()

        # Adicionando o gráfico de barras
        fig_barra.add_trace(go.Bar(
                x=categoriasb,
                y=valores_barrab,
                hovertemplate="%{y} em %{x}<extra></extra>",
                name='Custo',
                text=valores_barrab,
                textposition='outside',  # Posição do texto
                marker=dict(color='RoyalBlue')  # Define a cor das barras
        ))
        
        # Configurações adicionais do layout
        fig_barra.update_layout(
                plot_bgcolor='rgba(0, 0, 0, 0)',  # Fundo do gráfico transparente
                margin=dict(l=0, r=0, t=0, b=0),  # Margens
                height=270,
                width=None,
                font=dict(
                    family="Arial",
                    size=9,
                    color='#000000'
                ),
                yaxis=dict(
                    visible=False,  # Oculta o eixo Y  
                    range=[0,1000],   # Ajusta o intervalo do eixo Y
                    dtick=500        # Define o intervalo dos ticks
                ),
                showlegend=True,
                legend=dict(
                        orientation="h",          # Orientação horizontal
                        yanchor="top",         # Ancoragem na parte inferior
                        x=0,                      # Posiciona no centro
                        y=1.3,                   # Ajusta a posição vertical da legenda
                        font_size=10,
                        
                )
        )
        # Converter o gráfico para HTML 
        grafico_barra_html = fig_barra.to_html(full_html=False)
        
        ## Gráfico serie temporal com histograma
        categoriasM = ["Governança", "Gestão de riscos", "Gestão de ativos", "Gestão de cadeia <br> de suprimentos", "Requisitos regulamentares", "Gestão de identidade", "Concientização e treinamento", "Segurança de dados", "Processos e procedimentos<br>de proteção", "Manutenção", "Tecnologia de proteção", "Anomalias e eventos","Monitoramento de segurança", "Processos de detecção", "Planejamento de resposta"]
        valores_barraM = [1, 2, 3, 4, 5, 6, 7, 8, 8, 2, 5, 1, 2, 3, 3]
        valores_metaM = [1, 5, 3, 5, 5, 8, 7, 8, 8, 5, 2, 5, 2, 3, 4] # valores da linha devem ser maiores
        
        fig_serie_mat = go.Figure()

        # Adicionando o gráfico de barras
        fig_serie_mat.add_trace(go.Bar(
                x=categoriasM,
                y=valores_barraM,
                hovertemplate="%{y} em %{x}<extra></extra>",
                name='Aumento Maturidade',
                text=valores_barraM,
                textposition='inside',  # Posição do texto
                marker=dict(color='RoyalBlue')  # Define a cor das barras
        ))

        # Adicionando o gráfico de linha
        fig_serie_mat.add_trace(go.Scatter(
            x=categoriasM[:len(valores_barraM)],  # Ajustar o x para corresponder ao comprimento dos y
            y=valores_metaM,
            name='Custos',
            hovertemplate="%{customdata} de %{y}<extra></extra>",
            customdata=valores_barraM,  # Valores da barra associados aos pontos da linha
            text=[f"<b>{p}%</b>" for p in valores_metaM],
            textposition='top center',  # Posição do texto
            mode='lines+text', 
            line=dict(color='darkblue')
        ))

        # Configurações adicionais do layout
        fig_serie_mat.update_layout(
                plot_bgcolor='rgba(0, 0, 0, 0)',  # Fundo do gráfico transparente
                margin=dict(l=0, r=0, t=0, b=0),  # Margens
                height=270,
                width=None,
                font=dict(
                    family="Arial",
                    size=9,
                    color='#000000'
                ),
                yaxis=dict(
                    visible=False,      # Oculta o eixo Y
                    range=[0,15],       # Ajusta o intervalo do eixo Y
                    dtick=1.0           # Define o intervalo dos ticks
                ),
                showlegend=True,
                legend=dict(
                        yanchor="top",         # Ancoragem na parte superior
                        x=0,                   # Orientação horizontal
                        y=0.9,                 # Ajusta a posição vertical da legenda
                )
        )

        # Converter o gráfico para HTML 
        grafico_serie_maturidade_html = fig_serie_mat.to_html(full_html=False)
    
        context = {
            'assessments': assessments,
            # INÍCIO GRÁFICOS DO ASSESSMENT 
            'grafico_velocimetro_html': grafico_velocimetro_html,
            'cont_parcial_nao_conformes': cont_parcial_nao_conformes,
            'cont_prioridade_controle': cont_prioridade_controle,
            'grafico_barra_nota_secao_html': grafico_barra_nota_secao_html,
            'grafico_linha_html': grafico_linha_html,
            # FIM GRÁFICOS DO ASSESSMENT 
            # INÍCIO GRÁFICOS DO PLANO DE AÇÃO 
            'qtd_acoes_cad': qtd_acoes_cad,
            'percentual_acoes_cad': percentual_acoes_cad,
            'grafico_pizza_conclusao_html': grafico_pizza_conclusao_html,
            # FIM GRÁFICOS DO PLANO DE AÇÃO
            # INÍCIO GRÁFICOS DE CUSTO DO PLANO DE AÇÃO
            'soma_custo_estimado': soma_custo_estimado,
            # FIM GRÁFICOS DE CUSTO DO PLANO DE AÇÃO
            'grafico_pizza': grafico_pizza_html,
            'grafico_barra_r': grafico_barra_r_html,
            'grafico_barra': grafico_barra_html,
            'grafico_serie_maturidade':grafico_serie_maturidade_html,
        }

        return render(request, self.template_name, context)
