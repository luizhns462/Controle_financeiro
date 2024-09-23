#importando ferramentas para o codgo 
from pathlib import Path
import pandas as pd
import requests
from bs4 import BeautifulSoup
import pendulum
from datetime import  datetime

#buscando informaçoes de 'agora' 
data_agora = pendulum.now()
#dia 
dia = data_agora.strftime('%d')
#mes
mes = data_agora.strftime('%m')
#data ano para aparecer o ano como '2024'
ano = '20' + data_agora.strftime('%y')
#data completa 
mes_ano = data_agora.strftime('%m/%y')
dt_agora = data_agora.strftime('%d/%m'+'20'+'/%y')
#hora,mituto, e segundo exato
hora = data_agora.strftime('%H:%M:%S')
#formatando para ter o mes sem o '0'
mes = mes.replace('0','')

#lista de meses por extenson para os dataframe 
meses_portugues = {
    1: 'JANEIRO', 2: 'FEVEREIRO', 3: 'MARÇO', 4: 'ABRIL',
    5: 'MAIO', 6: 'JUNHO', 7: 'JULHO', 8: 'AGOSTO',
    9: 'SETEMBRO', 10: 'OUTUBRO', 11: 'NOVEMBRO', 12: 'DEZEMBRO'}  


#criando o caminho do arquivo para a leitura dos dataframe 
pasta_arquivo = Path(__file__).parents[1] / 'Arquivos'
arquivos_tabela = pasta_arquivo / 'CUSTOS E INVESTIMENTOS02.xlsx'
arquivos_tabela_cartão = pasta_arquivo / 'ARQUIVO CARTÃO.xlsx'


#@st.cache_data   
#criando tabela de gastos no cartão e das tabelas do estrato de cada cartão
def funçao_cartao():
    # lendo arquivo cartão
    df_exel_cartão = pd.read_excel(arquivos_tabela_cartão,sheet_name='CARTÃO')
    #criando, modificando e atualizando arquivo
    df_exel_cartão['DATA'] = pd.to_datetime(df_exel_cartão['DATA']) 
    df_exel_cartão.insert(1,'ANO',df_exel_cartão['DATA'].dt.year)
    df_exel_cartão['DATA'] = df_exel_cartão['DATA'].dt.month.map(meses_portugues)  
    df_exel_cartão['ANO'] = df_exel_cartão['ANO'].astype(str)
    df_exel_cartão['TOTAL'] = (df_exel_cartão['PERNAMBUCANAS']
                                + df_exel_cartão['XP'] 
                                + df_exel_cartão['PICPAY'] 
                                + df_exel_cartão['SICREDI']
                                + df_exel_cartão['MAGAZINE LUIZA'])
    #crianod uma lista com todos os df
    df_aquivo_exel = df_exel_cartão
    return  df_aquivo_exel

def função_pernabucanas():
        # lendo arquivo cartão
    df_exel_cartão = pd.read_excel(arquivos_tabela_cartão,sheet_name='PERNAMBUCANAS')
    return df_exel_cartão
def função_xp():
        # lendo arquivo cartão
    df_exel_cartão = pd.read_excel(arquivos_tabela_cartão,sheet_name='XP')
    return df_exel_cartão
def função_sicredi():
    df_exel_cartão = pd.read_excel(arquivos_tabela_cartão,sheet_name='SICREDI')
    return df_exel_cartão 
def função_picpay():
    df_exel_cartão = pd.read_excel(arquivos_tabela_cartão,sheet_name='PICPAY')
    return df_exel_cartão 
def função_magalu():
        # lendo arquivo cartão
    df_exel_cartão = pd.read_excel(arquivos_tabela_cartão,sheet_name='MAGAZINE LUIZA')
    return df_exel_cartão
