#importando ferramentas para o codgo 
from pathlib import Path
import pandas as pd
import requests
from bs4 import BeautifulSoup
import pendulum
from datetime import  datetime , timedelta
import time 

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

   

#criando tabela de gastos no cartão e das tabelas do estrato de cada cartão
def funçao_cartao():
    df_exel_cartão_xp = pd.read_excel(arquivos_tabela_cartão,sheet_name='XP')
    df_exel_cartão_sicredi = pd.read_excel(arquivos_tabela_cartão,sheet_name='SICREDI')
    df_exel_cartão_picpay = pd.read_excel(arquivos_tabela_cartão,sheet_name='PICPAY')
    df_exel_cartão_xp['DATA PAGAMENTO'] = pd.to_datetime(df_exel_cartão_xp['DATA PAGAMENTO'], format='%d/%m/%Y', errors='coerce')
    df_exel_cartão_picpay['DATA PAGAMENTO'] = pd.to_datetime(df_exel_cartão_picpay['DATA PAGAMENTO'], format='%d/%m/%Y', errors='coerce')
    df_exel_cartão_sicredi['DATA PAGAMENTO'] = pd.to_datetime(df_exel_cartão_sicredi['DATA PAGAMENTO'], format='%d/%m/%Y', errors='coerce')

    df_final = pd.DataFrame()
    if len(df_exel_cartão_xp['DATA PAGAMENTO'].unique()) == len(df_exel_cartão_sicredi['DATA PAGAMENTO'].unique()) == len(df_exel_cartão_picpay['DATA PAGAMENTO'].unique()):
        meses_fechamento = df_exel_cartão_picpay['DATA PAGAMENTO'].unique()
        for mes in meses_fechamento:
            df_picpay = df_exel_cartão_picpay[df_exel_cartão_picpay['DATA PAGAMENTO'].dt.month == mes.month]
            df_sicredi = df_exel_cartão_sicredi[df_exel_cartão_sicredi['DATA PAGAMENTO'].dt.month == mes.month]
            df_xp = df_exel_cartão_xp[df_exel_cartão_xp['DATA PAGAMENTO'].dt.month == mes.month]
            df_01 = pd.DataFrame({'MÊS':[mes],
                                'ANO':[mes],
                                'XP':[sum(df_xp['VALOR'])],
                                'SICREDI':[sum(df_sicredi['VALOR'])],
                                'PICPAY':[sum(df_picpay['VALOR'])],
                                'TOTAL':[sum(df_xp['VALOR'])+sum(df_sicredi['VALOR'])+sum(df_picpay['VALOR'])]
                                                        }) 
            df_01['MÊS'] = df_01['MÊS'].dt.month.map(meses_portugues)
            df_01['ANO'] = df_01['ANO'].dt.year
            df_01['MÊS'] = df_01['MÊS'].astype(str)
            df_01['ANO'] = df_01['ANO'].astype(str)  
            df_final = pd.concat([df_final,df_01])
    return  df_final



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
   


