#Importando funçoes---------------------------------------------------------------------------------
import streamlit as st 
import plotly.express as px
import pandas as pd
import pendulum
from base_de_dado import função_cotações
from base_de_dado import funçao_cartao
from base_de_dado import funçao_cotação_investimento
from base_de_dado import função_custo_mensal
from base_de_dado import função_xp
from base_de_dado import função_sicredi
from base_de_dado import função_picpay
from base_de_dado import funçao_salario
from base_de_dado import função_divizão_gasto_mensais
from base_de_dado import função_Banco_de_Dados21
#colocando o streamlit no modo layout grande---------------------------------------------------------
st.set_page_config(layout="wide")

#Passando o caminho do arquivo e o aquivo-----------------------------------------------------------
col1,col2,col3 = st.columns(3)
data_agora = pendulum.now()
data = data_agora.strftime('%d/%m/%Y')
hora = data_agora.strftime('%H:%M:%S')
col1.caption('Login: Luizh')
col2.caption('Data de Hoje: '+ data)
col3.caption('Hora da Ultima Atualização: '+ hora )

#criando na sidebar a seleçao da planilha que for analiazr-------------------------------------------
abas_de_pesquisa = ['Custo Mensal','Cartão','Investimentos','Proventos']
filtro_abas = st.sidebar.selectbox('Selecione as informações que vc que analizar',abas_de_pesquisa)

# Função de formatação personalizada trocando "," por "." na casa dos milhares e vise versa-----------------
def formatar_numero(x):
    if isinstance(x, float) or isinstance(x, int):
        return f"{x:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
    return x
st.markdown("""
            <style>
            .dataframe tbody td {
            font-size: 18px; /* Aumenta o tamanho da fonte das células */
            }
            .dataframe thead th {
            font-size: 20px; /* Aumenta o tamanho da fonte do cabeçalho */
            }
            </style>
            """, unsafe_allow_html=True)
#Lendo o aquivo exel .xlsx/ selecionando a tabela que deseja fazer a analize  -----------------------
if filtro_abas == 'Custo Mensal':
    col1s,col2s,col3s = st.columns(3)
    col2s.title('Custo Mensal')  
    st.session_state.custo_mensal = função_custo_mensal()
    df_aquivo_exel = st.session_state.custo_mensal
    col1,col2,col3,col4 = st.columns(4) 
    col1.markdown('Total dos Gastos:  '+ str(f" **R${df_aquivo_exel['TOTAL'].sum():,.2f}**".replace(",", "X").replace(".", ",").replace("X", ".")))
    #col2.markdown('Total dos Gastos Pessoais:  '+ str(f" **R${df_aquivo_exel['TOTAL PESSOAL'].sum():,.2f}**".replace(",", "X").replace(".", ",").replace("X", ".")))
    #col3.markdown('Total dos Gastos com Terceiros: '+ str(f" **R${df_aquivo_exel['GASTOS COM TERCEIRO'].sum():,.2f}**".replace(",", "X").replace(".", ",").replace("X", ".")))
    col4.markdown('Valor em Conta: '+str(f"**R${funçao_salario():,.2f}**".replace(",", "X").replace(".", ",").replace("X", ".")))
    tb_meses,tb_divmes,tb_individual = st.tabs(['Demontrativo dos Meses','Divisão dos Gastos','Analize Indidual por Mês']) 
    with tb_meses:
        col_custo_mensal = ['Todos']
        col_custo_mensal.extend(list(df_aquivo_exel['ANO'].unique()))
        but_ano = st.sidebar.selectbox('Filtro',col_custo_mensal)
        if but_ano != 'Todos':
            df_aquivo_exel = df_aquivo_exel[(df_aquivo_exel['ANO'] == but_ano)]
        else:
            st.session_state.custo_mensal = função_custo_mensal()
            df_aquivo_exel = st.session_state.custo_mensal
        fig_1 = px.line(df_aquivo_exel,x='DATA',y='TOTAL',title='Demontrativo dos Gastos Mensais')
        fig_1.update_xaxes(dtick="M1",tickformat="%m/%Y")
        fig_1.update_layout(width=1000)
        fig_1.update_layout(title={'text': "Demontrativo dos Gastos Mensais",'y':0.85,'x':0.5,'xanchor': 'center','yanchor': 'top',  'font': {'family':"Times New Roman",'size': 25}})
        st.write(fig_1)
        st.dataframe(df_aquivo_exel, use_container_width=True)
    with tb_divmes:
        colu1,colu2 = st.columns(2)
        df_descriçãos_gastos_ms = função_divizão_gasto_mensais()
        df_descriçãos_gastos = df_descriçãos_gastos_ms[df_descriçãos_gastos_ms['Valor']> 200]
        fig_5 = px.pie(df_descriçãos_gastos,values='Valor', names='Descrição', title='Maiores gastos')
        fig_5.update_traces(textposition='inside', textinfo='percent+label')
        st.write(fig_5)
        st.dataframe(df_descriçãos_gastos_ms, use_container_width=True)
    with tb_individual:
        colunas =['CARTÃO','TOTAL']
        fig = px.line(df_aquivo_exel,x='DATA',y=colunas,title='Gastos por Mes')
        fig.update_xaxes(dtick="M1",tickformat="%m/%Y")
        fig.update_layout(width=1000)
        fig.update_layout(title={'text':"Gastos do Cartão ao Longo dos Meses",'y':0.85,'x':0.5,'xanchor': 'center','yanchor': 'top',  'font': {'family':"Times New Roman",'size': 25}})
        st.write(fig)
        st.session_state.função_Banco_de_Dados21 = função_Banco_de_Dados21()
        df_banco21 = st.session_state.função_Banco_de_Dados21
        st.dataframe(df_banco21, use_container_width=True)
