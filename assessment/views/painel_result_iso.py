from django.shortcuts import render
from django.views import View

from ..models import AssessmentModel, CadPlanodeAcaoModel, PlanoAcaoModel

import plotly.graph_objects as go

# Função para renderizar a página painel de resultados ISO 'paginas/painel_result_iso.html
class PaineldeResultadosIso(View):
    template_name = 'paginas/painel_result_iso.html'
    
    def get(self, request):

        assessments = AssessmentModel.objects.all()
        
        ## Grafico de linha
        percentual1 = [10, 20, 20, 80, 90, 100]
        data1 = ["10/04/2024", "10/05/2024", "10/06/2024", "10/07/2024", "10/08/2024", "10/09/2024"]
        percentual2 = [5, 10, 10, 15, 20, 25]
        data2 = ["10/04/2024", "10/05/2024", "10/06/2024", "10/07/2024", "10/08/2024", "10/09/2024"]

        # Criar o gráfico eixos x e y
        fig_linha = go.Figure()
        
        fig_linha.add_trace(go.Scatter(
                        x=data1, 
                        y=percentual1,
                        name='Meta',
                        hovertemplate="%{y}<extra></extra>",
                        text=[f"{p}%" for p in percentual1],  # Adiciona o símbolo de % aos rótulos
                        textposition='top center',  # Posição do texto
                        mode='lines+markers+text',
                        line=dict(color='darkblue')
        ))
        fig_linha.add_trace(go.Scatter(
                        x=data2, 
                        y=percentual2,
                        name='Nota',
                        hovertemplate="%{y}<extra></extra>",
                        text=[f"{p}%" for p in percentual2],
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
            yaxis_title='NIST CSF 2.0',  # Título do eixo Y
            yaxis=dict(
                visible=True,          # Oculta o eixo Y
                showticklabels=False,  # Oculta os valores dos ticks
                range=[0, 200],        # Ajuste os valores conforme necessário
                tick0=1,   # Valor inicial para os ticks
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
        grafico_linha_html = fig_linha.to_html(full_html=False, config={'responsive': True})
        
        ## Grafico velocimetro
        # Dados para o gráfico
        valores = [2.4, 3.8]  #valor da nota media e meta
        cormarcador = ["darkblue", "RoyalBlue", "LightBlue"]    
        
        fig_velocimetro = go.Figure(go.Indicator( 
            mode="gauge+number",
            value=valores[1], 
            number={'font': {'color': "red", 'size': 16}}, 
            gauge={ 
                'axis': {
                            'range': [0, 10], 
                            'tickcolor': "blue", 
                            'ticks': "inside", 
                            'tickfont': dict(size=10),
                },
                'bar': {'color': 'rgba(0, 0, 0, 0)'},  # Cor da barra do indicador transparente
                'bordercolor': "white",
                'steps': [  # Partes
                    {'range': [0, valores[0]], 'color': cormarcador[0]},  # nota media
                    {'range': [valores[0], 10], 'color': cormarcador[2]}  
                ],
                'threshold': {  # meta
                    'line': {'color': "red", 'width': 3},
                    'thickness': 0.80,
                    'value': valores[1]}
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
        grafico_velocimetro_html = fig_velocimetro.to_html(full_html=False)
        
                      
        ## Gráfico serie_GOVERN temporal com histograma
        categorias = ["Contexto organizacional", "Estratégia de Risco", "Papeis e Responsabilidades", "Política", "Supervisão", "Gestão de Riscos <br> da cadeia de suprimentos", "Gestão de resposta <br>a incidentes"]
        valores_barra = [1, 2, 3, 4, 5, 6, 7]
        valores_meta = [1, 5, 3, 5, 5, 8, 10] # valores da linha devem ser maiores
        
        fig_serie_govern = go.Figure()

        # Adicionando o gráfico de barras
        fig_serie_govern.add_trace(go.Bar(
                x=categorias,
                y=valores_barra,
                hovertemplate="%{y} em %{x}<extra></extra>",
                name='Nota',
                text=valores_barra,
                textposition='inside',  # Posição do texto
                marker=dict(color='#fffacd')  # Define a cor das barras
        ))

        # Adicionando o gráfico de linha
        fig_serie_govern.add_trace(go.Scatter(
            x=categorias[:len(valores_barra)],  # Ajustar o x para corresponder ao comprimento dos y
            y=valores_meta,
            name='Meta',
            hovertemplate="%{customdata} de %{y}<extra></extra>",
            customdata=valores_barra,  # Valores da barra associados aos pontos da linha
            text=valores_meta,
            textposition='top center',  # Posição do texto
            mode='lines+markers+text', 
            line=dict(color='darkblue')
        ))

        # Configurações adicionais do layout
        fig_serie_govern.update_layout(
                plot_bgcolor='rgba(0, 0, 0, 0)',  # Fundo do gráfico transparente
                margin=dict(l=20, r=0, t=0, b=0),  # Margens
                height=240,
                width=None,
                font=dict(
                    family="Arial",
                    size=9,
                    color='#000000'
                ),
                yaxis=dict(
                    visible=False,      # Oculta o eixo Y
                    range=[0,18],  # Ajusta o intervalo do eixo Y
                    dtick=1.0                # Define o intervalo dos ticks
                ),
                showlegend=True,
                legend=dict(
                        yanchor="top",         # Ancoragem na parte inferior
                        x=0,                # Orientação horizontal
                        y=0.9,                 # Ajusta a posição vertical da legenda
                )
        )

        # Converter o gráfico para HTML 
        grafico_serie_govern_html = fig_serie_govern.to_html(full_html=False)
        
        ## Gráfico serie_IDENTIFY temporal com histograma
        categorias = ["Gestão de ativos", "Avaliação de Riscos", "Melhoria"]
        valores_barra = [1, 2, 8]
        valores_meta = [1, 5, 10] # valores da linha devem ser maiores
        
        fig_serie_identify = go.Figure()

        # Adicionando o gráfico de barras_identify
        fig_serie_identify.add_trace(go.Bar(
                x=categorias,
                y=valores_barra,
                hovertemplate="%{y} em %{x}<extra></extra>",
                name='Nota',
                text=valores_barra,
                textposition='inside',  # Posição do texto
                marker=dict(color='LightBlue')  # Define a cor das barras
        ))

        # Adicionando o gráfico de linha
        fig_serie_identify.add_trace(go.Scatter(
            x=categorias[:len(valores_barra)],  # Ajustar o x para corresponder ao comprimento dos y
            y=valores_meta,
            name='Meta',
            hovertemplate="%{customdata} de %{y}<extra></extra>",
            customdata=valores_barra,  # Valores da barra associados aos pontos da linha
            text=valores_meta,
            textposition='top center',  # Posição do texto
            mode='lines+markers+text', 
            line=dict(color='darkblue')
        ))

        # Configurações adicionais do layout
        fig_serie_identify.update_layout(
                plot_bgcolor='rgba(0, 0, 0, 0)',  # Fundo do gráfico transparente
                margin=dict(l=20, r=0, t=0, b=50),  # Margens
                height=240,
                width=None,
                font=dict(
                    family="Arial",
                    size=9,
                    color='#000000'
                ),
                yaxis=dict(
                    visible=False,      # Oculta o eixo Y
                    range=[0,18],       # Ajusta o intervalo do eixo Y
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
        grafico_serie_identify_html = fig_serie_identify.to_html(full_html=False)
        #----------
        
        ## Gráfico serie_PROTECT temporal com histograma
        categorias = ["Contexto organizacional", "Estratégia de Risco", "Papeis e Responsabilidades", "Política", "Supervisão", "Gestão de Riscos <br> da cadeia de suprimentos", "Gestão de resposta <br>a incidentes"]
        valores_barra = [1, 2, 3, 4, 5, 6, 7]
        valores_meta = [1, 5, 3, 5, 5, 8, 10] # valores da linha devem ser maiores
        
        fig_serie_protect = go.Figure()

        # Adicionando o gráfico de barras_protect
        fig_serie_protect.add_trace(go.Bar(
                x=categorias,
                y=valores_barra,
                hovertemplate="%{y} em %{x}<extra></extra>",
                name='Nota',
                text=valores_barra,
                textposition='inside',  # Posição do texto
                marker=dict(color='#fffacd')  # Define a cor das barras
        ))

        # Adicionando o gráfico de linha
        fig_serie_protect.add_trace(go.Scatter(
            x=categorias[:len(valores_barra)],  # Ajustar o x para corresponder ao comprimento dos y
            y=valores_meta,
            name='Meta',
            hovertemplate="%{customdata} de %{y}<extra></extra>",
            customdata=valores_barra,  # Valores da barra associados aos pontos da linha
            text=valores_meta,
            textposition='top center',  # Posição do texto
            mode='lines+markers+text', 
            line=dict(color='darkblue')
        ))

        # Configurações adicionais do layout
        fig_serie_protect.update_layout(
                plot_bgcolor='rgba(0, 0, 0, 0)',  # Fundo do gráfico transparente
                margin=dict(l=20, r=0, t=0, b=0),  # Margens
                height=240,
                width=None,
                font=dict(
                    family="Arial",
                    size=9,
                    color='#000000'
                ),
                yaxis=dict(
                    visible=False,      # Oculta o eixo Y
                    range=[0,18],  # Ajusta o intervalo do eixo Y
                    dtick=1.0                # Define o intervalo dos ticks
                ),
                showlegend=True,
                legend=dict(
                        yanchor="top",         # Ancoragem na parte inferior
                        x=0,                # Orientação horizontal
                        y=0.9,                 # Ajusta a posição vertical da legenda
                )
        )

        # Converter o gráfico para HTML 
        grafico_serie_protect_html = fig_serie_protect.to_html(full_html=False)
        
        ## Gráfico serie_DETECT temporal com histograma
        categorias = ["Gestão de ativos", "Avaliação de Riscos", "Melhoria"]
        valores_barra = [1, 2, 8]
        valores_meta = [1, 5, 10] # valores da linha devem ser maiores
        
        fig_serie_detect = go.Figure()

        # Adicionando o gráfico de barras
        fig_serie_detect.add_trace(go.Bar(
                x=categorias,
                y=valores_barra,
                hovertemplate="%{y} em %{x}<extra></extra>",
                name='Nota',
                text=valores_barra,
                textposition='inside',  # Posição do texto
                marker=dict(color='#F4a460')  # Define a cor das barras
        ))

        # Adicionando o gráfico de linha
        fig_serie_detect.add_trace(go.Scatter(
            x=categorias[:len(valores_barra)],  # Ajustar o x para corresponder ao comprimento dos y
            y=valores_meta,
            name='Meta',
            hovertemplate="%{customdata} de %{y}<extra></extra>",
            customdata=valores_barra,  # Valores da barra associados aos pontos da linha
            text=valores_meta,
            textposition='top center',  # Posição do texto
            mode='lines+markers+text', 
            line=dict(color='darkblue')
        ))

        # Configurações adicionais do layout
        fig_serie_detect.update_layout(
                plot_bgcolor='rgba(0, 0, 0, 0)',  # Fundo do gráfico transparente
                margin=dict(l=20, r=0, t=0, b=50),  # Margens
                height=240,
                width=None,
                font=dict(
                    family="Arial",
                    size=9,
                    color='#000000'
                ),
                yaxis=dict(
                    visible=False,      # Oculta o eixo Y
                    range=[0,18],       # Ajusta o intervalo do eixo Y
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
        grafico_serie_detect_html = fig_serie_detect.to_html(full_html=False)
        
        #-----------------
     ## Gráfico serie_RESPOND temporal com histograma
        categorias = ["Gestão de incidentes", "Análise de incidentes", "Reslatório e Comunicação <br>de incidentes", "Mitigação de Incidentes"]
        valores_barra = [1, 2, 3, 4, 5, 6, 7]
        valores_meta = [1, 5, 3, 5, 5, 8, 10] # valores da linha devem ser maiores
        
        fig_serie_respond = go.Figure()

        # Adicionando o gráfico de barras
        fig_serie_respond.add_trace(go.Bar(
                x=categorias,
                y=valores_barra,
                hovertemplate="%{y} em %{x}<extra></extra>",
                name='Nota',
                text=valores_barra,
                textposition='inside',  # Posição do texto
                marker=dict(color='RoyalBlue')  # Define a cor das barras
        ))

        # Adicionando o gráfico de linha
        fig_serie_respond.add_trace(go.Scatter(
            x=categorias[:len(valores_barra)],  # Ajustar o x para corresponder ao comprimento dos y
            y=valores_meta,
            name='Meta',
            hovertemplate="%{customdata} de %{y}<extra></extra>",
            customdata=valores_barra,  # Valores da barra associados aos pontos da linha
            text=valores_meta,
            textposition='top center',  # Posição do texto
            mode='lines+markers+text', 
            line=dict(color='darkblue')
        ))

        # Configurações adicionais do layout
        fig_serie_respond.update_layout(
                plot_bgcolor='rgba(0, 0, 0, 0)',  # Fundo do gráfico transparente
                margin=dict(l=20, r=0, t=0, b=0),  # Margens
                height=240,
                width=None,
                font=dict(
                    family="Arial",
                    size=9,
                    color='#000000'
                ),
                yaxis=dict(
                    visible=False,      # Oculta o eixo Y
                    range=[0,18],  # Ajusta o intervalo do eixo Y
                    dtick=1.0                # Define o intervalo dos ticks
                ),
                showlegend=True,
                legend=dict(
                        yanchor="top",         # Ancoragem na parte inferior
                        x=0,                # Orientação horizontal
                        y=0.9,                 # Ajusta a posição vertical da legenda
                )
        )

        # Converter o gráfico para HTML 
        grafico_serie_respond_html = fig_serie_respond.to_html(full_html=False)
        
        ## Gráfico serie_RECOVER temporal com histograma
        categorias = ["Execução do plano <br> de recuperação de incidentes", "Comunicação de recuperação de incidentes"]
        valores_barra = [1, 2]
        valores_meta = [1, 10] # valores da linha devem ser maiores
        
        fig_serie_recover = go.Figure()

        # Adicionando o gráfico de barras
        fig_serie_recover.add_trace(go.Bar(
                x=categorias,
                y=valores_barra,
                hovertemplate="%{y} em %{x}<extra></extra>",
                name='Nota',
                text=valores_barra,
                textposition='inside',  # Posição do texto
                marker=dict(color='#90ee90')  # Define a cor das barras
        ))

        # Adicionando o gráfico de linha
        fig_serie_recover.add_trace(go.Scatter(
            x=categorias[:len(valores_barra)],  # Ajustar o x para corresponder ao comprimento dos y
            y=valores_meta,
            name='Meta',
            hovertemplate="%{customdata} de %{y}<extra></extra>",
            customdata=valores_barra,  # Valores da barra associados aos pontos da linha
            text=valores_meta,
            textposition='top center',  # Posição do texto
            mode='lines+markers+text', 
            line=dict(color='darkblue')
        ))

        # Configurações adicionais do layout
        fig_serie_recover.update_layout(
                plot_bgcolor='rgba(0, 0, 0, 0)',  # Fundo do gráfico transparente
                margin=dict(l=20, r=0, t=0, b=50),  # Margens
                height=240,
                width=None,
                font=dict(
                    family="Arial",
                    size=9,
                    color='#000000'
                ),
                yaxis=dict(
                    visible=False,      # Oculta o eixo Y
                    range=[0,18],       # Ajusta o intervalo do eixo Y
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
        grafico_serie_recover_html = fig_serie_recover.to_html(full_html=False)
       
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
        
        ## Grafico roda
        status = ['não iniciado', 'andamento', 'atrasado', 'finalizado']
        valores = [1000, 20000, 50000, 100000]
        cormarcador = ["#F4a460","#fffacd", "#d3d3d3", "#90ee90"]

        fig_roda = go.Figure(data=go.Pie(labels=status,
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
        grafico_roda_html = fig_roda.to_html(full_html=False, config={'responsive': True})
        
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
        categoriasb = ["Contexto organizacional", "Estratégia de <br> gerenciamento de riscos", "Papéis,responsabilidades,<br>autoridades", "Política", "Supervisão", "Gestão de riscos <br> cadeia suprimentos", "Gestão de <br>ativos", "Avaliação de Riscos", "Melhoria", "Gestão de <br>identidade", "Concientização", "Segurança de <br> dados","Segurança de <br> plataforma", "Resiliência da <br> infraestrutura", "Monitoramento", "Análise de eventos", "Gestão de <br>incidentes", "Análise de incidentes", "Relatório de incidentes", "Mitigação", "Plano de incidentes", "Comunicação de <br> Recuperação"]
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
            'grafico_velocimetro': grafico_velocimetro_html,
            'grafico_linha': grafico_linha_html,
            'grafico_pizza': grafico_pizza_html,
            'grafico_serie_govern': grafico_serie_govern_html,
            'grafico_serie_identify': grafico_serie_identify_html,
            'grafico_serie_protect': grafico_serie_protect_html,
            'grafico_serie_detect': grafico_serie_detect_html,
            'grafico_serie_respond': grafico_serie_respond_html,
            'grafico_serie_recover': grafico_serie_recover_html,
            'grafico_roda': grafico_roda_html,
            'grafico_barra_r': grafico_barra_r_html,
            'grafico_barra': grafico_barra_html,
            'grafico_serie_maturidade':grafico_serie_maturidade_html,
        }

        return render(request, self.template_name, context)
