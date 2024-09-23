#Importando funçoes---------------------------------------------------------------------------------
import streamlit as st 
import pandas as pd
import plotly.express as px
import pendulum
from base_de_dado import funçao_cartao
from base_de_dado import funçao_investimento
from base_de_dado import função_custo_mensal
from base_de_dado import função_xp
from base_de_dado import função_sicredi
from base_de_dado import função_picpay

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
filtro_abas = st.sidebar.selectbox('Selecione as informaçoes que vc que analizar',abas_de_pesquisa)

# Função de formatação personalizada trocando "," por "." na casa dos milhares e vise versa-----------------
def formatar_numero(x):
    if isinstance(x, float) or isinstance(x, int):
        return f"{x:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
    return x

#Lendo o aquivo exel .xlsx/ selecionando a tabela que deseja fazer a analize  -----------------------
if filtro_abas == 'Custo Mensal':
    st.header('Custo Mensal')  
    st.session_state.custo_mensal = função_custo_mensal()
    df_aquivo_exel = st.session_state.custo_mensal
    col1,col2,col3 = st.columns(3) 
    col1.markdown('Total dos Gastos:  '+ str(f" **R${df_aquivo_exel['TOTAL'].sum():,.2f}**".replace(",", "X").replace(".", ",").replace("X", ".")))
    col2.markdown('Total dos Gastos Pessoais:  '+ str(f" **R${df_aquivo_exel['TOTAL PESSOAL'].sum():,.2f}**".replace(",", "X").replace(".", ",").replace("X", ".")))
    col3.markdown('Total dos Gastos com Terceiros: '+ str(f" **R${df_aquivo_exel['GASTOS COM TERCEIRO'].sum():,.2f}**".replace(",", "X").replace(".", ",").replace("X", ".")))
    tb_meses,tb_individual,tb_tabeal = st.tabs(['Demontrativo dos Meses','Analize Indidual','Tabela']) 
    with tb_meses:
        fig_1 = px.bar(df_aquivo_exel,x='MÊS',y='TOTAL',title='Demontrativo dos Gastos Mensais')
        fig_1.update_xaxes(dtick="M1",tickformat="%m/%Y")
        fig_1.update_layout(width=1000)
        fig_1.update_layout(title={'text': "Demontrativo dos Gastos Mensais",'y':0.85,'x':0.5,'xanchor': 'center','yanchor': 'top',  'font': {'family':"Times New Roman",'size': 25}})
        st.write(fig_1)
    with tb_individual:
        colunas =['TOTAL PESSOAL','GASTOS COM TERCEIRO','OUTROS GASTOS','GASTO NO CARTÃO']
        fig = px.line(df_aquivo_exel,x='MÊS',y=colunas,title='Gastos por Mes')
        fig.update_xaxes(dtick="M1",tickformat="%m/%Y")
        fig.update_layout(width=1000)
        fig.update_layout(title={'text':"Gastos do Cartão ao Longo dos Meses",'y':0.85,'x':0.5,'xanchor': 'center','yanchor': 'top',  'font': {'family':"Times New Roman",'size': 25}})
        st.write(fig)
    with tb_tabeal:
        st.write(df_aquivo_exel.applymap(formatar_numero)) # type: ignore
