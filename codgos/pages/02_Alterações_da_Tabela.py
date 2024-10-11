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
mensagem = ('***Você Esta na Pagina de Alteração e Adição do banco de dados.***')
coluna = st.columns(1)
abas_de_pesquisa = ['Outros Gastos','Cartão','Investimentos','Suplemento']
filtro_abas = st.sidebar.selectbox('Selecione a Base de Dados em que vc quer Modificar',abas_de_pesquisa)
coluna1,coluna2 = st.columns(2)
col1,col2,col3,col4 = st.columns(4)

#criando os aquivos -------------------------------------------------------------------------------------------
df_outros_gastos = pd.read_excel(arquivos_tabela,sheet_name='OUTROS GASTOS')
df_cartão = pd.read_excel(arquivos_tabela_cartão,sheet_name='CARTÃO')
df_cartão_pernambucanas = pd.read_excel(arquivos_tabela_cartão,sheet_name='PERNAMBUCANAS')
df_cartão_xp = pd.read_excel(arquivos_tabela_cartão,sheet_name='XP')
df_cartão_sicredi = pd.read_excel(arquivos_tabela_cartão,sheet_name='SICREDI')
df_cartão_picpay = pd.read_excel(arquivos_tabela_cartão,sheet_name='PICPAY')
df_cartão_magalu = pd.read_excel(arquivos_tabela_cartão,sheet_name='MAGAZINE LUIZA')
df_investimentos = pd.read_excel(arquivos_tabela,sheet_name='INVESTIMENTO')
df_suplemento = pd.read_excel(arquivos_tabela,sheet_name='SUPLEMENTO')

#fazendo o bekup do aquivo do cartão------------------------------------------------------------------------------
with pd.ExcelWriter(arquivos_tabela_cartão_beckup, engine='openpyxl') as writer:
    df_cartão.to_excel(writer, sheet_name='CARTÃO', index=False)
    df_cartão_pernambucanas.to_excel(writer, sheet_name='PERNAMBUCANAS', index=False)
    df_cartão_xp .to_excel(writer, sheet_name='XP', index=False)
    df_cartão_sicredi.to_excel(writer, sheet_name='SICREDI', index=False)
    df_cartão_picpay.to_excel(writer, sheet_name='PICPAY', index=False)
    df_cartão_magalu.to_excel(writer, sheet_name='MAGAZINE LUIZA', index=False)

#fazendo o bekup do aquivo custo e investimento--------------------------------------------------------------------
with pd.ExcelWriter(arquivos_tabela_backup, engine='openpyxl') as writer:  
    df_outros_gastos.to_excel(writer, sheet_name='OUTROS GASTOS', index=False) 
    df_investimentos.to_excel(writer, sheet_name='INVESTIMENTO', index=False)
    df_suplemento.to_excel(writer, sheet_name='SUPLEMENTO', index=False)

#criando as variaveis para não causar erro de não existensiaou vazia mais a frente--------------------------------
df_editado_outrosgastos = df_outros_gastos
df_editado_cartão = df_cartão
df_editado_pernambucanas =df_cartão_pernambucanas
df_editado_xp = df_cartão_xp
df_editado_sicredi = df_cartão_sicredi
df_editado_picpay = df_cartão_picpay
df_editado_magalu = df_cartão_magalu
df_editado_investimentos = df_investimentos
df_editado_suplemento = df_suplemento

#selecionando as planilhas que vão ser modificadas ou não-------------------------------------------------------------
if filtro_abas == 'Outros Gastos':
    coluna1.header('Outros gastos')
    coluna1.markdown(mensagem)
    #criando o dataframe que é interativo com o usuario e editavel para modificar-----------------------------------------
    df_editado_outrosgastos = st.data_editor(df_outros_gastos, num_rows="dynamic")
elif filtro_abas == 'Cartão':
    coluna1.header('Cartão')
    coluna1.markdown(mensagem)
    tb_cart,tb_pernambucanas,tb_xp,tb_sicred,tb_picpay,tb_magalu = st.tabs(['Resumo dos Cartões','PERNAMBUCANAS','XP','SICREDI','PICPAY','MAGAZINE LUIZA']) 
    with tb_cart:
        df_editado_cartão = st.data_editor(df_cartão, num_rows="dynamic")
    with tb_pernambucanas:
        df_editado_pernambucanas = st.data_editor(df_cartão_pernambucanas, num_rows="dynamic")
    with tb_xp:
        df_editado_xp = st.data_editor(df_cartão_xp, num_rows="dynamic")
    with tb_sicred:
        df_editado_sicredi = st.data_editor(df_cartão_sicredi, num_rows="dynamic")
    with tb_picpay:
        df_editado_picpay = st.data_editor(df_cartão_picpay, num_rows="dynamic")
    with tb_magalu:
        df_editado_magalu = st.data_editor(df_cartão_magalu, num_rows="dynamic")
elif filtro_abas == 'Investimentos':
    coluna1.header('Investimento')  
    coluna1.markdown(mensagem)
    df_editado_investimentos = st.data_editor(df_investimentos, num_rows="dynamic")
elif filtro_abas == 'Suplemento':
    coluna1.header('Suplemento')  
    coluna1.markdown(mensagem)
    df_editado_suplemento = st.data_editor(df_suplemento, num_rows="dynamic")
col1,col2 = st.sidebar.columns(2)
but_salvar = col1.button('Salvar Alteração')
but_limpar = col2.button('Limpar')
#salvando o arquivo modificado ------------------------------------------------------------------------------------------
if but_salvar:
    with pd.ExcelWriter(arquivos_tabela_cartão, engine='openpyxl') as writer:
        df_editado_cartão.to_excel(writer, sheet_name='CARTÃO', index=False)
        df_editado_pernambucanas.to_excel(writer, sheet_name='PERNAMBUCANAS', index=False)
        df_editado_xp .to_excel(writer, sheet_name='XP', index=False)
        df_editado_sicredi.to_excel(writer, sheet_name='SICREDI', index=False)
        df_editado_picpay.to_excel(writer, sheet_name='PICPAY', index=False)
        df_editado_magalu.to_excel(writer, sheet_name='MAGAZINE LUIZA', index=False)
    with pd.ExcelWriter(arquivos_tabela, engine='openpyxl') as writer:  
        df_editado_outrosgastos.to_excel(writer, sheet_name='OUTROS GASTOS', index=False) 
        df_editado_investimentos.to_excel(writer, sheet_name='INVESTIMENTO', index=False)
        df_editado_suplemento.to_excel(writer, sheet_name='SUPLEMENTO', index=False)
    st.success('Arquivo Salvo')
