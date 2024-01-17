# Ler todas as cotações e recomendações das ações da B3 e grava as informações em arquivos csv

from tradingview_ta import TA_Handler, Interval, Exchange
from tradingview_ta import *
import requests
import numpy
import csv
import json
import pandas as pd

url_si = 'https://statusinvest.com.br/category/advancedsearchresult?search=%7B%22Sector%22%3A%22%22%2C%22SubSector%22%3A%22%22%2C%22Segment%22%3A%22%22%2C%22my_range%22%3A%220%3B25%22%2C%22dy%22%3A%7B%22Item1%22%3Anull%2C%22Item2%22%3Anull%7D%2C%22p_L%22%3A%7B%22Item1%22%3Anull%2C%22Item2%22%3Anull%7D%2C%22p_VP%22%3A%7B%22Item1%22%3Anull%2C%22Item2%22%3Anull%7D%2C%22p_Ativo%22%3A%7B%22Item1%22%3Anull%2C%22Item2%22%3Anull%7D%2C%22margemBruta%22%3A%7B%22Item1%22%3Anull%2C%22Item2%22%3Anull%7D%2C%22margemEbit%22%3A%7B%22Item1%22%3Anull%2C%22Item2%22%3Anull%7D%2C%22margemLiquida%22%3A%7B%22Item1%22%3Anull%2C%22Item2%22%3Anull%7D%2C%22p_Ebit%22%3A%7B%22Item1%22%3Anull%2C%22Item2%22%3Anull%7D%2C%22eV_Ebit%22%3A%7B%22Item1%22%3Anull%2C%22Item2%22%3Anull%7D%2C%22dividaLiquidaEbit%22%3A%7B%22Item1%22%3Anull%2C%22Item2%22%3Anull%7D%2C%22dividaliquidaPatrimonioLiquido%22%3A%7B%22Item1%22%3Anull%2C%22Item2%22%3Anull%7D%2C%22p_SR%22%3A%7B%22Item1%22%3Anull%2C%22Item2%22%3Anull%7D%2C%22p_CapitalGiro%22%3A%7B%22Item1%22%3Anull%2C%22Item2%22%3Anull%7D%2C%22p_AtivoCirculante%22%3A%7B%22Item1%22%3Anull%2C%22Item2%22%3Anull%7D%2C%22roe%22%3A%7B%22Item1%22%3Anull%2C%22Item2%22%3Anull%7D%2C%22roic%22%3A%7B%22Item1%22%3Anull%2C%22Item2%22%3Anull%7D%2C%22roa%22%3A%7B%22Item1%22%3Anull%2C%22Item2%22%3Anull%7D%2C%22liquidezCorrente%22%3A%7B%22Item1%22%3Anull%2C%22Item2%22%3Anull%7D%2C%22pl_Ativo%22%3A%7B%22Item1%22%3Anull%2C%22Item2%22%3Anull%7D%2C%22passivo_Ativo%22%3A%7B%22Item1%22%3Anull%2C%22Item2%22%3Anull%7D%2C%22giroAtivos%22%3A%7B%22Item1%22%3Anull%2C%22Item2%22%3Anull%7D%2C%22receitas_Cagr5%22%3A%7B%22Item1%22%3Anull%2C%22Item2%22%3Anull%7D%2C%22lucros_Cagr5%22%3A%7B%22Item1%22%3Anull%2C%22Item2%22%3Anull%7D%2C%22liquidezMediaDiaria%22%3A%7B%22Item1%22%3Anull%2C%22Item2%22%3Anull%7D%7D&CategoryType=1'
headers_si = { 'accept': '*/*',
      'accept-language': 'en-US,en;q=0.9,pt-BR;q=0.8,pt;q=0.7,es-MX;q=0.6,es;q=0.5',
      'content-type': 'application/x-www-form-urlencoded; charset=UTF-8',
      'x-requested-with': 'XMLHttpRequest',
      'sec-ch-ua': '" Not;A Brand";v="99", "Google Chrome";v="97", "Chromium";v="97"',
      'sec-ch-ua-mobile': '?0',
      'sec-ch-ua-platform': '"macOS"',
      'sec-fetch-dest': 'empty',
      'sec-fetch-mode': 'cors',
      'sec-fetch-site': 'same-origin',
      'user-agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko)'}