elif filtro_abas == 'Cartão':
    st.header('Cartão')
    tb_cart,tb_xp,tb_sicred,tb_picpay = st.tabs(['Resumo dos Cartões','XP','SICREDI','PICPAY']) 
    with tb_cart:
        st.session_state.funçao_cartao = funçao_cartao()
        df_aquivo_exel = st.session_state.funçao_cartao
        df_aquivo_exel['ANO'] = pd.to_datetime(df_aquivo_exel['ANO'], format='%Y')
        df_aquivo_exel = df_aquivo_exel[(df_aquivo_exel['ANO'] == data_agora.strftime('%Y'))]
        col1,col2,col3 = st.columns(3)
        col1.markdown('**Media** **de** **Gastos:** '+str(f"R${df_aquivo_exel['TOTAL'].sum()/len(df_aquivo_exel)-1:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")))
        col2.markdown('**Valor** **Total** **Gasto:** '+str(f"R${df_aquivo_exel['TOTAL'].sum():,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")))
        df_aquivo_exel = df_aquivo_exel.drop(columns=['TOTAL'])    
        colunas_numero = ['PERNAMBUCANAS','XP','PICPAY','SICREDI']
        col3.markdown('**Cartão** **com** **os** **Maiores** **Gastos:** '+ str(df_aquivo_exel[colunas_numero].sum().idxmax()))
        fig = px.line(df_aquivo_exel, x='DATA', y=colunas_numero, title='Gastos do Cartão ao Longo dos Meses')  
        fig.update_xaxes(dtick="M1",tickformat="%m/%Y")
        fig.update_layout(width=1000)
        fig.update_layout(title={'text': "Gastos do Cartão ao Longo dos Meses",'y':0.85,'x':0.5,'xanchor': 'center','yanchor': 'top',  'font': {'family':"Times New Roman",'size': 25}})
        st.write(fig)
    with tb_xp:
        col1,col2 = st.columns(2)
        st.session_state.cartao_xp = função_xp()
        df_aquivo_exel =  st.session_state.cartao_xp
        fig_xp1 = px.pie(df_aquivo_exel,values='VALOR', names='DEVEDOR', title='Divisão de Contas')
        fig_xp1.update_traces(textposition='inside', textinfo='percent+label')
        col1.write(fig_xp1) 
        fig_xp2 = px.bar(df_aquivo_exel,x='DATA PAGAMENTO',y='VALOR',title='Relação de Gastos ao Londo dos Meses')
        fig_xp2.update_layout(title={'text': "Relação de Gastos ao Londo dos Meses",'y':0.85,'x':0.5,'xanchor': 'center','yanchor': 'top',  'font': {'family':"Times New Roman",'size': 25}})
        col2.write(fig_xp2)
    with tb_sicred:
        col1,col2 = st.columns(2)
        st.session_state.cartao_sicred = função_sicredi()
        df_aquivo_exel =  st.session_state.cartao_sicred
        fig_sic1 = px.pie(df_aquivo_exel,values='VALOR', names='DEVEDOR', title='Divisão de Contas')
        fig_sic1.update_traces(textposition='inside', textinfo='percent+label')
        col1.write(fig_sic1)
        fig_sic2 = px.bar(df_aquivo_exel,x='DATA PAGAMENTO',y='VALOR',title='Relação de Gastos ao Londo dos Meses')
        fig_sic2.update_layout(title={'text': "Relação de Gastos ao Londo dos Meses",'y':0.85,'x':0.5,'xanchor': 'center','yanchor': 'top',  'font': {'family':"Times New Roman",'size': 25}})
        col2.write(fig_sic2)
    with tb_picpay:
        col1,col2 = st.columns(2)
        st.session_state.cartao_picpay = função_picpay()
        df_aquivo_exel =  st.session_state.cartao_picpay
        fig_pic1 = px.pie(df_aquivo_exel,values='VALOR', names='DEVEDOR', title='Divisão de Contas')
        fig_pic1.update_traces(textposition='inside', textinfo='percent+label')
        col1.write(fig_pic1)
        fig_pic2 = px.bar(df_aquivo_exel,x='DATA PAGAMENTO',y='VALOR',title='Relação de Gastos ao Londo dos Meses')
        fig_pic2.update_layout(title={'text': "Relação de Gastos ao Londo dos Meses",'y':0.85,'x':0.5,'xanchor': 'center','yanchor': 'top',  'font': {'family':"Times New Roman",'size': 25}})
        col2.write(fig_pic2)
elif filtro_abas == 'Investimentos':
    st.header('Investimentos')  
    st.session_state.função_investimento = funçao_investimento()
    df_aquivo_exel = st.session_state.função_investimento
    col1,col2,col3 = st.columns(3) 
    st.metric('VALOR APLICADO','R$'+ f"{sum(df_aquivo_exel['VALOR BRUTO']):,.2f}".replace(",", "X").replace(".", ",").replace("X", "."),float(f"{sum(df_aquivo_exel['LUCRO/PREJUÍZO']):,.2f}"))
    tb_1,tb_2 = st.tabs(['Proporção dos Ativos','Divisão dos Ativos']) 
    with tb_1:
        fig = px.bar(df_aquivo_exel,x='TICKER',y='LUCRO/PREJUÍZO',title='Relação Lucro e Prejuizo')
        fig.update_layout(width=1000)
        fig.update_layout(title={'text': "Relação Lucro e Prejuizo",'y':0.85,'x':0.5,'xanchor': 'center','yanchor': 'top',  'font': {'family':"Times New Roman",'size': 25}})
        st.write(fig)
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
        fig = px.pie(df_aquivo_exel,values='VALOR BRUTO', names='CORRETORA', title='Divisão por Impresa')
        fig.update_layout(width=500)
        fig.update_layout(title={'text': "Divisão por Impresa",'y':0.85,'x':0.4,'xanchor': 'center','yanchor': 'top',  'font': {'family':"Times New Roman",'size': 25}})
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