def funçao_investimento():
    #criando tabela de investimento
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
    lista_nomes_fiis = []
    lista_preco_fiis = []
    #extrutura para pesquisar o valor e o nome dos ativos online 
    for tipo in lista_TIPO:
        #expecificando o tipo de ativo para fazer pesquisa mais expesifica 
        if tipo == 'ação':
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
        elif tipo == 'FIIs':
            #atualizando o indice 
            indice  = indice +1
            #buscando o nome do ativo na lista de ativos 
            fiis = lista_TICKER[indice-1]
            # Fazendo a requisição HT
            resposta = requests.get("https://www.google.com/finance/quote/"+ fiis +":BVMF?hl=pt")
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
                nome_fiis = nome.get_text().strip()
            else:
                nome_fiis = 'Nome não encontrado'
            #adicionando valores na lista 
            lista_nomes_fiis.append(nome_fiis)
            lista_preco_fiis.append(valor)


            # Modificando, criando e atualizando aquivo exel
    df_aquivo_exel.insert(2,'NOME',lista_nomes_acao + lista_nomes_cripto + lista_nomes_fiis)
    df_aquivo_exel['COTAÇÃO ATUAL'] = lista_preco_acao + lista_preco_brl_cripto + lista_preco_fiis
    df_aquivo_exel['VALOR BRUTO'] = df_aquivo_exel['QUANTIDADE'] * df_aquivo_exel['PREÇO MEDIO']
    df_aquivo_exel['VALOR CORRIGIDO'] = df_aquivo_exel['QUANTIDADE'].astype(float) * df_aquivo_exel['COTAÇÃO ATUAL'].astype(float)
    df_aquivo_exel['LUCRO/PREJUÍZO'] = (df_aquivo_exel['QUANTIDADE']
                                         * df_aquivo_exel['COTAÇÃO ATUAL'].astype(float) 
                                         - df_aquivo_exel['VALOR BRUTO'].astype(float))
    return df_aquivo_exel



def funçao_suplemento():
    #lendo aquivo
    df_aquivo_exel = pd.read_excel(arquivos_tabela,sheet_name='SUPLEMENTO')
    #criando colunas 
    df_aquivo_exel.insert(2,'QUANTIDADE DE DOSE',df_aquivo_exel['QUANTIDADE TOTAL'] / df_aquivo_exel['DOSE'])
    df_aquivo_exel.insert(4,'PREÇO POR DOSE',df_aquivo_exel['PREÇO TOTAL'] / df_aquivo_exel['QUANTIDADE DE DOSE'])
    df_aquivo_exel.insert(5,'PREÇO MENSAL',df_aquivo_exel['PREÇO POR DOSE'] * 30 ) 
    return df_aquivo_exel


  
def funçao_outros_gastos():
    #lendo aquivo 
    df_aquivo_exel = pd.read_excel(arquivos_tabela,sheet_name='OUTROS GASTOS')
    df_aquivo_exel['DATA'] = df_aquivo_exel['DATA'].astype(str)
    return df_aquivo_exel
  


def funçao_salario():
    conta_xp = 23.99
    conta_picpay = 614.37
    conta_sicred = 3.91
    df_aquivo_exel = pd.read_excel(arquivos_tabela,sheet_name='OUTROS GASTOS')
    recebimento = df_aquivo_exel[(df_aquivo_exel['MODALIDADE'] == 'RECEBIMENTO')]
    recebimento = sum(recebimento['VALOR'])
    valor_em_conta = conta_picpay + conta_sicred + conta_xp +  recebimento
    debito = df_aquivo_exel[(df_aquivo_exel['MODALIDADE'] == 'PAGAMENTO')]
    debito = sum(debito['VALOR'])
    valor_na_conta =  valor_em_conta - debito
    return valor_na_conta
  


