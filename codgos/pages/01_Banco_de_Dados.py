#Importando funçoes---------------------------------------------------------------------------------
import streamlit as st 
from base_de_dado import funçao_cartao
from base_de_dado import funçao_investimento
from base_de_dado import funçao_suplemento
from base_de_dado import funçao_outros_gastos

st.set_page_config(layout="wide")


#criando na sidebar a seleçao da planilha que for analiazr-------------------------------------------
abas_de_pesquisa = ['Outros Gastos','Cartão','Investimentos','Proventos','Suplemento']
filtro_abas = st.sidebar.selectbox('Selecione as informaçoes que vc que analizar',abas_de_pesquisa)

#Lendo o aquivo exel .xlsx/ selecionando a tabela que deseja fazer a analize  -----------------------
mensagem = ('***Você Esta na Pagina de Visualização do Banco de Dados.***')
col1,col2,col3 = st.columns(3)
if filtro_abas == 'Outros Gastos':
    col2.title('Outros gastos')
    st.markdown(mensagem)
    st.session_state.funçao_outros_gastos = funçao_outros_gastos()
    df_aquivo_exel = st.session_state.funçao_outros_gastos
elif filtro_abas == 'Cartão':
    col2.title('Cartão')  
    st.markdown(mensagem)
    st.session_state.funçao_cartao = funçao_cartao()
    df_aquivo_exel = st.session_state.funçao_cartao
elif filtro_abas == 'Investimentos':
    col2.title('Investimento')  
    st.markdown(mensagem)
    st.session_state.função_investimento = funçao_investimento()
    df_aquivo_exel = st.session_state.função_investimento
elif filtro_abas == 'Proventos':
    col2.title('Proventos') 
    st.title('Esta aba esta INDISPONIVEL no momento')
    st.markdown(mensagem) 
elif filtro_abas == 'Suplemento':
    col2.title('Suplemento')  
    st.markdown(mensagem)
    df_aquivo_exel = funçao_suplemento()
else:
    st.write('estas imformaçoes esta imcorretas')

# Função de formatação personalizada trocando "," por "." na casa dos milhares e vise versa-----------------
def formatar_numero(x):
    if isinstance(x, float) or isinstance(x, int):
        return f"{x:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
    return x
df_formatado = df_aquivo_exel.applymap(formatar_numero) # type: ignore

#filtro---------------------------------------------filtro--------------------------------------------------
#filtro///listas de colunas separadas por types---------------------------------------------------------------
colunas_numero = list(df_aquivo_exel.select_dtypes(include=['int64']).columns) + list(df_aquivo_exel.select_dtypes(include=['float64']).columns)  
colunas_obj_object = list(df_aquivo_exel.select_dtypes(include=['object']).columns)
 
#Fazendo o seleção de colunas e de linhas para aparecer na sidebar-------------------------------------------

col1,col2 = st.sidebar.columns(2)
coluna_filtro = col1.selectbox('Selecione á coluna:',list(df_aquivo_exel.columns))

#filtro///butão para realizar o filtro de coluna e linha-------------------------------------------------------
but_filtrar = col1.button('Filtrar')  

#filtro2/// if's para fazer um segundo filtro de colunas de acordo com o nessesario-----------------------------
if coluna_filtro in colunas_numero:
    filtro_maior_menor = col2.selectbox('Friltrar por:',['Maior valor','Menor valor'])
    if but_filtrar:
        if filtro_maior_menor == 'Maior valor':
            df_coluna_desc = df_aquivo_exel.sort_values(by=coluna_filtro, ascending=False) 
            st.write(df_coluna_desc.applymap(formatar_numero)) # type: ignore
        elif filtro_maior_menor == 'Menor valor':
            df_coluna_cresc = df_aquivo_exel.sort_values(by=coluna_filtro, ascending=True) 
            st.write(df_coluna_cresc.applymap(formatar_numero))  # type: ignore
    else:
        st.write(df_formatado)  
elif coluna_filtro in colunas_obj_object:
    linha_filtro = col2.selectbox('Selecione a indice:',list(df_aquivo_exel[coluna_filtro].unique()))
    if but_filtrar:
        st.write(df_formatado[df_formatado[coluna_filtro] == linha_filtro])
    else:
        st.write(df_formatado) 
but_limpar = col2.button('Limpar')
