#importando ferramentas para o codgo 
from pathlib import Path
import pandas as pd
import requests
from bs4 import BeautifulSoup
import pendulum
from datetime import  datetime , timedelta
import time 
import pdfplumber
from pypdf import PdfReader, PdfWriter
import os
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
import io
import numpy as np
import re
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
Banco_de_Dados21 = pasta_arquivo/ "Banco_de_Dados-2,1.xlsx"
#função de fitragem da aba investimentos
def extrair(linha):
    if not isinstance(linha, str):
        return None, None, None

    # Expressão regular para identificar os 3 grupos: movimentação, ticker, quantidade
    padrao = re.search(r'^(.*?)([A-Z]{4,5}\d{1,2})\s*S/?\s*(\d+)$', linha.strip())
    if padrao:
        movimentacao = padrao.group(1).strip()
        ticker = padrao.group(2).strip()
        quantidade = int(padrao.group(3))
        return movimentacao, ticker, quantidade
    else:
        return None, None, None
def extrair_lancamento(linha):
    linha = linha.strip()
    # Expressão regular para detectar padrão "TEXTO TICKER S/ <QUANTIDADE>"
    padrao = re.search(r'^(.*?)([A-Z]{4}[0-9])\s*S/?\s*(\d+)$', linha)
    if padrao:
        movimentacao = padrao.group(1).strip()
        ticker = padrao.group(2).strip()
        quantidade = int(padrao.group(3))
    else:
        # Tentar outro padrão: TEXTO TICKER (sem quantidade)
        padrao2 = re.search(r'^(.*?)([A-Z]{4}[0-9])$', linha)
        if padrao2:
            movimentacao = padrao2.group(1).strip()
            ticker = padrao2.group(2).strip()
            quantidade = None
        else:
            movimentacao = linha
            ticker = None
            quantidade = None
    return pd.Series([movimentacao, quantidade, ticker])
# Separar pastas de extratos e faturas
pastas_extrato = []
pastas_fatura = []

for pasta in os.listdir(pasta_arquivo):
    if pasta.lower().startswith('extrato'):
        pastas_extrato.append(pasta)
    elif pasta.lower().startswith('fatura'):
        pastas_fatura.append(pasta)

# Carregar índice de controle
df_banco = pd.read_excel(Banco_de_Dados21, sheet_name='Indices', engine='openpyxl')

# Criar DataFrame final
df_final = pd.DataFrame()
df_final_invest = pd.DataFrame()
# Verificar quantidade de arquivos de extrato
lista_arquivos = []
for pasta in pastas_extrato:
    caminho_pasta = pasta_arquivo / pasta
    lista_arquivos += os.listdir(caminho_pasta)

quantidade_arquivos = len(lista_arquivos)
quantidade_limite = df_banco.iloc[0, 0]