#@st.cache_data   
#criando tabela de investimento
def funçao_investimento():
    #lendo arquivo
    df_aquivo_exel = pd.read_excel(arquivos_tabela,sheet_name='INVESTIMENTO')
    #lista de nomes para pesquisa
    lista_TICKER = list(df_aquivo_exel['TICKER'])
    lista_TIPO = list(df_aquivo_exel['TIPO'])
    #indice para atulização e finalizão do sistema de repetição (for)
    indice = 0
    #criando as listas que vão formar a tabela 
    lista_nomes_acao = []
    lista_nomes_cripto = []
    lista_preco_acao = []
    lista_preco_usd_cripto = []
    lista_preco_brl_cripto = []
    #extrutura para pesquisar o valor e o nome dos ativos online 
    for tipo in lista_TIPO:
        #expecificando o tipo de ativo para fazer pesquisa mais expesifica 
        if tipo != 'cripto':
            #atualizando o indice 
            indice  = indice +1
            #buscando o nome do ativo na lista de ativos 
            impresa = lista_TICKER[indice-1]
            # Fazendo a requisição HT
            resposta = requests.get("https://www.google.com/finance/quote/"+ impresa + ":BVMF?hl=pt")
            # Parsing do HTML
            soup = BeautifulSoup(resposta.text, 'html.parser')
            # Buscando o elemento que contém o valor
            elemento = soup.find('div', class_='YMlKec fxKbKc') 
            # Buscando o elemento que contem o nome 
            nome = soup.find('div', class_='zzDege')
            # extraindo o valor, limpando o elemento e mudando o valor para o padrão americano para não dar erro no (float)
            if elemento:
                valor = elemento.get_text().strip()
                valor = valor[-5:]
                valor = valor.replace('.','').replace(',','.').strip()
            else:
                valor = 'Valor não encontrado'
            #Extraindo o texto do elemento e limpando o valor   
            if nome:
                nome_impresa = nome.get_text().strip()
            else:
                nome_impresa = 'Nome não encontrado'
            #adicionando valores na lista 
            lista_nomes_acao.append(nome_impresa)
            lista_preco_acao.append(valor)
        #buscando o valor br, buscando o valor usa e os nomes dos ativos online 
        elif tipo == 'cripto':
            #atualizando i indice 
            indice = indice +1
            #buscando o nome do ativo na lista de ativos 
            cripto = lista_TICKER[indice-1]
            # Fazendo a requisição HT
            resposta = requests.get('https://www.google.com/finance/quote/' +cripto +'-USD?hl=pt&window=6M')
            resposta_br = requests.get('https://www.google.com/finance/quote/'+cripto+'-BRL?hl=pt')
            # Parsing do HTML
            soup = BeautifulSoup(resposta.text, 'html.parser')
            soup_br = BeautifulSoup(resposta_br.text, 'html.parser')
            # Buscando o elemento que contém o valor
            elemento = soup.find('div', class_='YMlKec fxKbKc')
            elemento_br = soup_br.find('div', class_='YMlKec fxKbKc')
            # Buscando o elemento que contem o nome 
            nome = soup.find('div',class_='zzDege')
            # Extraindo o valor usa e passando para o padrão usa para não dar erro no (float)
            if elemento:
                valor = elemento.get_text().strip().replace('R$', '').replace('\xa0', '').strip()
                valor = valor.replace('.','').replace(',','.').strip()
                valor = float(valor)
            else:
                valor = 'Valor não encontrado'
            # Extraindo o valor br e passando para o padrão usa para não dar erro no (float)   
            if elemento_br:
                valor_br = elemento_br.get_text().strip().replace('R$', '').replace('\xa0', '').replace('.','').replace(',','.').strip()
                valor_br = float(valor_br)
            else:
                valor = 'Valor não encontrado'
            # Extraindo o texto do elemento e limpando o valor
            if nome:
                nome_cripto = nome.get_text().strip()
            else:
                nome_cripto = 'Nome não encontrado'
            #adicionando nas lista 
            lista_preco_brl_cripto.append(valor_br)
            lista_preco_usd_cripto.append(valor)
            lista_nomes_cripto.append(nome_cripto)
            # Modificando, criando e atualizando aquivo exel
    df_aquivo_exel.insert(2,'NOME',lista_nomes_acao + lista_nomes_cripto)
    df_aquivo_exel['COTAÇÃO ATUAL'] = lista_preco_acao + lista_preco_brl_cripto
    df_aquivo_exel['VALOR BRUTO'] = df_aquivo_exel['QUANTIDADE'] * df_aquivo_exel['PREÇO MEDIO']
    df_aquivo_exel['VALOR CORRIGIDO'] = df_aquivo_exel['QUANTIDADE'].astype(float) * df_aquivo_exel['COTAÇÃO ATUAL'].astype(float)
    df_aquivo_exel['LUCRO/PREJUÍZO'] = (df_aquivo_exel['QUANTIDADE']
                                         * df_aquivo_exel['COTAÇÃO ATUAL'].astype(float) 
                                         - df_aquivo_exel['VALOR BRUTO'].astype(float))
    return df_aquivo_exel