def função_custo_mensal():
    #buscando os gastos em dinheiro ou tranferencia 
    df_outros_gastos = pd.read_excel(arquivos_tabela,sheet_name='OUTROS GASTOS')  
    # Convertendo a coluna de datas para datetime
    df_outros_gastos['DATA'] = pd.to_datetime(df_outros_gastos['DATA'], format='%d/%m/%Y', errors='coerce')
    #criando as variaveis com valor zero para não dar erro no final 
    lista_dos_ano = (df_outros_gastos['DATA'].dt.year).unique()
    primeira_info = df_outros_gastos['DATA'].iloc[0].month
    ultima_info = (df_outros_gastos['DATA'].iloc[-1]).month
    # Definindo o mês e ano para o fechamento
    list_dtabertura = ['11/01','11/02','11/03','11/04','11/05','11/06','11/07','11/08','11/09','11/10','11/11','11/12']
    list_fechamento = ['10/02','10/03','10/04','10/05','10/06','10/07','10/08','10/09','10/10','10/11','10/12','10/01']
    df_custo_mensal_final = pd.DataFrame()
    for ano in lista_dos_ano: 
        df_fil_ano = df_outros_gastos[(df_outros_gastos['DATA'].dt.year) == int(ano)]
        primeira_info = df_fil_ano['DATA'].iloc[0].month
        ultima_info = df_fil_ano['DATA'].iloc[-1].month
        for mes in range(primeira_info,ultima_info+2):
            if mes == 1:
                continue
            if mes == 13:
                data_fechamento = datetime.strptime(list_fechamento[int(mes)-2] +'/'+ str(ano+1), '%d/%m/%Y')
            else:
                data_fechamento = datetime.strptime(list_fechamento[int(mes)-2] +'/'+ str(ano), '%d/%m/%Y')
            data_abertura = datetime.strptime(list_dtabertura[int(mes)-2] +'/'+ str(ano), '%d/%m/%Y')
   

            # Filtrando o DataFrame para o intervalo de datas
            df_filtrado = df_outros_gastos[(df_outros_gastos['DATA'] >= data_abertura) & (df_outros_gastos['DATA'] <= data_fechamento)]
            df_filtrado = df_filtrado[(df_filtrado['MODALIDADE'] == 'PAGAMENTO') & 
                                    (df_filtrado['DESCRIÇÃO GERAL'] != 'FATURA') &
                                    (df_filtrado['MODALIDADE'] != 'TRANFERÊNCIA')]
            df_pessoal = df_filtrado[(df_filtrado['DEVEDOR'] == 'PESSOAL')]
            soma_pess_outg = sum(df_pessoal['VALOR'])
            df_terceiro = df_filtrado[(df_filtrado['DEVEDOR'] == 'TERCEIRO')]
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
                df_exel = pd.read_excel(arquivos_tabela_cartão,sheet_name=planilha)
                df_exel['DATA PAGAMENTO'] = pd.to_datetime(df_exel['DATA PAGAMENTO'])
                df_exel = df_exel[df_exel['DATA PAGAMENTO'].dt.month == data_fechamento.month]
                df_deve_terc = df_exel[(df_exel['DEVEDOR'] == 'TERCEIRO')]
                lis_deve_terc.append(sum(df_deve_terc['VALOR']))
                soma_lis_terc  = sum(lis_deve_terc)
                df_deve_pess = df_exel[(df_exel['DEVEDOR'] == 'PESSOAL')]
                lis_deve_pess.append(sum(df_deve_pess['VALOR']))
                soma_lis_pess = sum(lis_deve_pess)
              

            #g_mes_menos_cart = g_mes_sup_dinhero + g_mes_outg + g_terceiros_outg 
            g_mes_terceiro = soma_lis_terc + soma_terceiros_outg
            g_mes_cart = soma_lis_pess + soma_lis_terc
            print(g_mes_cart)
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