if quantidade_arquivos > quantidade_limite: # type: ignore
    for pasta in pastas_extrato:
        caminho_pasta = pasta_arquivo / pasta
        arquivos_pdf_csv = os.listdir(caminho_pasta)

        for arquivo in arquivos_pdf_csv:
            caminho_arquivo = caminho_pasta / arquivo

            if arquivo.lower().endswith('picpay.pdf'):
                with pdfplumber.open(caminho_arquivo) as pdf:
                    for i in range(0, len(pdf.pages)):
                        page = pdf.pages[i]
                        table = page.extract_table()
                        if table:
                            tabela_extrato = pd.DataFrame(table)
                            tabela_extrato.columns = ['Data', 'Descrição', 'Valor', 'Saldo', 'Saldo Sacável']
                            tabela_extrato = tabela_extrato.drop(index=0)
                            tabela_extrato['Data'] = tabela_extrato['Data'].str.replace('\n', ' ', regex=True)
                            tabela_extrato = tabela_extrato.drop(['Saldo', 'Saldo Sacável'], axis=1)
                            df_final = pd.concat([df_final, tabela_extrato], ignore_index=True)
                            df_final['Data'] = pd.to_datetime(df_final['Data'], dayfirst=True)

            elif arquivo.lower().endswith('xp.csv'):
                df = pd.read_csv(caminho_arquivo, sep=';')
                df.columns = ['Data','Descrição','Valor','Saldo']
                df = df[['Data', 'Descrição', 'Valor']]  # Mantém apenas colunas importantes
                df['Data'] = df['Data'].str.replace('Ã s', '  ')
                df['Data'] = df['Data'].str.replace('às', '  ')
                df_final = pd.concat([df_final, df], ignore_index=True)
                df_final['Data'] = pd.to_datetime(df_final['Data'], dayfirst=True)

            elif arquivo.lower().endswith('sicred.pdf'):
                # Preparar caminhos
                indice = len(arquivo) - 4
                arquivo_saida = arquivo[:indice] + '_editado' + arquivo[indice:]
                caminho_pdf_editado = caminho_pasta / arquivo_saida
                # Criar linhas verticais
                width, height = letter
                packet = io.BytesIO()
                can = canvas.Canvas(packet, pagesize=letter)
                can.setStrokeColorRGB(0, 0, 0)
                can.setLineWidth(1)
                can.line(100, 0, 100, height)
                can.save()
                packet.seek(0)
                # Criar linhas 2 verticais
                packet_1 = io.BytesIO()
                can_1 = canvas.Canvas(packet_1, pagesize=letter)
                can_1.setStrokeColorRGB(0, 0, 0)
                can_1.setLineWidth(1)
                can_1.line(490, 0, 490, height)
                can_1.save()
                packet_1.seek(0)
                # Criar linhas 3 verticais
                packet_2 = io.BytesIO()
                can_2 = canvas.Canvas(packet_2, pagesize=letter)
                can_2.setStrokeColorRGB(0, 0, 0)
                can_2.setLineWidth(1)
                can_2.line(30, 0, 30, height)
                can_2.save()
                packet_2.seek(0)
                # Criar linhas 4 verticais
                packet_3 = io.BytesIO()
                can_3 = canvas.Canvas(packet_3, pagesize=letter)
                can_3.setStrokeColorRGB(0, 0, 0)
                can_3.setLineWidth(1)
                can_3.line(565, 0, 565, height)
                can_3.save()
                packet_3.seek(0)
                # Carregar linhas e PDF original
                linha_pdf = PdfReader(packet)
                linha_pdf_1 = PdfReader(packet_1)
                linha_pdf_2 = PdfReader(packet_2)
                linha_pdf_3 = PdfReader(packet_3)
                pagina_linha = linha_pdf.pages[0]
                pagina_linha_1 = linha_pdf_1.pages[0]
                pagina_linha_2 = linha_pdf_2.pages[0]
                pagina_linha_3 = linha_pdf_3.pages[0]
                pdf_original = PdfReader(str(caminho_arquivo))
                escritor = PdfWriter()
                # Mesclar linhas em cada página
                for pagina in pdf_original.pages:
                    pagina.merge_page(pagina_linha)
                    pagina.merge_page(pagina_linha_1)
                    pagina.merge_page(pagina_linha_2)
                    pagina.merge_page(pagina_linha_3)
                    escritor.add_page(pagina)
                # Recortar a primeira página
                writer = PdfWriter()
                primeira_pagina = escritor.pages[0]
                primeira_pagina.mediabox.lower_left = (0, 0)
                primeira_pagina.mediabox.upper_right = (595, 490)
                writer.add_page(primeira_pagina)
                for pagina in escritor.pages[1:]:
                    writer.add_page(pagina)
                # Salvar PDF editado
                with open(caminho_pdf_editado, "wb") as f:
                    writer.write(f)
                # Ler PDF editado
                with pdfplumber.open(caminho_pdf_editado) as pdf:
                    for i in range(0, len(pdf.pages)):
                        page = pdf.pages[i]
                        table = page.extract_table()
                        if table:
                            tabela_extrato = pd.DataFrame(table)
                            primeira_coluna = tabela_extrato.iloc[:, 0]
                            coluna_modificada = pd.to_datetime(primeira_coluna, errors='coerce')
                            tabela_extrato = tabela_extrato[~coluna_modificada.isna()]
                            tabela_extrato.replace(r'^\s*$', np.nan, regex=True, inplace=True)
                            tabela_extrato.dropna(axis=1, how='any', inplace=True)
                            tabela_extrato.dropna(inplace=True)
                            if len(tabela_extrato.columns) == 3:
                                tabela_extrato.columns = ['Data', 'Descrição', 'Valor']
                                df_final = pd.concat([df_final, tabela_extrato], ignore_index=True)

            elif arquivo.lower().endswith('xpinvestimentos.xlsx') or arquivo.lower().endswith('clear.xlsx'):
                df_invest = pd.read_excel(caminho_arquivo)
                df_invest = df_invest.iloc[14:]
                indice = [0,4]
                df_invest.drop(columns=df_invest.columns[indice], inplace=True)
                df_invest.columns = ['Mov', 'Liquidação', 'Lançamento','Valor da Operação','Saldo']
                if arquivo.lower().endswith('xpinvestimentos.xlsx'):
                    df_invest['Instituição'] ='XP INVESTIMENTOS'
                elif arquivo.lower().endswith('clear.xlsx'):
                    df_invest['Instituição'] ='CLEAR CORRETORA'
                # Tenta converter a coluna 'liq' para datetime. Valores inválidos serão convertidos para NaT.
                df_invest['Data'] = pd.to_datetime(df_invest['Liquidação'], errors='coerce')
                # Agora, você pode verificar quais linhas têm um datetime válido (não NaT)
                df_invest = df_invest[df_invest['Data'].notna()]
                df_invest = df_invest.drop(['Liquidação','Saldo','Mov'], axis=1)
                df_invest['Entrada/Saída'] = 'Entrada'
                df_invest = df_invest[~(df_invest['Lançamento'].str.contains('NOTA',case=False,na=False))]
                df_invest = df_invest[~(df_invest['Lançamento'].str.contains('TED',case=False,na=False))]
                df_invest = df_invest[~(df_invest['Lançamento'].str.contains('TRANSFERÊNCIA',case=False,na=False))]
                df_invest = df_invest[~(df_invest['Lançamento'].str.contains('OPERAÇÕES',case=False,na=False))]
                df_invest[['Movimentação', 'Quantidade', 'Ticker']] = df_invest['Lançamento'].apply(extrair_lancamento)
                df_invest = df_invest.drop(['Lançamento'], axis=1)
                df_invest['Preço unitário'] = df_invest['Valor da Operação'] / df_invest['Quantidade']
                df_final_invest = pd.concat([df_final_invest,df_invest], ignore_index=True)
                df_final_invest['Data'] = pd.to_datetime(df_final_invest['Data'],dayfirst=True)

            elif arquivo.lower().endswith('clear_Antiga.xlsx'):
                df_clear = pd.read_excel(caminho_arquivo)
                df_clear = df_clear.iloc[6:]
                df_clear.columns = ['Liquidação', 'Mov', 'Lançamento','Valor da Operação','Saldo']
                # Tenta converter a coluna 'liq' para datetime. Valores inválidos serão convertidos para NaT.
                df_clear['Data'] = pd.to_datetime(df_clear['Liquidação'], errors='coerce')
                # Agora, você pode verificar quais linhas têm um datetime válido (não NaT)
                df_clear = df_clear[df_clear['Data'].notna()]
                df_clear = df_clear.drop(['Liquidação','Saldo','Mov'], axis=1)
                df_clear['Instituição'] ='CLEAR CORRETORA'
                df_clear['Entrada/Saída'] = 'Entrada'
                df_clear = df_clear[~(df_clear['Lançamento'].str.contains('NOTA',case=False,na=False))]
                df_clear = df_clear[~(df_clear['Lançamento'].str.contains('TED',case=False,na=False))]
                df_clear = df_clear[~(df_clear['Lançamento'].str.contains('TRANSFERÊNCIA',case=False,na=False))]
                df_clear = df_clear[~(df_clear['Lançamento'].str.contains('OPERAÇÕES',case=False,na=False))]
                df_clear[['Movimentação', 'Quantidade', 'Ticker']] = df_clear['Lançamento'].apply(extrair)
                df_clear = df_clear.drop(['Lançamento'], axis=1)
                df_clear['Preço unitário'] = df_clear['Valor da Operação'] / df_clear['Quantidade']
                df_final_invest = pd.concat([df_final_invest,df_clear], ignore_index=True)
                df_final_invest['Data'] = pd.to_datetime(df_final_invest['Data'],dayfirst=True)

            elif arquivo.lower().endswith('vend_b3.xlsx'):
                df_b3 = pd.read_excel(caminho_arquivo)
                df_b3['Instituição'] ='B3'
                df_final_invest = pd.concat([df_final_invest,df_b3], ignore_index=True)
                df_final_invest['Data'] = pd.to_datetime(df_final_invest['Data'],dayfirst=True)

            elif arquivo.lower().endswith('binance.csv'):
                df_binance = pd.DataFrame()
                df = pd.read_csv(caminho_arquivo, sep=',')
                df = df[(df['type'] != 'Deposit') & (df['type']!= 'Withdrawal')]
                #taduzindo e convertento a coluna type na coluna entrada/saida para cocatenar com o dfinvest
                df_binance['Entrada/Saída'] = df['type'].map({'Buy': 'Entrada',
                                                              'Sell': 'Saída',
                                                              'Receive': 'Entrada'})
                df_binance['Movimentação'] = df['type'].map({'Buy': 'Transferência - Liquidação',
                                                              'Sell': 'Transferência - Liquidação',
                                                              'Receive': 'Bonificação em Ativos'})
                df_binance['Data'] = pd.to_datetime(df['datetime_tz_BRT']).dt.strftime('%d/%m/%Y')
                #trazendo o nome dos ativos para a coluna
                df_binance['Ticker'] = df.apply(
                                            lambda x: x['received_currency'] if x['type'] in ['Buy', 'Receive'] else x['sent_currency'],
                                            axis=1
                                            )
                df_binance['Nome'] = df_binance['Ticker'] 
                df_binance['Nome'] =  df_binance['Nome'].map({'USDT': 'Tether a Real brasileiro',
                                                        'FDUSD': 'First Digital USD',
                                                        'BTC': ' Bitcoin',
                                                        'ETH':'Ether',
                                                        'BRL':'Real Brasileiro'})
                # ou use um dicionário de nomes
                df_binance['Instituição'] = 'Binance'
                #convertendo a quantidade 
                df_binance['Quantidade'] = df.apply(
                                                lambda x: x['received_amount'] if x['type'] in ['Buy', 'Receive', 'Deposit'] else x['sent_amount'],
                                                axis=1
                                                )
                df_binance['Valor da Operação'] = df[['sent_value_BRL', 'received_value_BRL']].max(axis=1)
                # 9. Preço unitário = valor / quantidade (evita divisão por zero)
                df_binance['Preço unitário'] = df_binance.apply(
                                                        lambda x: float(x['Valor da Operação']) / float(x['Quantidade']) if float(x['Quantidade']) != 0 else 0,
                                                        axis=1
                                                        )
                df_final_invest = pd.concat([df_final_invest,df_binance], ignore_index=True)
                df_final_invest['Data'] = pd.to_datetime(df_final_invest['Data'],dayfirst=True)
                
    # Atualizar índice no banco de dados
    df_banco.iloc[0, 0] = quantidade_arquivos 
    # Ajustar e salvar o DataFrame final
    df_final['Data'].astype(str)
    df_final['Data'] = pd.to_datetime(df_final['Data'], format='%m/%d/%Y', errors='coerce')
    df_final['Data'] = df_final['Data'].dt.normalize()
    df_final.sort_values(by='Data', inplace=True)
    def limpar_valores(coluna):
        return (
                coluna.astype(str)  # Garante que tudo é string
                .str.replace(r"R\$\s*", "", regex=True)  # Remove "R$" e espaços
                .str.replace(".", "", regex=False)  # Remove ponto de milhar
                .str.replace(",", ".", regex=False)  # Troca vírgula por ponto decimal
                .str.replace(r"[^0-9\.\-]", "", regex=True)  # Remove tudo, menos números, ponto e sinal de negativo
                 )
    df_final["Valor"] = limpar_valores(df_final["Valor"])
    df_final['Valor'].astype(float)
    # Ajustar e salvar o DataFrame final
    df_final_invest['Data'].astype(str)
    df_final_invest['Data'] = df_final_invest['Data'].dt.normalize()
    df_final_invest.sort_values(by='Data', inplace=True)
    df_final_invest['Quantidade'].astype(float)
    with pd.ExcelWriter(Banco_de_Dados21, engine='openpyxl', mode='a', if_sheet_exists='replace') as writer:
        df_final.to_excel(writer, sheet_name='Extrato', index=False)
        df_final_invest.to_excel(writer, sheet_name='Extrato_investimentos', index=False)
        df_banco.to_excel(writer, sheet_name='Indices', index=False)
    


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