#@st.cache_data  
def funçao_suplemento():
    #lendo aquivo
    df_aquivo_exel = pd.read_excel(arquivos_tabela,sheet_name='SUPLEMENTO')
    #criando colunas 
    df_aquivo_exel.insert(2,'QUANTIDADE DE DOSE',df_aquivo_exel['QUANTIDADE TOTAL'] / df_aquivo_exel['DOSE'])
    df_aquivo_exel.insert(4,'PREÇO POR DOSE',df_aquivo_exel['PREÇO TOTAL'] / df_aquivo_exel['QUANTIDADE DE DOSE'])
    df_aquivo_exel.insert(5,'PREÇO MENSAL',df_aquivo_exel['PREÇO POR DOSE'] * 30 ) 
    return df_aquivo_exel



#@st.cache_data  
def funçao_outros_gastos():
    #lendo aquivo 
    df_aquivo_exel = pd.read_excel(arquivos_tabela,sheet_name='OUTROS GASTOS')
    df_aquivo_exel['DATA'] = df_aquivo_exel['DATA'].astype(str)
    return df_aquivo_exel

#@st.cache_data  
def funçao_salario():
    conta_xp = 67.28
    conta_picpay = 98.46
    conta_sicred = 7.83
    df_aquivo_exel = pd.read_excel(arquivos_tabela,sheet_name='OUTROS GASTOS')
    salario = df_aquivo_exel[(df_aquivo_exel['FORMA DE PAGAMENTO'] == 'CONTA-SALARIO')]
    salario = sum(salario['VALOR'])
    valor_em_conta = conta_picpay+conta_sicred+conta_xp+salario
    lista_valores = [salario,valor_em_conta]
    return lista_valores