def função_cotações():
    #cotação do indices das bousas de valores Ibovespa  e S&P500\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\
    ibov = requests.get("https://www.google.com/finance/quote/IBOV:INDEXBVMF?hl=pt")
    resposta = requests.get("https://www.google.com/finance/quote/.INX:INDEXSP?hl=pt")
    # Parsing do HTML
    soup_ibov = BeautifulSoup(ibov.text, 'html.parser')
    soup = BeautifulSoup(resposta.text, 'html.parser')
    # Buscando o elemento que contém o valor
    elemento_ibov = soup_ibov.find('div', class_='YMlKec fxKbKc')
    elemento_ult_ibov = soup_ibov.find('div', class_='P6K39c')
    elemento = soup.find('div', class_='YMlKec fxKbKc')
    elemento_ult = soup.find('div', class_='P6K39c')
    # extraindo o valor, limpando o elemento e mudando o valor para o padrão americano para não dar erro no (float)
    if elemento_ibov:
        valor_ibov = elemento_ibov.get_text().strip()[-10:]
        valor_ibov = valor_ibov.replace('.','').replace(',','.').strip()
        valor_ibov = float(valor_ibov)
    else:
        valor_ibov = 'Valor não encontrado'
    if elemento_ult_ibov:
        valor_ult_ibov = elemento_ult_ibov.get_text().strip()[-10:]
        valor_ult_ibov = valor_ult_ibov.replace('.','').replace(',','.').strip()
        valor_ult_ibov = float(valor_ult_ibov)
    else:
        valor_ult_ibov = 'Valor não encontrado'
    #Extraindo o texto do elemento e limpando o valor     
    if elemento:
        valor = elemento.get_text().strip()[-8:]
        valor = valor.replace('.','').replace(',','.').strip()
        valor = float(valor)
    else:
        valor = 'Valor não encontrado'
    if elemento_ult:
        valor_ult = elemento_ult.get_text().strip()[-8:]
        valor_ult = valor_ult.replace('.','').replace(',','.').strip()
        valor_ult = float(valor_ult)
    else:
        valor_ult = 'Valor não encontrado'
    #buscando os valores dos criptoativos\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\
    resposta = requests.get('https://www.google.com/finance/quote/BTC-USD?hl=pt&window=6M')
    resposta_eth = requests.get('https://www.google.com/finance/quote/ETH-USD?hl=pt&window=6M')
    # Parsing do HTML
    soup = BeautifulSoup(resposta.text, 'html.parser')
    soup_eth = BeautifulSoup(resposta_eth.text, 'html.parser')
    # Buscando o elemento que contém o valor
    elemento_btc = soup.find('div', class_='YMlKec fxKbKc')
    elemento_utl_btc = soup.find('div', class_='P6K39c')
    elemento_eth = soup_eth.find('div', class_='YMlKec fxKbKc')
    elemento_ult_eth = soup_eth.find('div', class_='P6K39c')
    # Extraindo o valor usa e passando para o padrão usa para não dar erro no (float)
    if elemento_btc:
        valor_btc = elemento_btc.get_text().strip().replace('R$', '').replace('\xa0', '').strip()
        valor_btc = valor_btc.replace('.','').replace(',','.').strip()
        valor_btc = float(valor_btc)
    else:
        valor_btc = 'Valor não encontrado'
    if elemento_utl_btc:
        valor_ult_btc = elemento_utl_btc.get_text().strip().replace('R$', '').replace('\xa0', '').strip()
        valor_ult_btc = valor_ult_btc.replace('.','').replace(',','.').strip()
        valor_ult_btc = float(valor_ult_btc)
    else:
        valor_ult_btc = 'Valor não encontrado'
    # Extraindo o valor br e passando para o padrão usa para não dar erro no (float)   
    if elemento_eth:
        valor_eth = elemento_eth.get_text().strip().replace('R$', '').replace('\xa0', '').replace('.','').replace(',','.').strip()
        valor_eth = float(valor_eth)
    else:
        valor_eth = 'Valor não encontrado'
    if elemento_ult_eth:
        valor_ult_eth = elemento_ult_eth.get_text().strip().replace('R$', '').replace('\xa0', '').replace('.','').replace(',','.').strip()
        valor_ult_eth = float(valor_ult_eth)
    else:
        valor_ult_eth = 'Valor não encontrado'
    #cotação do dolar \\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\
    requisicao = requests.get("https://economia.awesomeapi.com.br/last/USD-BRL")
    requisicao_dolar = requisicao.json()
    cotacao_dolar = requisicao_dolar["USDBRL"]["bid"]

    data_ontem = (datetime.now() - timedelta(days=1))
    data_ontem = data_ontem.strftime("%m-%d-%Y")
    site = requests.get(f"https://olinda.bcb.gov.br/olinda/servico/PTAX/versao/v1/odata/CotacaoDolarDia(dataCotacao=@dataCotacao)?@dataCotacao='{data_ontem}'&$top=100&$format=json&$select=cotacaoCompra")
    time.sleep(2)
    requisicao_ult_dolar= site.json()
    ult_valor_dolar = requisicao_ult_dolar["value"][0]["cotacaoCompra"]


    lista_ativos = pd.DataFrame({'IBOV':[valor_ibov],
                                 'ULTIMO FECHAMENTO IBOV':[valor_ult_ibov],
                                 'S&P500':[valor],
                                 'ULTIMO FECHAMENTO S&P500':[valor_ult],
                                 'BTC':[valor_btc],
                                 'ULTIMO FECHAMENTO BTC':[valor_ult_btc],
                                 'ETH':[valor_eth],
                                 'ULTIMO FECHAMENTO ETH':[valor_ult_eth],
                                 'DOLAR':[cotacao_dolar],
                                 'ULTIMO FECHAMENTO DOLAR':[ult_valor_dolar]})
    lista_ativos['DOLAR'] = lista_ativos['DOLAR'].astype(float)
    

    return lista_ativos