#VISÃO GERALA PARTE DO CARTÃO--------------------------------------------------------------------------------------------------------------------------------------------
elif filtro_abas == 'Cartão':
    col1s,col2s,col3s = st.columns(3)
    col2s.title('Cartão')
    tb_cart,tb_xp,tb_sicred,tb_picpay = st.tabs(['Resumo dos Cartões','XP','SICREDI','PICPAY'])
    st.session_state.funçao_cartao = funçao_cartao()
    df_aquivo_exel = st.session_state.funçao_cartao
    with tb_cart:
        df_cart = df_aquivo_exel[(df_aquivo_exel['ANO'] == data_agora.strftime('%Y'))]
        col1,col2,col3 = st.columns(3)
        col1.markdown('**Media** **de** **Gastos:** '+str(f"R${df_aquivo_exel['TOTAL'].sum()/len(df_aquivo_exel)-1:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")))
        col2.markdown('**Valor** **Total** **Gasto:** '+str(f"R${df_aquivo_exel['TOTAL'].sum():,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")))
        df_cart = df_cart.drop(columns=['TOTAL'])    
        colunas_numero = ['XP','PICPAY','SICREDI']
        col3.markdown('**Cartão** **com** **os** **Maiores** **Gastos:** '+ str(df_cart[colunas_numero].sum().idxmax()))
        fig = px.line(df_aquivo_exel, x='MÊS', y=colunas_numero, title='Gastos do Cartão ao Longo dos Meses')  
        fig.update_xaxes(dtick="M1",tickformat="%m/%Y")
        fig.update_layout(title={'text': "Gastos do Cartão ao Longo dos Meses",'y':0.85,'x':0.5,'xanchor': 'center','yanchor': 'top',  'font': {'family':"Times New Roman",'size': 25}})
        st.write(fig)
        st.dataframe(df_aquivo_exel, use_container_width=True)     
    with tb_xp:
        col1,col2 = st.columns(2)
        st.session_state.cartao_xp = função_xp()
        df_aquivo_xp =  st.session_state.cartao_xp
        df_xp = df_aquivo_xp[df_aquivo_xp['DESCRIÇÃO'] != 'PAGAMENTO ADIAN.']
        fig_xp1 = px.pie(df_xp,values='VALOR', names='DESCRIÇÃO', title='Divisão de Contas')
        fig_xp1.update_traces(textposition='inside', textinfo='percent+label')
        col1.write(fig_xp1) 
        fig_xp2 = px.bar(df_aquivo_exel,x='MÊS',y='XP',title='Relação de Gastos ao Londo dos Meses')
        fig_xp2.update_layout(title={'text': "Relação de Gastos ao Londo dos Meses",'y':0.85,'x':0.5,'xanchor': 'center','yanchor': 'top',  'font': {'family':"Times New Roman",'size': 25}})
        col2.write(fig_xp2)
        st.dataframe(df_aquivo_xp, use_container_width=True)  
    with tb_sicred:
        col1,col2 = st.columns(2)
        st.session_state.cartao_sicred = função_sicredi()
        df_cartão_sic =  st.session_state.cartao_sicred
        df_sic = df_cartão_sic[df_cartão_sic['DESCRIÇÃO'] != 'PAGAMENTO ADIAN.']
        fig_sic1 = px.pie(df_sic,values='VALOR', names='DESCRIÇÃO', title='Divisão de Contas')
        fig_sic1.update_traces(textposition='inside', textinfo='percent+label')
        col1.write(fig_sic1)
        fig_sic2 = px.bar(df_aquivo_exel,x='MÊS',y='SICREDI',title='Relação de Gastos ao Londo dos Meses')
        fig_sic2.update_layout(title={'text': "Relação de Gastos ao Londo dos Meses",'y':0.85,'x':0.5,'xanchor': 'center','yanchor': 'top',  'font': {'family':"Times New Roman",'size': 25}})
        col2.write(fig_sic2)
        st.dataframe(df_cartão_sic, use_container_width=True)  
    with tb_picpay:
        col1,col2 = st.columns(2)
        st.session_state.cartao_picpay = função_picpay()
        df_cartão_pic =  st.session_state.cartao_picpay
        df_pic = df_cartão_pic[df_cartão_pic['DESCRIÇÃO'] != 'PAGAMENTO ADIAN.']
        fig_pic1 = px.pie(df_pic,values='VALOR', names='DESCRIÇÃO', title='Divisão de Contas')
        fig_pic1.update_traces(textposition='inside', textinfo='percent+label')      
        col1.write(fig_pic1)
        fig_pic2 = px.bar(df_aquivo_exel,x='MÊS',y='PICPAY',title='Relação de Gastos ao Londo dos Meses')
        fig_pic2.update_layout(title={'text': "Relação de Gastos ao Londo dos Meses",'y':0.85,'x':0.5,'xanchor': 'center','yanchor': 'top',  'font': {'family':"Times New Roman",'size': 25}})
        col2.write(fig_pic2)
        st.dataframe(df_cartão_pic, use_container_width=True)  
