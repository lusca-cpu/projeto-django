from django.shortcuts import render
from django.views import View

import plotly.graph_objects as go

# Função para renderizar a página painelderesultados.html
class PaineldeResultados(View):
    template_name = 'paginas/painel_result.html'
    
    def get(self, request):
        
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
                visible=True,# Oculta o eixo Y
            ),
            yaxis_title='CIS Controls v8.1',  # Título do eixo Y
            yaxis=dict(
                visible=True,   # Oculta o eixo Y
                showticklabels=False,   # Oculta os valores dos ticks
                range=[0, 200],        # Ajuste os valores conforme necessário
                tick0=1,  # Valor inicial para os ticks
                dtick=10   # Espaçamento entre os ticks
            ),
            margin=dict(l=0, r=0, t=1, b=0),
            height=230,
            width=None,
            font=dict(
                family="Arial",
                size=9
            ),
        )
        # Converter o gráfico para HTML
        grafico_linha_html = fig_linha.to_html(full_html=False, config={'responsive': True})
        
        ## Grafico velocimetro
        # Dados para o gráfico
        valores = [15, 82]  #valor da aderencia e meta
        #categorias = ['Aderente', 'Meta']
        cormarcador = ["darkblue", "RoyalBlue", "LightBlue"]    
        
        fig_velocimetro = go.Figure(go.Indicator( 
            mode="gauge+number",
            value=valores[1], 
            number={'font': {'color': "darkblue", 'size': 16},
                    'suffix': '%'}, # Adiciona o símbolo de porcentagem}
            gauge={ 
                'axis': {
                            'range': [0, 100], 
                            'tickcolor': "blue", 
                            'ticks': "inside", 
                            'tickfont': dict(size=10),
                },
                'bar': {'color': cormarcador[0]},  # Cor da barra do indicador
                'bordercolor': "white",
                'steps': [  # Partes
                    {'range': [0, valores[0]], 'color': cormarcador[1]},  # aderente
                    {'range': [valores[0], 100], 'color': "LightBlue"}  # não aderente
                ],
                'threshold': {  # meta
                    'line': {'color': "red", 'width': 3},
                    'thickness': 0.80,
                    'value': valores[1]}
            },
        ))

        # Ajustar o layout para tamanho definido
        fig_velocimetro.update_layout(
                 margin=dict(l=10, r=20, t=20, b=0),  # Margens
                 width=None,
                 height=250, 
                 showlegend=True,
                 legend=dict(
                        orientation="h",          # Orientação horizontal
                        yanchor="bottom",         # Ancoragem na parte inferior
                        x=0.5,                    # Posiciona no centro
                        y=1.1,                   # Ajusta a posição vertical da legenda
                        font_size=10,
                    ),
                 paper_bgcolor='rgba(0, 0, 0, 0)',  # Fundo transparente
                 plot_bgcolor='rgba(0, 0, 0, 0)',    # Fundo do gráfico transparente
        )
     
        # Adicionar traces invisíveis para a legenda
        fig_velocimetro.add_trace(go.Scatter(
            x=[""], y=[""],
            mode='lines',
            line=dict(color='darkblue', width=3),
            name='Aderente',
            
        ))

        fig_velocimetro.add_trace(go.Scatter(
            x=[""], y=[""],
            mode='lines',
            line=dict(color='red', width=3),
            name='Meta',
        ))

        # Converter o gráfico para HTML
        grafico_velocimetro_html = fig_velocimetro.to_html(full_html=False)
        
        
        ## Gráfico Radar ref:https://plotly.com/python/radar-chart/
        
        categories = ['Recover','Govern','Detect', 'Identify', 'Protect', 'Respond']
        fig_radar = go.Figure()

        fig_radar.add_trace(go.Scatterpolar(r=[1, 5, 2, 2, 3],
            theta=categories,fill='toself', name='Aderente'
        ))
       
        fig_radar.add_trace(go.Scatterpolar(r=[4, 3, 2.5, 1, 2],
            theta=categories, fill='toself', name='Meta'
        ))

        fig_radar.update_layout(
                                polar=dict(
                                radialaxis=dict(
                                visible=True,
                                range=[0, 5]
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
                 height=250
                
        )
        # Converter o gráfico para HTML 
        grafico_radar_html = fig_radar.to_html(full_html=False)
        
        ## Gráfico serie temporal com histograma
        categorias = ["Concientização e <br> treinamento de Segurança", "Configuração segura de <br> ativos de software", "Gestão do controle de <br>Acessos", "Proteção de dados", "Gestão contínua de <br> vulnerabilidades", "Gestão de Contas", "Gestão de resposta <br>a incidentes", "Defesas contra malware", "Gestão de rergistros de <br> auditoria", "Iventário e Controle de <br>ativos de software", "Recuperação de dados", "Proteção de email e<br> navegador","Gestão da infraestrutura <br>de rede", "Inventário e controle <br>de ativos corporativos", "Gestão de provedor de<br> serviços"]
        valores_barra = [1, 2, 3, 4, 5, 6, 7, 8, 9, 2, 5, 1, 2, 3, 3]
        valores_meta = [1, 5, 3, 5, 5, 8, 7, 8, 8, 5, 2, 5, 2, 3, 4] # valores da linha devem ser maiores
        

        # Gráfico de barra e linha
        fig_serie = go.Figure()

        # Adicionando o gráfico de barras
        fig_serie.add_trace(go.Bar(
                x=categorias,
                y=valores_barra,
                hovertemplate="%{y} em %{x}<extra></extra>",
                name='Aderente',
                text=valores_barra,
                textposition='inside'  # Posição do texto
        ))

        # Adicionando o gráfico de linha
        fig_serie.add_trace(go.Scatter(
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
                ),
                showlegend=True,
                legend=dict(
                        yanchor="top",         # Ancoragem na parte inferior
                        x=-0.1,                # Orientação horizontal
                        y=1.0,                 # Ajusta a posição vertical da legenda
                )
        )

        # Converter o gráfico para HTML 
        grafico_serie_html = fig_serie.to_html(full_html=False)
       
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
        status = ['iniciado', 'andamento', 'atrasado', 'finalizado']
        valores = [1000, 20000, 50000, 100000]
        cormarcador = ["DarkBlue","RoyalBlue", "blue", "LightBlue"]

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
        fig_barra_r = go.Figure()

        # Adiciona as barras
        fig_barra_r.add_trace(go.Bar(x=x, y=[2, 5, 1, 9, 1], text=[2, 5, 1, 9, 1], textposition='inside'))
        fig_barra_r.add_trace(go.Bar(x=x, y=[1, 4, 9, 16, 1], text=[1, 4, 9, 12, 1], textposition='inside'))
        fig_barra_r.add_trace(go.Bar(x=x, y=[6, 8, 4.5, 8, 1], text=[6, 8, 4.5, 8, 1], textposition='inside'))
        fig_barra_r.add_trace(go.Bar(x=x, y=[2, 4, 8, 1, 1], text=[2, 4, 8, 1, 1], textposition='inside'))
        fig_barra_r.add_trace(go.Bar(x=x, y=[2, 4, 8, 1, 1], text=[2, 4, 8, 1, 1], textposition='inside'))    
       
        # Configuração do layout
        fig_barra_r.update_layout(
            barmode='stack',
            xaxis={'categoryorder': 'category ascending'},
            showlegend=False,  # Retira a legenda
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
        fig_barra = go.Figure()

        # Adicionando o gráfico de barras
        fig_barra.add_trace(go.Bar(
                x=categorias,
                y=valores_barra,
                hovertemplate="%{y} em %{x}<extra></extra>",
                name='Custo',
                text=valores_barra,
                textposition='outside'  # Posição do texto
        ))

        
        # Configurações adicionais do layout
        fig_barra.update_layout(
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
                ),
                legend=dict(
                        yanchor="top",         # Ancoragem na parte inferior
                        x=-0.1,                # Orientação horizontal
                        y=1.0,                 # Ajusta a posição vertical da legenda
                )
        )

        # Converter o gráfico para HTML 
        grafico_barra_html = fig_barra.to_html(full_html=False)
    
        context = {
            'grafico_velocimetro': grafico_velocimetro_html,
            'grafico_linha': grafico_linha_html,
            'grafico_pizza': grafico_pizza_html,
            'grafico_radar': grafico_radar_html,
            'grafico_serie': grafico_serie_html,
            'grafico_roda': grafico_roda_html,
            'grafico_barra_r': grafico_barra_r_html,
            'grafico_barra': grafico_barra_html,
        }

        return render(request, self.template_name, context)