def função_divizão_gasto_mensais():
        #buscando os gastos em dinheiro ou tranferencia 
    df_outros_gastos = pd.read_excel(arquivos_tabela,sheet_name='OUTROS GASTOS')  
    # Convertendo a coluna de datas para datetime
    df_outros_gastos['DATA'] = pd.to_datetime(df_outros_gastos['DATA'], format='%d/%m/%Y', errors='coerce')
    #criando as variaveis com valor zero para não dar erro no final 
    lista_dos_ano = (df_outros_gastos['DATA'].dt.year).unique()
    primeira_info = df_outros_gastos['DATA'].iloc[0].month
    ultima_info = (df_outros_gastos['DATA'].iloc[-1]).month
    # Definindo o mês e ano para o fechamento
    list_dtabertura = ['11/01','11/02','11/03','11/04','11/05','11/06','11/07','11/08','11/09','11/10','11/11','11/12']
    list_fechamento = ['10/02','10/03','10/04','10/05','10/06','10/07','10/08','10/09','10/10','10/11','10/12','10/01']
    df_custo_mensal_final = pd.DataFrame()
    lista_s = []
    for ano in lista_dos_ano: 
        df_fil_ano = df_outros_gastos[(df_outros_gastos['DATA'].dt.year) == int(ano)]
        primeira_info = df_fil_ano['DATA'].iloc[0].month
        ultima_info = df_fil_ano['DATA'].iloc[-1].month
        for mes in range(primeira_info,ultima_info+2):
            if mes == 1:
                continue
            if mes == 13:
                data_fechamento = datetime.strptime(list_fechamento[int(mes)-2] +'/'+ str(ano+1), '%d/%m/%Y')
            else:
                data_fechamento = datetime.strptime(list_fechamento[int(mes)-2] +'/'+ str(ano), '%d/%m/%Y')
            data_abertura = datetime.strptime(list_dtabertura[int(mes)-2] +'/'+ str(ano), '%d/%m/%Y')



            df_f = df_outros_gastos[(df_outros_gastos['DATA'] >= data_abertura) & (df_outros_gastos['DATA'] <= data_fechamento)]
            df_filtrado = df_outros_gastos[(df_outros_gastos['MODALIDADE'] == 'PAGAMENTO')&(df_outros_gastos['DESCRIÇÃO GERAL'] != 'TRANSFERÊNCIA')]
            lista_v = []
            lista_de_gastos = list(df_filtrado['DESCRIÇÃO GERAL'].unique())
            for gasto in lista_de_gastos:
                soma = 0
                df_gasto = df_f[df_f['DESCRIÇÃO GERAL'] == gasto]
                soma = sum(df_gasto['VALOR'])
                if soma:
                    lista_v.append(soma)
                else:
                    soma = 0
                    lista_v.append(soma)
                if lista_v and type(lista_v[0]) == str:
                    continue
                else:
                    lista_v.insert(0,str(data_abertura)) 
            lista_de_gastos.insert(0,'DATA')
            lista_s.append(lista_v)
            df = pd.DataFrame(lista_s, columns=lista_de_gastos)
            
    return df