elif filtro_abas == 'Investimentos':
    col1s,col2s,col3s = st.columns(3)
    col2s.title('Investimentos')  
    st.session_state.função_investimentos = funçao_cotação_investimento()
    df_aquivo_exel = st.session_state.função_investimentos
    st.session_state.função_cotação = função_cotações()
    df_cotação = st.session_state.função_cotação
    col1,col2,col3 = st.columns(3) 
    col3.metric('VALOR APLICADO', 
    'R$ '+f"{sum(df_aquivo_exel['VALOR BRUTO']):,.2f}".replace(",", "X").replace(".", ",").replace("X", "."), 
    f"{sum(df_aquivo_exel['LUCRO/PREJUÍZO']):,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
    )
    col1.metric('INDICE IBOVESPA', 
    f"{sum(df_cotação['IBOV']):,.2f}".replace(",", "X").replace(".", ",").replace("X", "."), 
    f"{(sum(df_cotação['IBOV'].astype(float)-df_cotação['ULTIMO FECHAMENTO IBOV'].astype(float))):,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
    )
    col1.metric('INDICE S&P500', 
    f"{sum(df_cotação['S&P500']):,.2f}".replace(",", "X").replace(".", ",").replace("X", "."), 
    f"{(sum(df_cotação['S&P500'].astype(float)-df_cotação['ULTIMO FECHAMENTO S&P500'].astype(float))):,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
    )
    col2.metric('COTAÇÃO BITCOIN', 
    '$ '+f"{sum(df_cotação['BTC']):,.2f}".replace(",", "X").replace(".", ",").replace("X", "."), 
    f"{(sum(df_cotação['BTC'].astype(float)-df_cotação['ULTIMO FECHAMENTO BTC'].astype(float))):,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
    )
    col2.metric('COTAÇÃO ETHERIUM', 
    '$ '+f"{sum(df_cotação['ETH']):,.2f}".replace(",", "X").replace(".", ",").replace("X", "."), 
    f"{(sum(df_cotação['ETH'].astype(float)-df_cotação['ULTIMO FECHAMENTO ETH'].astype(float))):,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
    )
    col3.metric('COTAÇÃO DOLAR',
    '$ '+f"{sum(df_cotação['DOLAR']):,.2f}".replace(",", "X").replace(".", ",").replace("X", "."),
    f"{(sum(df_cotação['DOLAR'].astype(float)-df_cotação['ULTIMO FECHAMENTO DOLAR'].astype(float))):,.2f}".replace(",", "X").replace(".", ",").replace("X", "."))
    
    tb_1,tb_2 = st.tabs(['Proporção dos Ativos','Divisão dos Ativos']) 
    with tb_1:
        fig = px.bar(df_aquivo_exel,x='TICKER',y='LUCRO/PREJUÍZO',title='Relação Lucro e Prejuizo')
        fig.update_layout(width=1000)
        fig.update_layout(title={'text': "Relação Lucro e Prejuizo",'y':0.85,'x':0.5,'xanchor': 'center','yanchor': 'top',  'font': {'family':"Times New Roman",'size': 25}})
        st.write(fig)
        st.dataframe(df_aquivo_exel, use_container_width=True)
    with tb_2:
        col1,col2 = st.columns(2)
        fig = px.pie(df_aquivo_exel,values='VALOR BRUTO', names='TIPO', title='Divisão de Ativos')
        fig.update_layout(width=500)
        fig.update_layout(title={'text': "Divisão de Ativos",'y':0.85,'x':0.4,'xanchor': 'center','yanchor': 'top',  'font': {'family':"Times New Roman",'size': 25}})
        col1.plotly_chart(fig)
        fig = px.pie(df_aquivo_exel,values='VALOR BRUTO', names='TICKER', title='Quantidade das Impresas')
        fig.update_layout(width=500)
        fig.update_layout(title={'text': "Quantidade das Imprezas",'y':0.85,'x':0.4,'xanchor': 'center','yanchor': 'top',  'font': {'family':"Times New Roman",'size': 25}})
        col2.plotly_chart(fig)
        fig = px.pie(df_aquivo_exel,values='VALOR BRUTO', names='CORRETORA', title='Divisão por Corretora')
        fig.update_layout(width=500)
        fig.update_layout(title={'text': "Divisão por Corretora",'y':0.85,'x':0.4,'xanchor': 'center','yanchor': 'top',  'font': {'family':"Times New Roman",'size': 25}})
        col1.plotly_chart(fig)
        df_aquivo_exel = df_aquivo_exel[(df_aquivo_exel['LUCRO/PREJUÍZO'] > 0 )]
        fig = px.pie(df_aquivo_exel,values='LUCRO/PREJUÍZO', names='TICKER', title='Lucro por Ticker')
        fig.update_layout(width=500)
        fig.update_layout(title={'text': "Lucro por Ticker",'y':0.85,'x':0.4,'xanchor': 'center','yanchor': 'top',  'font': {'family':"Times New Roman",'size': 25}})
        col2.plotly_chart(fig)
elif filtro_abas == 'Proventos':
    st.title('Esta aba esta INDISPONIVEL no momento')
else:
    st.write('estas imformaçoes esta imcorretas')