def função_Banco_de_Dados21(): 
        df_outros_gastos = pd.read_excel(Banco_de_Dados21,sheet_name='Extrato') 
        df_outros_gastos = df_outros_gastos[df_outros_gastos['Valor']<0]
        return df_outros_gastos



def função_picpay():
    df_exel_cartão = pd.read_excel(arquivos_tabela_cartão,sheet_name='PICPAY')
    return df_exel_cartão 
   


def função_investimentos():

    l = 10
    return l



def funçao_cotação_investimento():
    #criando tabela de investimento
    #lendo arquivo
    df_aquivo_exel = pd.read_excel(arquivos_tabela,sheet_name='INVESTIMENTO')
    #lista de nomes para pesquisa
    df_acao = df_aquivo_exel[df_aquivo_exel['TIPO'] == 'ação']
    df_fiis = df_aquivo_exel[df_aquivo_exel['TIPO'] == 'FIIs' ]
    df_cripto = df_aquivo_exel[df_aquivo_exel['TIPO'] == 'cripto']
    lista_açoes = list(df_acao['TICKER'])
    lista_fiis = list(df_fiis['TICKER'])
    lista_cripto =list(df_cripto['TICKER'])


    #indice para atulização e finalizão do sistema de repetição (for)

    #criando as listas que vão formar a tabela 
    lista_nomes_acao = []
    lista_nomes_cripto = []
    lista_preco_acao = []
    lista_preco_usd_cripto = []
    lista_preco_brl_cripto = []
    lista_nomes_fiis = []
    lista_preco_fiis = []
    #extrutura para pesquisar o valor e o nome dos ativos online 
    
        #expecificando o tipo de ativo para fazer pesquisa mais expesifica 
    for impresa in lista_açoes:
        #atualizando o indice 
        #buscando o nome do ativo na lista de ativos 
        # Fazendo a requisição HT
        resposta = requests.get("https://www.google.com/finance/quote/'{impresa}':BVMF?hl=pt")
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
    for cripto in lista_cripto:
        #atualizando i indice 
        #buscando o nome do ativo na lista de ativos 
         # Fazendo a requisição HT
        resposta = requests.get("https://www.google.com/finance/quote/'{cripto}'-USD?hl=pt&window=6M")
        resposta_br = requests.get("https://www.google.com/finance/quote/'{cripto}'-BRL?hl=pt")
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
    for fiis in lista_fiis:
        #atualizando o indice 
        #buscando o nome do ativo na lista de ativos 
        # Fazendo a requisição HT
        resposta = requests.get("https://www.google.com/finance/quote/'{fiis}':BVMF?hl=pt")
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



