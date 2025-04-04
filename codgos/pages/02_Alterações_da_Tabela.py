#Importando funçoes---------------------------------------------------------------------------------
from pathlib import Path
import pandas as pd
import streamlit as st 
st.set_page_config(layout="wide")

#Passando o caminho do arquivo e o aquivo-----------------------------------------------------------
pasta_arquivo = Path(__file__).parents[2] / 'Arquivos'
arquivos_tabela = pasta_arquivo / 'CUSTOS E INVESTIMENTOS02.xlsx'
arquivos_tabela_cartão = pasta_arquivo / 'ARQUIVO CARTÃO.xlsx'
arquivos_tabela_backup = pasta_arquivo / 'backup_custo_investimentos.xlsx'
arquivos_tabela_cartão_beckup = pasta_arquivo / 'backup_cartão.xlsx'

#criando na sidebar a seleçao da planilha que for analiazr-------------------------------------------
cols1,cols2,cols3 = st.columns(3)
mensagem = ('***Você Esta na Pagina de Alteração e Adição do banco de dados.***')
coluna = st.columns(1)
abas_de_pesquisa = ['Outros Gastos','Cartão','Investimentos','Suplemento']
filtro_abas = st.sidebar.selectbox('Selecione a Base de Dados em que vc quer Modificar',abas_de_pesquisa)
coluna1,coluna2 = st.columns(2)
col1,col2,col3,col4 = st.columns(4)

#criando os aquivos -------------------------------------------------------------------------------------------
df_outros_gastos = pd.read_excel(arquivos_tabela,sheet_name='OUTROS GASTOS')
df_cartão_xp = pd.read_excel(arquivos_tabela_cartão,sheet_name='XP')
df_cartão_sicredi = pd.read_excel(arquivos_tabela_cartão,sheet_name='SICREDI')
df_cartão_picpay = pd.read_excel(arquivos_tabela_cartão,sheet_name='PICPAY')
df_investimentos = pd.read_excel(arquivos_tabela,sheet_name='INVESTIMENTO')
df_suplemento = pd.read_excel(arquivos_tabela,sheet_name='SUPLEMENTO')

#fazendo o bekup do aquivo do cartão------------------------------------------------------------------------------
with pd.ExcelWriter(arquivos_tabela_cartão_beckup, engine='openpyxl') as writer:
    df_cartão_xp .to_excel(writer, sheet_name='XP', index=False)
    df_cartão_sicredi.to_excel(writer, sheet_name='SICREDI', index=False)
    df_cartão_picpay.to_excel(writer, sheet_name='PICPAY', index=False)


#fazendo o bekup do aquivo custo e investimento--------------------------------------------------------------------
with pd.ExcelWriter(arquivos_tabela_backup, engine='openpyxl') as writer:  
    df_outros_gastos.to_excel(writer, sheet_name='OUTROS GASTOS', index=False) 
    df_investimentos.to_excel(writer, sheet_name='INVESTIMENTO', index=False)
    df_suplemento.to_excel(writer, sheet_name='SUPLEMENTO', index=False)

#criando as variaveis para não causar erro de não existensiaou vazia mais a frente--------------------------------
df_editado_outrosgastos = df_outros_gastos
df_editado_xp = df_cartão_xp
df_editado_sicredi = df_cartão_sicredi
df_editado_picpay = df_cartão_picpay
df_editado_investimentos = df_investimentos
df_editado_suplemento = df_suplemento

#selecionando as planilhas que vão ser modificadas ou não-------------------------------------------------------------
if filtro_abas == 'Outros Gastos':
    cols2.title('Outros gastos')
    coluna1.markdown(mensagem)
    #criando o dataframe que é interativo com o usuario e editavel para modificar-----------------------------------------
    df_editado_outrosgastos = st.data_editor(df_outros_gastos, num_rows="dynamic")
elif filtro_abas == 'Cartão':
    cols2.title('Cartão')
    coluna1.markdown(mensagem)
    tb_xp,tb_sicred,tb_picpay = st.tabs(['XP','SICREDI','PICPAY']) 
    with tb_xp:
        df_editado_xp = st.data_editor(df_cartão_xp, num_rows="dynamic")
    with tb_sicred:
        df_editado_sicredi = st.data_editor(df_cartão_sicredi, num_rows="dynamic")
    with tb_picpay:
        df_editado_picpay = st.data_editor(df_cartão_picpay, num_rows="dynamic")
elif filtro_abas == 'Investimentos':
    cols2.title('Investimento')  
    coluna1.markdown(mensagem)
    df_editado_investimentos = st.data_editor(df_investimentos, num_rows="dynamic")
elif filtro_abas == 'Suplemento':
    cols2.title('Suplemento')  
    coluna1.markdown(mensagem)
    df_editado_suplemento = st.data_editor(df_suplemento, num_rows="dynamic")
col1,col2 = st.sidebar.columns(2)
but_salvar = col1.button('Salvar Alteração')
but_limpar = col2.button('Limpar')
#salvando o arquivo modificado ------------------------------------------------------------------------------------------
if but_salvar:
    with pd.ExcelWriter(arquivos_tabela_cartão, engine='openpyxl') as writer:
        df_editado_xp .to_excel(writer, sheet_name='XP', index=False)
        df_editado_sicredi.to_excel(writer, sheet_name='SICREDI', index=False)
        df_editado_picpay.to_excel(writer, sheet_name='PICPAY', index=False)
    with pd.ExcelWriter(arquivos_tabela, engine='openpyxl') as writer:  
        df_editado_outrosgastos.to_excel(writer, sheet_name='OUTROS GASTOS', index=False) 
        df_editado_investimentos.to_excel(writer, sheet_name='INVESTIMENTO', index=False)
        df_editado_suplemento.to_excel(writer, sheet_name='SUPLEMENTO', index=False)
    st.success('Arquivo Salvo')
