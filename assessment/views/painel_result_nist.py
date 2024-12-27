from django.db.models import Count, Sum, Q
from django.shortcuts import render
from django.views import View

from ..models import AssessmentModel, CadPlanodeAcaoModel, NistModel, PlanoAcaoModel

import plotly.graph_objects as go
import re

# Função para renderizar a página painel de resultados do Nist
class PaineldeResultadosNist(View):
    template_name = 'paginas/painel_result_nist.html'
    
    # INÍCIO GRÁFICOS DO ASSESSMENT ########################################################
    # Responsável pela criação do gráfico de velocímetro
    def view_grafico_velocimetro(self):
        # Filtrar apenas as instâncias relacionadas ao CisModel
        assessments_nist = AssessmentModel.objects.filter(framework__nome__icontains='nist', status='Concluído')

        # Calcular soma de meta e resultado
        soma_meta = assessments_nist.aggregate(Sum('meta'))['meta__sum'] or 0
        soma_resultado = assessments_nist.aggregate(Sum('resultado'))['resultado__sum'] or 0

        total_instancias = AssessmentModel.objects.filter(framework__nome__icontains='nist', status='Concluído').count()

        soma_meta = soma_meta/total_instancias
        soma_resultado = soma_resultado/total_instancias

        # Dados para o gráfico
        valores = [soma_resultado, soma_meta]
        cormarcador = ["darkblue", "RoyalBlue", "LightBlue"]    
        
        fig_velocimetro = go.Figure(go.Indicator( 
            mode="gauge+number",
            value=valores[1], 
            number={'font': {'color': "red", 'size': 16}}, 
            gauge={ 
                'axis': {
                            'range': [0, 5], 
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
                 margin=dict(l=15, r=15, t=5, b=5),  # Margens
                 width=255,
                 height=230, 
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
            name='Nota',
            
        ))

        fig_velocimetro.add_trace(go.Scatter(
            x=[""], y=[""],
            mode='lines',
            line=dict(color='red', width=3),
            name='Meta',
        ))

        # Converter o gráfico para HTML
        return fig_velocimetro.to_html(full_html=False)
    
    # Respoosanvel porr calcular a porcentagem e por retornar o gráfico de radar
    def view_grafico_radar(self):
        # Total de registros no NistModel
        total_nist = NistModel.objects.count()

        if total_nist == 0:  # Evitar divisão por zero
            return {
                'Recovery': 0,
                'Govern': 0,
                'Detect': 0,
                'Identify': 0,
                'Protect': 0,
                'Respond': 0
            }

        result = (
            NistModel.objects
            .values('funcao')
            .annotate(total_notaCss=Sum('notaCss'))
        )

        meta = (
            NistModel.objects
            .values('funcao')
            .annotate(total_meta=Sum('meta'))
        )

        # Contar total de instâncias para cada nível
        counts_total = (
            NistModel.objects
            .values('funcao')
            .annotate(count=Count('funcao'))
        )

        # Criar dicionário com totais por nível
        total_por_nivel = {item['funcao']: item['count'] for item in counts_total}

        # Criar dicionário para o resultado
        funcao_result = {item['funcao']: item['total_notaCss'] for item in result}

        # Criar dicionário para a meta
        funcao_meta = {item['funcao']: item['total_meta'] for item in meta}

        media_meta = {}
        for funcao, total in total_por_nivel.items():
            media = funcao_meta.get(funcao, 0)
            media_meta[funcao] = round(media/total, 2) if total > 0 else 0

        media_result = {}
        for funcao, total in total_por_nivel.items():
            media = funcao_result.get(funcao, 0)  
            media_result[funcao] = round(media/total, 2) if total > 0 else 0 

        categorias = ['Recovery','Govern','Detect', 'Identify', 'Protect', 'Respond']

        # Organizar os valores na ordem das categorias
        r_meta = [media_meta.get(cat, 0) for cat in categorias]
        r_result = [media_result.get(cat, 0) for cat in categorias]

        fig_radar = go.Figure()

        fig_radar.add_trace(go.Scatterpolar(r=r_result,
            theta=categorias,fill='toself', name='Nota'
        ))
       
        fig_radar.add_trace(go.Scatterpolar(r=r_meta,
            theta=categorias, fill='toself', name='Meta'
        ))

        fig_radar.update_layout(
                                polar=dict(
                                radialaxis=dict(
                                visible=True,
                                range=[0, 6]
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
    
    # Responsável por calcular a média e por retornar o gráfico de barra da função GOVERN
    def view_grafico_barra_linha_govern(self):
        # Total de registros no NistModel
        total_nist = NistModel.objects.count()

        if total_nist == 0:  # Evitar divisão por zero
            return {
                'Contexto Organizacional (GV.OC)': 0,
                'Estratégia de Gerenciamento de Riscos (GV.RM)': 0,
                'Papéis, Responsabilidades e Autoridades (GV.RR)': 0,
                'Política (GV.PO)': 0,
                'Supervisão (GV.OV)': 0,
                'Gestão de Riscos da Cadeia de Suprimentos de Cibersegurança (GV.SC)': 0
            }

        result = (
            NistModel.objects
            .filter(funcao='Govern')
            .values('categoria')
            .annotate(total_notaCss=Sum('notaCss'))
        )

        meta = (
            NistModel.objects
            .filter(funcao='Govern')
            .values('categoria')
            .annotate(total_meta=Sum('meta'))
        )

        # Contar total de instâncias para cada nível
        counts_total = (
            NistModel.objects
            .filter(funcao='Govern')
            .values('categoria')
            .annotate(count=Count('categoria'))
        )

        # Criar dicionário com totais por nível
        total_por_nivel = {item['categoria']: item['count'] for item in counts_total}

        # Criar dicionário para o resultado
        funcao_result = {item['categoria']: item['total_notaCss'] for item in result}

        # Criar dicionário para a meta
        funcao_meta = {item['categoria']: item['total_meta'] for item in meta}

        media_meta = {}
        for funcao, total in total_por_nivel.items():
            media = funcao_meta.get(funcao, 0)
            media_meta[funcao] = round(media/total, 2) if total > 0 else 0

        media_result = {}
        for funcao, total in total_por_nivel.items():
            media = funcao_result.get(funcao, 0)  
            media_result[funcao] = round(media/total, 2) if total > 0 else 0 

        categorias = ["Contexto Organizacional (GV.OC)", 
                        "Estratégia de Gerenciamento <br>de Riscos (GV.RM)", 
                        "Papéis, Responsabilidades e <br>Autoridades (GV.RR)", 
                        "Política (GV.PO)", 
                        "Supervisão (GV.OV)", 
                        "Gestão de Riscos da <br>Cadeia de Suprimentos de <br>Cibersegurança (GV.SC)"]
        categorias_limpa = [re.sub(r"<br>", "", cat).strip() for cat in categorias] # Versão limpa das categorias (removendo as tags <br>)

        y_meta = [media_meta.get(cat, 0) for cat in categorias_limpa]
        y_result = [media_result.get(cat, 0) for cat in categorias_limpa]

        # Ordenar as categorias com base nos valores das barras (y_result) em ordem decrescente
        sorted_data = sorted(zip(y_result, y_meta, categorias), key=lambda x: x[0], reverse=True)
        y_result_sorted, y_meta_sorted, categorias_sorted = zip(*sorted_data)
        
        fig_serie_govern = go.Figure()
         # Adicionando o gráfico de barras
        fig_serie_govern.add_trace(go.Bar(
                x=categorias_sorted,
                y=y_result_sorted,
                hovertemplate="%{y} em %{x}<extra></extra>",
                name='Nota',
                text=y_result_sorted,
                textposition='inside',  # Posição do texto
                marker=dict(color='#fffacd')  # Define a cor das barras
        ))

        # Adicionando o gráfico de linha
        fig_serie_govern.add_trace(go.Scatter(
            x=categorias_sorted[:len(y_result_sorted)],  # Ajustar o x para corresponder ao comprimento dos y
            y=y_meta_sorted,
            name='Meta',
            hovertemplate="%{customdata} de %{y}<extra></extra>",
            customdata=y_result_sorted,  # Valores da barra associados aos pontos da linha
            text=y_meta_sorted,
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
                    range=[0,10],  # Ajusta o intervalo do eixo Y
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
        return fig_serie_govern.to_html(full_html=False)

    # Responsável por calcular a média e por retornar o gráfico de barra da função IDENTIFY
    def view_grafico_barra_linha_identify(self):
        # Total de registros no NistModel
        total_nist = NistModel.objects.count()

        if total_nist == 0:  # Evitar divisão por zero
            return {
                'Gestão de Ativos (ID.AM)': 0,
                'Avaliação de Riscos (ID.RA)': 0,
                'Melhoria (ID.IM)': 0,
            }

        result = (
            NistModel.objects
            .filter(funcao='Identify')
            .values('categoria')
            .annotate(total_notaCss=Sum('notaCss'))
        )

        meta = (
            NistModel.objects
            .filter(funcao='Identify')
            .values('categoria')
            .annotate(total_meta=Sum('meta'))
        )

        # Contar total de instâncias para cada nível
        counts_total = (
            NistModel.objects
            .filter(funcao='Identify')
            .values('categoria')
            .annotate(count=Count('categoria'))
        )

        # Criar dicionário com totais por nível
        total_por_nivel = {item['categoria']: item['count'] for item in counts_total}

        # Criar dicionário para o resultado
        funcao_result = {item['categoria']: item['total_notaCss'] for item in result}

        # Criar dicionário para a meta
        funcao_meta = {item['categoria']: item['total_meta'] for item in meta}

        media_meta = {}
        for funcao, total in total_por_nivel.items():
            media = funcao_meta.get(funcao, 0)
            media_meta[funcao] = round(media/total, 2) if total > 0 else 0

        media_result = {}
        for funcao, total in total_por_nivel.items():
            media = funcao_result.get(funcao, 0)  
            media_result[funcao] = round(media/total, 2) if total > 0 else 0 

        categorias = ["Gestão de Ativos (ID.AM)",
                        "Avaliação de Riscos (ID.RA)", 
                        "Melhoria (ID.IM)"]
        categorias_limpa = [re.sub(r"<br>", "", cat).strip() for cat in categorias] # Versão limpa das categorias (removendo as tags <br>)

        y_meta = [media_meta.get(cat, 0) for cat in categorias_limpa]
        y_result = [media_result.get(cat, 0) for cat in categorias_limpa]

        # Ordenar as categorias com base nos valores das barras (y_result) em ordem decrescente
        sorted_data = sorted(zip(y_result, y_meta, categorias), key=lambda x: x[0], reverse=True)
        y_result_sorted, y_meta_sorted, categorias_sorted = zip(*sorted_data)
        
        fig_serie_identify = go.Figure()

        # Adicionando o gráfico de barras_identify
        fig_serie_identify.add_trace(go.Bar(
                x=categorias_sorted,
                y=y_result_sorted,
                hovertemplate="%{y} em %{x}<extra></extra>",
                name='Nota',
                text=y_result_sorted,
                textposition='inside',  # Posição do texto
                marker=dict(color='LightBlue')  # Define a cor das barras
        ))

        # Adicionando o gráfico de linha
        fig_serie_identify.add_trace(go.Scatter(
            x=categorias[:len(y_result_sorted)],  # Ajustar o x para corresponder ao comprimento dos y
            y=y_meta_sorted,
            name='Meta',
            hovertemplate="%{customdata} de %{y}<extra></extra>",
            customdata=y_result_sorted,  # Valores da barra associados aos pontos da linha
            text=y_meta_sorted,
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
                    range=[0,10],       # Ajusta o intervalo do eixo Y
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
        return fig_serie_identify.to_html(full_html=False)

    # Responsável por calcular a média e por retornar o gráfico de barra da função PROTECT
    def view_grafico_barra_linha_protect(self):
        # Total de registros no NistModel
        total_nist = NistModel.objects.count()

        if total_nist == 0:  # Evitar divisão por zero
            return {
                'Gestão de Identidade, Autenticação e Controle de Acesso (PR.AA)': 0,
                'Conscientização e Treinamento (PR.AT)': 0,
                'Segurança de Dados (PR.DS)': 0,
                'Segurança da Plataforma (PR.PS)': 0,
                'Resiliência da Infraestrutura <br>Tecnológica (PR.IR)': 0
            }

        result = (
            NistModel.objects
            .filter(funcao='Protect')
            .values('categoria')
            .annotate(total_notaCss=Sum('notaCss'))
        )

        meta = (
            NistModel.objects
            .filter(funcao='Protect')
            .values('categoria')
            .annotate(total_meta=Sum('meta'))
        )

        # Contar total de instâncias para cada nível
        counts_total = (
            NistModel.objects
            .filter(funcao='Protect')
            .values('categoria')
            .annotate(count=Count('categoria'))
        )

        # Criar dicionário com totais por nível
        total_por_nivel = {item['categoria']: item['count'] for item in counts_total}

        # Criar dicionário para o resultado
        funcao_result = {item['categoria']: item['total_notaCss'] for item in result}

        # Criar dicionário para a meta
        funcao_meta = {item['categoria']: item['total_meta'] for item in meta}

        media_meta = {}
        for funcao, total in total_por_nivel.items():
            media = funcao_meta.get(funcao, 0)
            media_meta[funcao] = round(media/total, 2) if total > 0 else 0

        media_result = {}
        for funcao, total in total_por_nivel.items():
            media = funcao_result.get(funcao, 0)  
            media_result[funcao] = round(media/total, 2) if total > 0 else 0 

        categorias = ["Gestão de Identidade, Autenticação <br>e Controle de Acesso (PR.AA)", 
                        "Conscientização e Treinamento (PR.AT)", 
                        "Segurança de Dados (PR.DS)", 
                        "Segurança da Plataforma (PR.PS)", 
                        "Resiliência da Infraestrutura <br>Tecnológica (PR.IR)"]
        categorias_limpa = [re.sub(r"<br>", "", cat).strip() for cat in categorias] # Versão limpa das categorias (removendo as tags <br>)

        y_meta = [media_meta.get(cat, 0) for cat in categorias_limpa]
        y_result = [media_result.get(cat, 0) for cat in categorias_limpa]

        # Ordenar as categorias com base nos valores das barras (y_result) em ordem decrescente
        sorted_data = sorted(zip(y_result, y_meta, categorias), key=lambda x: x[0], reverse=True)
        y_result_sorted, y_meta_sorted, categorias_sorted = zip(*sorted_data)
        
        fig_serie_protect = go.Figure()

        # Adicionando o gráfico de barras_protect
        fig_serie_protect.add_trace(go.Bar(
                x=categorias_sorted,
                y=y_result_sorted,
                hovertemplate="%{y} em %{x}<extra></extra>",
                name='Nota',
                text=y_result_sorted,
                textposition='inside',  # Posição do texto
                marker=dict(color='#d3d3d3')  # Define a cor das barras
        ))

        # Adicionando o gráfico de linha
        fig_serie_protect.add_trace(go.Scatter(
            x=categorias_sorted[:len(y_result_sorted)],  # Ajustar o x para corresponder ao comprimento dos y
            y=y_meta_sorted,
            name='Meta',
            hovertemplate="%{customdata} de %{y}<extra></extra>",
            customdata=y_result_sorted,  # Valores da barra associados aos pontos da linha
            text=y_meta_sorted,
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
                    range=[0,10],  # Ajusta o intervalo do eixo Y
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
        return fig_serie_protect.to_html(full_html=False)

    # Responsável por calcular a média e por retornar o gráfico de barra da função DETECT
    def view_grafico_barra_linha_detect(self):
        # Total de registros no NistModel
        total_nist = NistModel.objects.count()

        if total_nist == 0:  # Evitar divisão por zero
            return {
                'Monitoramento Contínuo (DE.CM)': 0,
                'Análise de Eventos Adversos (DE.AE)': 0
            }

        result = (
            NistModel.objects
            .filter(funcao='Detect')
            .values('categoria')
            .annotate(total_notaCss=Sum('notaCss'))
        )

        meta = (
            NistModel.objects
            .filter(funcao='Detect')
            .values('categoria')
            .annotate(total_meta=Sum('meta'))
        )

        # Contar total de instâncias para cada nível
        counts_total = (
            NistModel.objects
            .filter(funcao='Detect')
            .values('categoria')
            .annotate(count=Count('categoria'))
        )

        # Criar dicionário com totais por nível
        total_por_nivel = {item['categoria']: item['count'] for item in counts_total}

        # Criar dicionário para o resultado
        funcao_result = {item['categoria']: item['total_notaCss'] for item in result}

        # Criar dicionário para a meta
        funcao_meta = {item['categoria']: item['total_meta'] for item in meta}

        media_meta = {}
        for funcao, total in total_por_nivel.items():
            media = funcao_meta.get(funcao, 0)
            media_meta[funcao] = round(media/total, 2) if total > 0 else 0

        media_result = {}
        for funcao, total in total_por_nivel.items():
            media = funcao_result.get(funcao, 0)  
            media_result[funcao] = round(media/total, 2) if total > 0 else 0 

        categorias = ["Monitoramento Contínuo (DE.CM)", 
                        "Análise de Eventos Adversos (DE.AE)"]
        categorias_limpa = [re.sub(r"<br>", "", cat).strip() for cat in categorias] # Versão limpa das categorias (removendo as tags <br>)

        y_meta = [media_meta.get(cat, 0) for cat in categorias_limpa]
        y_result = [media_result.get(cat, 0) for cat in categorias_limpa]

        # Ordenar as categorias com base nos valores das barras (y_result) em ordem decrescente
        sorted_data = sorted(zip(y_result, y_meta, categorias), key=lambda x: x[0], reverse=True)
        y_result_sorted, y_meta_sorted, categorias_sorted = zip(*sorted_data)
        
        fig_serie_detect = go.Figure()

        # Adicionando o gráfico de barras
        fig_serie_detect.add_trace(go.Bar(
                x=categorias_sorted,
                y=y_result_sorted,
                hovertemplate="%{y} em %{x}<extra></extra>",
                name='Nota',
                text=y_result_sorted,
                textposition='inside',  # Posição do texto
                marker=dict(color='#F4a460')  # Define a cor das barras
        ))

        # Adicionando o gráfico de linha
        fig_serie_detect.add_trace(go.Scatter(
            x=categorias[:len(y_result_sorted)],  # Ajustar o x para corresponder ao comprimento dos y
            y=y_meta_sorted,
            name='Meta',
            hovertemplate="%{customdata} de %{y}<extra></extra>",
            customdata=y_result_sorted,  # Valores da barra associados aos pontos da linha
            text=y_meta_sorted,
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
                    range=[0,10],       # Ajusta o intervalo do eixo Y
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
        return fig_serie_detect.to_html(full_html=False)

    # Responsável por calcular a média e por retornar o gráfico de barra da função RESPOND
    def view_grafico_barra_linha_respond(self):
        # Total de registros no NistModel
        total_nist = NistModel.objects.count()

        if total_nist == 0:  # Evitar divisão por zero
            return {
                'Gestão de Incidentes (RS.MA)': 0,
                'Análise de Incidentes (RS.AN)': 0,
                'Relatório e Comunicação de Resposta a Incidentes (RS.CO)': 0,
                'Mitigação de Incidentes (RS.MI)': 0
            }

        result = (
            NistModel.objects
            .filter(funcao='Respond')
            .values('categoria')
            .annotate(total_notaCss=Sum('notaCss'))
        )

        meta = (
            NistModel.objects
            .filter(funcao='Respond')
            .values('categoria')
            .annotate(total_meta=Sum('meta'))
        )

        # Contar total de instâncias para cada nível
        counts_total = (
            NistModel.objects
            .filter(funcao='Respond')
            .values('categoria')
            .annotate(count=Count('categoria'))
        )

        # Criar dicionário com totais por nível
        total_por_nivel = {item['categoria']: item['count'] for item in counts_total}

        # Criar dicionário para o resultado
        funcao_result = {item['categoria']: item['total_notaCss'] for item in result}

        # Criar dicionário para a meta
        funcao_meta = {item['categoria']: item['total_meta'] for item in meta}

        media_meta = {}
        for funcao, total in total_por_nivel.items():
            media = funcao_meta.get(funcao, 0)
            media_meta[funcao] = round(media/total, 2) if total > 0 else 0

        media_result = {}
        for funcao, total in total_por_nivel.items():
            media = funcao_result.get(funcao, 0)  
            media_result[funcao] = round(media/total, 2) if total > 0 else 0

        categorias = ["Gestão de Incidentes (RS.MA)", 
                        "Análise de Incidentes (RS.AN)",    
                        "Relatório e Comunicação de <br>Resposta a Incidentes (RS.CO)",
                        "Mitigação de Incidentes (RS.MI)"]
        categorias_limpa = [re.sub(r"<br>", "", cat).strip() for cat in categorias] # Versão limpa das categorias (removendo as tags <br>)

        y_meta = [media_meta.get(cat, 0) for cat in categorias_limpa]
        y_result = [media_result.get(cat, 0) for cat in categorias_limpa]

        # Ordenar as categorias com base nos valores das barras (y_result) em ordem decrescente
        sorted_data = sorted(zip(y_result, y_meta, categorias), key=lambda x: x[0], reverse=True)
        y_result_sorted, y_meta_sorted, categorias_sorted = zip(*sorted_data)
        
        fig_serie_respond = go.Figure()

        # Adicionando o gráfico de barras
        fig_serie_respond.add_trace(go.Bar(
                x=categorias_sorted,
                y=y_result_sorted,
                hovertemplate="%{y} em %{x}<extra></extra>",
                name='Nota',
                text=y_result_sorted,
                textposition='inside',  # Posição do texto
                marker=dict(color='RoyalBlue')  # Define a cor das barras
        ))

        # Adicionando o gráfico de linha
        fig_serie_respond.add_trace(go.Scatter(
            x=categorias_sorted[:len(y_result_sorted)],  # Ajustar o x para corresponder ao comprimento dos y
            y=y_meta_sorted,
            name='Meta',
            hovertemplate="%{customdata} de %{y}<extra></extra>",
            customdata=y_result_sorted,  # Valores da barra associados aos pontos da linha
            text=y_meta_sorted,
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
                    range=[0,10],  # Ajusta o intervalo do eixo Y
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
        return fig_serie_respond.to_html(full_html=False)

    # Responsável por calcular a média e por retornar o gráfico de barra da função RECOVERY
    def view_grafico_barra_linha_recovery(self):
        # Total de registros no NistModel
        total_nist = NistModel.objects.count()

        if total_nist == 0:  # Evitar divisão por zero
            return {
                'Execução do Plano de Recuperação de Incidentes (RC.RP)': 0,
                'Comunicação de Recuperação <br>de Incidentes (RC.CO)': 0
            }

        result = (
            NistModel.objects
            .filter(funcao='Recovery')
            .values('categoria')
            .annotate(total_notaCss=Sum('notaCss'))
        )

        meta = (
            NistModel.objects
            .filter(funcao='Recovery')
            .values('categoria')
            .annotate(total_meta=Sum('meta'))
        )

        # Contar total de instâncias para cada nível
        counts_total = (
            NistModel.objects
            .filter(funcao='Recovery')
            .values('categoria')
            .annotate(count=Count('categoria'))
        )

        # Criar dicionário com totais por nível
        total_por_nivel = {item['categoria']: item['count'] for item in counts_total}

        # Criar dicionário para o resultado
        funcao_result = {item['categoria']: item['total_notaCss'] for item in result}

        # Criar dicionário para a meta
        funcao_meta = {item['categoria']: item['total_meta'] for item in meta}

        media_meta = {}
        for funcao, total in total_por_nivel.items():
            media = funcao_meta.get(funcao, 0)
            media_meta[funcao] = round(media/total, 2) if total > 0 else 0

        media_result = {}
        for funcao, total in total_por_nivel.items():
            media = funcao_result.get(funcao, 0)  
            media_result[funcao] = round(media/total, 2) if total > 0 else 0

        categorias = ["Execução do Plano de Recuperação <br>de Incidentes (RC.RP)", 
                        "Comunicação de Recuperação <br>de Incidentes (RC.CO)"]
        categorias_limpa = [re.sub(r"<br>", "", cat).strip() for cat in categorias] # Versão limpa das categorias (removendo as tags <br>)

        y_meta = [media_meta.get(cat, 0) for cat in categorias_limpa]
        y_result = [media_result.get(cat, 0) for cat in categorias_limpa]

        # Ordenar as categorias com base nos valores das barras (y_result) em ordem decrescente
        sorted_data = sorted(zip(y_result, y_meta, categorias), key=lambda x: x[0], reverse=True)
        y_result_sorted, y_meta_sorted, categorias_sorted = zip(*sorted_data)
        
        fig_serie_recovery = go.Figure()

        # Adicionando o gráfico de barras
        fig_serie_recovery.add_trace(go.Bar(
                x=categorias_sorted,
                y= y_result_sorted,
                hovertemplate="%{y} em %{x}<extra></extra>",
                name='Nota',
                text= y_result_sorted,
                textposition='inside',  # Posição do texto
                marker=dict(color='#90ee90')  # Define a cor das barras
        ))

        # Adicionando o gráfico de linha
        fig_serie_recovery.add_trace(go.Scatter(
            x=categorias_sorted[:len(y_result_sorted)],  # Ajustar o x para corresponder ao comprimento dos y
            y=y_meta_sorted,
            name='Meta',
            hovertemplate="%{customdata} de %{y}<extra></extra>",
            customdata= y_result_sorted,  # Valores da barra associados aos pontos da linha
            text=y_meta_sorted,
            textposition='top center',  # Posição do texto
            mode='lines+markers+text', 
            line=dict(color='darkblue')
        ))

        # Configurações adicionais do layout
        fig_serie_recovery.update_layout(
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
                    range=[0,10],       # Ajusta o intervalo do eixo Y
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
        return fig_serie_recovery.to_html(full_html=False)

    # Gráfico de linha
    def view_grafico_linha(self, request):
        limite = int(request.GET.get('limite', 12))
        # Filtrar apenas as instâncias relacionadas ao CisModel
        assessments_nist = AssessmentModel.objects.filter(framework__nome__icontains='nist', status='Concluído').order_by('-data_upload')[:limite]

        # Total de registros filtrados
        total_nist = assessments_nist.count()

        if total_nist > 0:
            meta = [float(value) for value in assessments_nist.values_list('meta', flat=True)]
            resultado = [float(value) for value in assessments_nist.values_list('resultado', flat=True)]
            meta.reverse()
            resultado.reverse()

            # Coletar as datas de upload no formato desejado
            data_meta = [data.strftime("%d/%m/%Y") for data in assessments_nist.values_list('data_upload', flat=True)]
            data_meta.reverse()
            data_resultado = data_meta.copy()  # Supondo que as datas sejam as mesmas
        else:
            meta = []
            resultado = []
            data_meta = []
            data_resultado = []

        # Criar o gráfico eixos x e y
        fig_linha = go.Figure()
        
        fig_linha.add_trace(go.Scatter(
                        x=data_meta, 
                        y=meta,
                        name='Meta',
                        hovertemplate="%{y}<extra></extra>",
                        text=[f"{m}" for m in meta],  # Adiciona o símbolo de % aos rótulos
                        textposition='top center',  # Posição do texto
                        mode='lines+markers+text',
                        line=dict(color='darkblue')
        ))
        fig_linha.add_trace(go.Scatter(
                        x=data_resultado, 
                        y=resultado,
                        name='Nota',
                        hovertemplate="%{y}<extra></extra>",
                        text=[f"{r}" for r in resultado],
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
                range=[0, 6],        # Ajuste os valores conforme necessário
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
        return fig_linha.to_html(full_html=False, config={'responsive': True})
    # FIM GRÁFICOS DO ASSESSMENT ########################################################

    # INÍCIO DAS DOS GRÁFICOS DO PLANO DE AÇÃO ################################################
    # Responsável por mostra os quantidades de ações cadastradas do plano de ação
    def view_qtd_acoes_cad(self):
        plano_acao = PlanoAcaoModel.objects.filter(nome__icontains='nist')

        # Soma os valores de 'acoes_cad' das instâncias filtradas
        total_acoes_cad = plano_acao.aggregate(total=Sum('acoes_cad'))['total'] or 0

        return total_acoes_cad
   
    # Responsável por mostra o percentual de ações cadastradas do plano de ação já concluidas
    def view_porcentagem_acoes_cad(self):
        plano_acao = PlanoAcaoModel.objects.filter(nome__icontains='nist')

        qtn_plano_acao = PlanoAcaoModel.objects.filter(nome__icontains='nist').count()

        por_plano_acao = plano_acao.aggregate(total=Sum('conclusao'))['total']

        percentual_concluido = (por_plano_acao / qtn_plano_acao)
        
        return percentual_concluido
    
    # Responsável por mostra o gráfico de pizza do status do plano de ação
    def view_grafico_pizza_conclusao(self):
        plano_acao = PlanoAcaoModel.objects.filter(nome__icontains='nist')

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
        grafico_pizza_conclusao_html = fig_roda.to_html(full_html=False, config={'responsive': True})
        return grafico_pizza_conclusao_html
    # FIM GRÁFICOS DO PLANO DE AÇÃO ################################################

    # INÍCIO DOS GRÁFICOS DE CUSTO DO PLANO DE AÇÃO ############################################
    # Resposánvel por somar todos os valores no cuso estimado do plano de ação
    def view_custo_estimado(self):
        plano_acao = PlanoAcaoModel.objects.filter(nome__icontains='Nist')

        # Soma os valores de 'custo_estimado' das instâncias filtradas
        total_custo_estimado = plano_acao.aggregate(total=Sum('custo_estimado'))['total'] or 0

        return total_custo_estimado
    
    # Responsável por mostra o gráfico de pizza do custo estimado por função do plano de ação
    def view_grafico_pizza_custo_estimado(self):
        funcoes = [
            'Govern', 
            'Identify', 
            'Protect', 
            'Detect', 
            'Respond', 
            'Recovery'
        ]

        subcontrole_somas = CadPlanodeAcaoModel.objects.values('subcontrole').annotate(total=Sum('quanto'))

        controle_subcontrole_map = {
            funcao: list(NistModel.objects.filter(funcao=funcao).values_list('subcategoria', flat=True))
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
        

    # Resposável por calcular a soma de custos de cada controle
    def calcular_soma_custos_de_cada_controle(self):
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
            CadPlanodeAcaoModel.objects.filter(planoacao__nome__icontains="nist")
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

    # Responsavel por somar todos os valores no cuso estimado do plano de ação por meta
    def view_grafico_serie_maturidade(self):
        categorias, categorias_limpa, controle_somas, valores_barra = self.calcular_soma_custos_de_cada_controle()

        # Total de registros no NistModel
        total_nist = NistModel.objects.count()

        if total_nist == 0:  # Evitar divisão por zero
            return {
                'Contexto Organizacional (GV.OC)': 0, 
                'Estratégia de Gerenciamento <br>de Riscos (GV.RM)': 0, 
                'Papéis, Responsabilidades e <br>Autoridades (GV.RR)': 0, 
                'Política (GV.PO)': 0, 
                'Supervisão (GV.OV)': 0, 
                'Gestão de Riscos da <br>Cadeia de Suprimentos de <br>Cibersegurança (GV.SC)': 0,
                'Gestão de Ativos (ID.AM)': 0,
                'Avaliação de Riscos (ID.RA)': 0, 
                'Melhoria (ID.IM)': 0,
                'Gestão de Identidade, Autenticação <br>e Controle de Acesso (PR.AA)': 0, 
                'Conscientização e Treinamento (PR.AT)': 0, 
                'Segurança de Dados (PR.DS)': 0, 
                'Segurança da Plataforma (PR.PS)': 0, 
                'Resiliência da Infraestrutura <br>Tecnológica (PR.IR)': 0,
                'Monitoramento Contínuo (DE.CM)': 0, 
                'Análise de Eventos Adversos (DE.AE)': 0,
                'Gestão de Incidentes (RS.MA)': 0, 
                'Análise de Incidentes (RS.AN)': 0,    
                'Relatório e Comunicação de <br>Resposta a Incidentes (RS.CO)': 0,
                'Mitigação de Incidentes (RS.MI)': 0,
                'Execução do Plano de Recuperação <br>de Incidentes (RC.RP)': 0, 
                'Comunicação de Recuperação <br>de Incidentes (RC.CO)': 0
            }

        # Obter soma das notas para cada categoria
        result = (
            NistModel.objects
            .values('categoria')
            .annotate(total_notaCss=Sum('notaCss'))
        )

        # Obter soma das metas para cada categoria
        meta = (
            NistModel.objects
            .values('categoria')
            .annotate(total_meta=Sum('meta'))
        )

        # Contar total de instâncias para cada categoria
        counts_total = (
            NistModel.objects
            .values('categoria')
            .annotate(count=Count('categoria'))
        )

        # Criar dicionários para armazenar os valores de soma e contagem
        total_por_nivel = {item['categoria']: item['count'] for item in counts_total}
        funcao_result = {item['categoria']: item['total_notaCss'] for item in result}
        funcao_meta = {item['categoria']: item['total_meta'] for item in meta}

        # Calcular a média de meta e notaCss por categoria e a diferença entre elas
        valores_meta = []
        for categoria in categorias_limpa:
            total = total_por_nivel.get(categoria, 1)  # Evitar divisão por zero, assume 1 se não houver total
            meta_total = funcao_meta.get(categoria, 0)
            notaCss_total = funcao_result.get(categoria, 0)
            
            # Calcular médias
            media_meta = meta_total / total
            media_notaCss = notaCss_total / total

            # Calcular a diferença média
            diferenca = media_meta - media_notaCss

            valores_meta.append((categoria, media_meta, diferenca))

    
        # Ordenar as categorias pela média de meta em ordem decrescente
        valores_meta_sorted = sorted(valores_meta, key=lambda x: x[1], reverse=True)

        # Extrair os valores ordenados
        categorias_sorted = [item[0] for item in valores_meta_sorted]
        valores_meta_sorted_only = [item[2] for item in valores_meta_sorted]  # Diferenças médias
        valores_barra_sorted = [controle_somas.get(cat, 0) for cat in categorias_sorted]

        # Criar um dicionário que mapeia as categorias limpas para as originais
        mapa_categorias = {re.sub(r"<br>", "", cat).strip(): cat for cat in categorias}

        # Restaurar os <br> nas categorias ordenadas
        categorias_sorted = [mapa_categorias[categoria] for categoria in categorias_sorted]
    
        # Criar o gráfico
        fig_serie_mat = go.Figure()

        # Adicionando o gráfico de barras
        fig_serie_mat.add_trace(go.Bar(
            x=categorias_sorted,
            y=valores_barra_sorted,
            hovertemplate="%{y} em %{x}<extra></extra>",
            name='Aumento Maturidade',
            text=valores_barra_sorted,
            textposition='inside',
            marker=dict(color='RoyalBlue')
        ))

        # Adicionando o gráfico de linha com um segundo eixo Y
        fig_serie_mat.add_trace(go.Scatter(
            x=categorias_sorted[:len(valores_barra_sorted)],
            y=valores_meta_sorted_only,
            name='Custos',
            hovertemplate="%{y}<extra></extra>",
            text=[f"<b>{p:.1f}</b>" for p in valores_meta_sorted_only],
            textposition='top center',
            mode='lines+text',
            line=dict(color='darkblue'),
            yaxis='y2'  # Referencia o segundo eixo Y
        ))

        # Configurações adicionais do layout
        fig_serie_mat.update_layout(
            plot_bgcolor='rgba(0, 0, 0, 0)',
            margin=dict(l=0, r=0, t=0, b=0),
            height=270,
            width=None,
            font=dict(
                family="Arial",
                size=9,
                color='#000000'
            ),
            yaxis=dict(
                range=[0, max(valores_meta_sorted_only) + 100],  # Ajusta o intervalo do eixo Y para as barras
                showgrid=False,
                dtick = 500
            ),
            yaxis2=dict(
                range=[0, 7],  # Ajusta o intervalo do eixo Y para a linha
                overlaying='y',  # Sobrepõe ao eixo Y primário
                side='right'     # Coloca o eixo Y2 do lado direito
            ),
            showlegend=True,
            legend=dict(
                yanchor="top",
                x=0,
                y=0.9
            )
        )

        # Converter o gráfico para HTML 
        return fig_serie_mat.to_html(full_html=False)

    # Responsanvel por somar todos os valores no cuso estimado do plano de ação porr categoria
    def view_grafico_barra_acao_categoria(self):
        categorias, categorias_limpa, controle_somas, valores_barra = self.calcular_soma_custos_de_cada_controle()

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
                range=[0, max(valores_barra_ordenados)*2],  # Ajusta o intervalo do eixo Y
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

    def get(self, request):

        assessments = AssessmentModel.objects.all()

        # INÍCIO GRÁFICOS DO ASSESSMENT ######################################################     
        # Gráfico de velocímetro
        grafico_velocimetro_html = self.view_grafico_velocimetro()

        # Gráfico Radar ref:https://plotly.com/python/radar-chart/
        grafico_radar_html = self.view_grafico_radar()

        # Gráfico de barra e elinha do GOVERN
        grafico_barra_linha_govern_html = self.view_grafico_barra_linha_govern()

        # Gráfico de barra e elinha do IDENTIFY
        grafico_barra_linha_identify_html = self.view_grafico_barra_linha_identify()

        # Gráfico de barra e elinha do PROTECT
        grafico_barra_linha_protect_html = self.view_grafico_barra_linha_protect()

        # Gráfico de barra e elinha do DETECT
        grafico_barra_linha_detect_html = self.view_grafico_barra_linha_detect()

        # Gráfico de barra e elinha do RESPOND
        grafico_barra_linha_respond_html = self.view_grafico_barra_linha_respond()

        # Gráfico de barra e elinha do RECOVERY
        grafico_barra_linha_recovery_html = self.view_grafico_barra_linha_recovery()

        # Gráfico de linha
        grafico_linha_html = self.view_grafico_linha(request)
        # FIM GRÁFICOS DO ASSESSMENT ######################################################
        
        # INÍCIO GRÁFICOS DO PLANO DE AÇÃO ##################################################
        # Quantidade de ações cadastradas
        qtd_acoes_cad = self.view_qtd_acoes_cad()

        # Porcentagem de ações cadastradas concluidas
        percentual_acoes_cad = self.view_porcentagem_acoes_cad()

        # Gráfico de pizza dos status do Plano de ação 
        grafico_pizza_conclusao_html = self.view_grafico_pizza_conclusao()
        # FIM GRÁFICOS DO PLANO DE AÇÃO ################################################

        # INÍCIO GRÁFICOS DE CUSTO DO PLANO DE AÇÃO #######################################
        soma_custo_estimado = self.view_custo_estimado()

        grafico_pizza_custo_estimado_html = self.view_grafico_pizza_custo_estimado()

        # Gráfico de barra de custo estimado das ações por maturidade
        grafico_serie_maturidade_html = self.view_grafico_serie_maturidade()

        # Gráfico de barra de custo estimado das ações por categoria
        grafico_barra_acao_categoria_html = self.view_grafico_barra_acao_categoria()
        # FIM GRÁFICOS DE CUSTO DO PLANO DE AÇÃO #######################################
         
        ## Grafico pizza
        # Dados
       
        
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
            'grafico_radar_html': grafico_radar_html,
            'grafico_barra_linha_govern_html': grafico_barra_linha_govern_html,
            'grafico_barra_linha_identify_html': grafico_barra_linha_identify_html,
            'grafico_barra_linha_protect_html': grafico_barra_linha_protect_html,
            'grafico_barra_linha_detect_html': grafico_barra_linha_detect_html,
            'grafico_barra_linha_respond_html': grafico_barra_linha_respond_html,
            'grafico_barra_linha_recovery_html': grafico_barra_linha_recovery_html,
            'grafico_linha_html': grafico_linha_html,
            # FIM GRÁFICOS DO ASSESSMENT
            # INÍCIO GRÁFICOS DO PLANO DE AÇÃO 
            'qtd_acoes_cad': qtd_acoes_cad,
            'percentual_acoes_cad': percentual_acoes_cad,
            'grafico_pizza_conclusao_html': grafico_pizza_conclusao_html,
            # FIM GRÁFICOS DO PLANO DE AÇÃO
            # INÍCIO GRÁFICOS DE CUSTO DO PLANO DE AÇÃO
            'soma_custo_estimado': soma_custo_estimado,
            'grafico_pizza_custo_estimado_html': grafico_pizza_custo_estimado_html,
            'grafico_serie_maturidade_html': grafico_serie_maturidade_html,
            'grafico_barra_acao_categoria_html': grafico_barra_acao_categoria_html,
            # FIM GRÁFICOS DE CUSTO DO PLANO DE AÇÃO
            'grafico_barra_r': grafico_barra_r_html,
        }

        return render(request, self.template_name, context)