session_requests = requests.session()
response = requests.get(url_si, headers = headers_si)
response.raise_for_status()  # raises exception when not a 2xx response
response_json = response.json()

df = pd.DataFrame(response_json)

# excluir as ações não relevantes
newdf = df[(df.p_vp < 200) & (df.dy < 100) & (df.dy > 0) & (df.p_l < 15) & (df.p_l > 0)]

# classifica em ordem decrescente por DY
newdf.sort_values(by=['dy'], inplace=True, ascending=False)

recomendacao_asset = '['
with open('Recomendacoes.csv', 'w') as testfile:

  # pass the the temporary variable to csv.writer function
  csvwriter = csv.writer(testfile,)
  csvwriter.writerow(['ticker','recomendação','buy','sell','neutral'])

  # monta lista de ativos para ler recomendacoes
  for asset in newdf['ticker']:
    # le recomendacoes de compra e venda
    ticker = TA_Handler(symbol=asset, screener="brazil", exchange="BMFBOVESPA",
      interval=Interval.INTERVAL_1_DAY)

    if recomendacao_asset != '[': # verifica se tem mais de um ticker
      recomendacao_asset = recomendacao_asset + ','
      recomendacao_asset = recomendacao_asset + '{"ticker": "'+asset+'", \
      "recomendação": "'+recomendacao['RECOMMENDATION']+'", "buy": "' + \
      str(recomendacao['BUY'])+'", "sell": "'+str(recomendacao['SELL'])+ \
      '", "neutral": "'+ str(recomendacao['NEUTRAL'])+'"}'
    try:
      recomendacao = ticker.get_analysis().summary
      csvwriter.writerow([asset, recomendacao['RECOMMENDATION'],
        recomendacao['BUY'], recomendacao['SELL'], recomendacao['NEUTRAL']])

    except:
      next # houve algum erro e a recomendação não veio

  recomendacao_asset = recomendacao_asset + ']'
  recomendacao_json = json.loads(recomendacao_asset)
  recomendacao_df = pd.DataFrame(recomendacao_json)
  newdf.to_csv('Cotacoes.csv', index=False)

# recomendacoes para carteira hipotética
newdf = ['AESB3','AURE3','B3SA3','BBAS3','BBDC4','BBSE3','BRAP4','CPLE6','CSMG3','EGIE3','EZTC3','GOAU4','ITSA4','ITUB4','KLBN4','LREN3','MGLU3','PETR4','SAPR11','TAEE11','TIMS3','TRPL4','USIM5','VALE3','VIVT3']

recomendacao_asset = '['
with open('Recomendacoes_Carteira.csv', 'w') as testfile:

  # pass the the temporary variable to csv.writer function
  csvwriter = csv.writer(testfile,)
  csvwriter.writerow(['ticker','recomendação','buy','sell','neutral'])

  # monta lista de ativos para ler recomendacoes
  for asset in newdf:
    # le recomendacoes de compra e venda
    ticker = TA_Handler(symbol=asset, screener="brazil", exchange="BMFBOVESPA",
      interval=Interval.INTERVAL_1_DAY)

    if recomendacao_asset != '[': # verifica se tem mais de um ticker
      recomendacao_asset = recomendacao_asset + ','
      recomendacao_asset = recomendacao_asset + '{"ticker": "'+asset+'", \
      "recomendação": "'+recomendacao['RECOMMENDATION']+'", "buy": "' + \
      str(recomendacao['BUY'])+'", "sell": "'+str(recomendacao['SELL'])+ \
      '", "neutral": "'+ str(recomendacao['NEUTRAL'])+'"}'
    try:
      recomendacao = ticker.get_analysis().summary
      csvwriter.writerow([asset, recomendacao['RECOMMENDATION'],
        recomendacao['BUY'], recomendacao['SELL'], recomendacao['NEUTRAL']])

    except:
      next # houve algum erro e a recomendação não veio

  recomendacao_asset = recomendacao_asset + ']'
  recomendacao_json = json.loads(recomendacao_asset)
  recomendacao_df = pd.DataFrame(recomendacao_json)