#@st.cache_data  
def função_custo_mensal():
    #buscando os gastos em dinheiro ou tranferencia 
    df_outros_gastos = pd.read_excel(arquivos_tabela,sheet_name='OUTROS GASTOS')  
    # Convertendo a coluna de datas para datetime
    df_outros_gastos['DATA'] = pd.to_datetime(df_outros_gastos['DATA'], format='%d/%m/%Y')
    #criando as variaveis com valor zero para não dar erro no final 
    lista_de_datas = (df_outros_gastos['DATA'].dt.month).unique()
    # Definindo o mês e ano para o fechamento
    
    ano = '20' + data_agora.strftime('%y')
    dia= data_agora.strftime('%d')
    dia = int(dia)
    ano = int(ano)

    df_custo_mensal_final = pd.DataFrame()
    for dt_mes in lista_de_datas:
        mes= dt_mes
        # Calculando as datas de abertura e fechamento
        dta_agora= datetime(ano,mes,dia)
        data_abertura = datetime(ano, mes, 10)

        data_abertura = datetime(ano, mes, 10)
        if mes == 12:
            data_fechamento = datetime(ano + 1, 1, 10) 
        else:
            data_fechamento = datetime(ano, mes + 1, 10)


        # Filtrando o DataFrame para o intervalo de datas
        df_filtrado = df_outros_gastos[(df_outros_gastos['DATA'] >= data_abertura) & (df_outros_gastos['DATA'] < data_fechamento)]
        df_pessoal = df_filtrado[(df_filtrado['DEVEDOR'] == 'PESSOAL') & 
                                (df_filtrado['MODALIDADE'] == 'PAGAMENTO') & 
                                (df_filtrado['DESCRIÇÃO GERAL'] != 'FATURA')]
        soma_pess_outg = sum(df_pessoal['VALOR'])
        df_terceiro = df_filtrado[(df_filtrado['DEVEDOR'] == 'TERCEIRO') & 
                                (df_filtrado['MODALIDADE'] == 'PAGAMENTO') & 
                                (df_filtrado['DESCRIÇÃO GERAL'] != 'FATURA')]
        soma_terceiros_outg = sum(df_terceiro['VALOR'])

        #buscando o gasto do mes correto para a tabela custo mensal 
        #lendo arquivo pois a funçao 'def' tem formataçao nas datas que eu preciso usar
        excel_file = pd.ExcelFile(arquivos_tabela_cartão)
        sheet_names = excel_file.sheet_names
        lis_deve_terc = []
        soma_lis_terc = 0
        lis_deve_pess = []
        soma_lis_pess = 0
        for planilha in sheet_names:
            if planilha == 'XP' or planilha =='PICPAY' or planilha =='SICREDI':
                df_exel = pd.read_excel(arquivos_tabela_cartão,sheet_name=planilha)
            
                lis_deve = list(df_exel['DEVEDOR'])
                lis_dt_pg = list(df_exel['DATA PAGAMENTO'].dt.month)
                lis_dt_pg_ano = list(df_exel['DATA PAGAMENTO'].dt.year)    
                indice = 0 
                for data in lis_dt_pg:
                    indice += 1
                    ano_lis = lis_dt_pg_ano[indice-1]
                    if int(data) == int(mes) and int(ano_lis) == int(ano):
                        devedor = lis_deve[indice-1]
                        if devedor == 'TERCEIRO':
                            lis_deve_terc.append(df_exel['VALOR'][indice-1 ])
                            soma_lis_terc  = sum(lis_deve_terc)
                        elif devedor == 'PESSOAL':
                            lis_deve_pess.append(df_exel['VALOR'][indice-1])   
                            soma_lis_pess = sum(lis_deve_pess)

        #g_mes_menos_cart = g_mes_sup_dinhero + g_mes_outg + g_terceiros_outg 
        g_mes_terceiro = soma_lis_terc + soma_terceiros_outg
        g_mes_cart = soma_lis_pess + soma_lis_terc  
        g_em_dinheiro = soma_terceiros_outg + soma_pess_outg 
        total = g_mes_cart + g_em_dinheiro
        g_mes_pess = total - g_mes_terceiro
        df_custo_mensal = pd.DataFrame({
                'MÊS':[data_abertura],
                'ANO':[data_abertura.year],
                'GASTO NO CARTÃO':[g_mes_cart],
                'OUTROS GASTOS':[g_em_dinheiro],
                'GASTOS COM TERCEIRO':[g_mes_terceiro],
                'TOTAL PESSOAL':[g_mes_pess],
                'TOTAL':[total]
                })
        df_custo_mensal['MÊS'] = pd.to_datetime(df_custo_mensal['MÊS']) 
        df_custo_mensal['MÊS'] = df_custo_mensal['MÊS'].dt.month.map(meses_portugues)  
        df_custo_mensal['MÊS'] = df_custo_mensal['MÊS'].astype(str)
        df_custo_mensal['ANO'] = df_custo_mensal['ANO'].astype(str)
        df_custo_mensal_final = pd.concat([df_custo_mensal_final, df_custo_mensal], axis=0)
    return df_custo_mensal_final