def funçao_salario():
    df_outros_gastos = pd.read_excel(Banco_de_Dados21,sheet_name='Extrato')
    df_outros_gastos = df_outros_gastos[(df_outros_gastos['Descrição'] != 'Aporte na carteira Cofrinho')&
                                      (df_outros_gastos['Descrição'] != 'Resgate na carteira Cofrinho')]
    valor_na_conta = sum(df_outros_gastos['Valor'])
    return valor_na_conta
  


def função_custo_mensal():
    #buscando os gastos em dinheiro ou tranferencia 
    df_outros_gastos = pd.read_excel(Banco_de_Dados21,sheet_name='Extrato') 
    df_outros_gastos = df_outros_gastos[df_outros_gastos['Valor']<0]
    # Convertendo a coluna de datas para datetime
    df_outros_gastos['Data'] = pd.to_datetime(df_outros_gastos['Data'], format='%d/%m/%Y', errors='coerce')
    #criando as variaveis com valor zero para não dar erro no final 
    lista_dos_ano = (df_outros_gastos['Data'].dt.year).unique()
    primeira_info = df_outros_gastos['Data'].iloc[0].month
    ultima_info = (df_outros_gastos['Data'].iloc[-1]).month
    # Definindo o mês e ano para o fechamento
    list_dtabertura = ['11/01','11/02','11/03','11/04','11/05','11/06','11/07','11/08','11/09','11/10','11/11','11/12']
    list_fechamento = ['10/02','10/03','10/04','10/05','10/06','10/07','10/08','10/09','10/10','10/11','10/12','10/01']
    df_custo_mensal_final = pd.DataFrame()
    for ano in lista_dos_ano: 
        df_fil_ano = df_outros_gastos[(df_outros_gastos['Data'].dt.year) == int(ano)]
        primeira_info = df_fil_ano['Data'].iloc[0].month
        ultima_info = df_fil_ano['Data'].iloc[-1].month
        for mes in range(primeira_info,ultima_info+2):
            if mes == 1:
                continue
            if mes == 13:
                data_fechamento = datetime.strptime(list_fechamento[int(mes)-2] +'/'+ str(ano+1), '%d/%m/%Y')
            else:
                data_fechamento = datetime.strptime(list_fechamento[int(mes)-2] +'/'+ str(ano), '%d/%m/%Y')
            data_abertura = datetime.strptime(list_dtabertura[int(mes)-2] +'/'+ str(ano), '%d/%m/%Y')
            df_filtrado = df_outros_gastos[(df_outros_gastos['Data'] >= data_abertura) & (df_outros_gastos['Data'] <= data_fechamento)]

            # Agora converte para float, e ignora erros
            df_filtrado["Valor"] = pd.to_numeric(df_filtrado["Valor"], errors="coerce")
            df_filtrado = df_filtrado[(df_filtrado['Descrição'] != 'RECEBIMENTO PIX - 70041500628 Luiz Henrique Normando Sousa')&
                                      (df_filtrado['Descrição'] != 'PAGAMENTO PIX - 70041500628 Luiz Henrique Normando Sousa')&
                                      (df_filtrado['Descrição'] != 'Transferência realizada - TED')&
                                      (df_filtrado['Descrição'] != 'Aporte na carteira Cofrinho')&
                                      (df_filtrado['Descrição'] != 'Resgate na carteira Cofrinho')]
            total = sum(df_filtrado['Valor'])
            cart_xp =(df_filtrado[df_filtrado['Descrição'].str.contains('Pagamento para BANCO XP S/A',case=False,na=False)])
            cart_pc = (df_filtrado[df_filtrado['Descrição'].str.contains('Pagamento de fatura PicPay',case=False,na=False)])
            cart_pc1 = (df_filtrado[df_filtrado['Descrição'].str.contains('Créditos utilizados',case=False,na=False)])
            cart_sic = (df_filtrado[df_filtrado['Descrição'].str.contains('PAGAMENTO DE FATURA CARTAO ',case=False,na=False)])
            cart_luiza = (df_filtrado[df_filtrado['Descrição'].str.contains('PAGAMENTO BOLETO - LUIZA CRED',case=False,na=False)])
            g_mes_cart = sum(cart_pc['Valor'])+sum(cart_pc1['Valor'])+sum(cart_sic['Valor'])+sum(cart_xp['Valor'])+sum(cart_luiza['Valor'])
            

            df_custo_mensal = pd.DataFrame({
                    'DATA':[data_abertura],
                    'MÊS':[data_abertura],
                    'ANO':[data_abertura.year],
                    'CARTÃO':[g_mes_cart],
                    'TOTAL':[total]
                    })
            df_custo_mensal['MÊS'] = pd.to_datetime(df_custo_mensal['MÊS'])
            df_custo_mensal['MÊS'] = df_custo_mensal['MÊS'].dt.month.map(meses_portugues)  
            df_custo_mensal['MÊS'] = df_custo_mensal['MÊS'].astype(str)
            df_custo_mensal['ANO'] = df_custo_mensal['ANO'].astype(str)
            df_custo_mensal['TOTAL'] = df_custo_mensal['TOTAL']* -1
            df_custo_mensal['CARTÃO'] = df_custo_mensal['CARTÃO']* -1
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
    df_outros_gastos = pd.read_excel(Banco_de_Dados21,sheet_name='Extrato')
    df_outros_gastos = df_outros_gastos[df_outros_gastos['Valor']<0]
    df_outros_gastos['Valor'] = df_outros_gastos['Valor']* -1
    # Convertendo a coluna de datas para datetime

    # Agora converte para float, e ignora erros
    df_divisão_gasto = pd.DataFrame()
    df_filtrado = df_outros_gastos[(df_outros_gastos['Descrição'] != 'RECEBIMENTO PIX - 70041500628 Luiz Henrique Normando Sousa')&
                                      (df_outros_gastos['Descrição'] != 'PAGAMENTO PIX - 70041500628 Luiz Henrique Normando Sousa')&
                                      (df_outros_gastos['Descrição'] !='PAGAMENTO PIX - 70041500628 LUIZ HENRIQUE NORMANDO SOUSA')&
                                      (df_outros_gastos['Descrição'] !='Ajuste nos rendimentos')&
                                      (df_outros_gastos['Descrição'] != 'Transferência realizada - TED')&
                                      (df_outros_gastos['Descrição'] != 'Aporte na carteira Cofrinho')&
                                      (df_outros_gastos['Descrição'] != 'Resgate na carteira Cofrinho')]
            
    lista_de_gastos = list(df_filtrado['Descrição'].unique())
    for gasto in lista_de_gastos:
        soma = 0
        df_gasto = df_filtrado[df_filtrado['Descrição'] == gasto]
        soma = sum(df_gasto['Valor'])
        df = pd.DataFrame({'Descrição':[gasto],
                              'Valor':[soma]})
        df_divisão_gasto = pd.concat([df_divisão_gasto,df],axis=0) 
        df_divisão_gasto = df_divisão_gasto.sort_values(by="Valor", ascending=False)      
    return df_divisão_gasto





