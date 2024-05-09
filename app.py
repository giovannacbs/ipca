from flask import Flask, request, render_template
import numpy as np

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')


@app.route("/ipca.html", methods=["GET"])
def ipca():
    periodicidade = request.args.get('periodicidade')
    classificacao = request.args.get('classificacao')
    
    result_ipca = calc_ipca(periodicidade, classificacao)

    return render_template('ipca.html', result_ipca = result_ipca)


def calc_ipca(periodicidade, classificacao):

  if periodicidade.lower() == "mensal":
    tabela = "7060"
    variaveis = "63|66|2265"
  elif periodicidade.lower() == "15":
    tabela = "7062"
    variaveis = "355|357|1120"
  else: 
    print("Erro")
    return None
        
  url = f"https://servicodados.ibge.gov.br/api/v3/agregados/{tabela}/periodos/-1/variaveis/{variaveis}?localidades=N1[all]&classificacao=315[7169]"
  r = requests.get(url, verify=False).json()

  infl_mm = float(list((r[0]["resultados"][0]["series"][0]["serie"]).values())[0])
  infl_yy = float(list((r[2]["resultados"][0]["series"][0]["serie"]).values())[0])
    
  data = list(r[0]["resultados"][0]["series"][0]["serie"].items())[0][0]
  mes = data[4:]
  ano = data[:4]
    
  meses = {
          "01": "janeiro",
          "02": "fevereiro",
          "03": "março",
          "04": "abril",
          "05": "maio",
          "06": "junho",
          "07": "julho",
          "08": "agosto",
          "09": "setembro",
          "10": "outubro",
          "11": "novembro",
          "12": "dezembro"
          }
    
  data_result = f"{(meses[mes]).title()}/{ano}"
    
  #print(f"{(meses[mes]).title()}/{ano}:\n{infl_mm}% m/m \n{infl_yy}% a/a")
    
  if classificacao == "grupo":
      parametro = "7169,7170,7445,7486,7558,7625,7660,7712,7766,7786"
      nome_par = 2
  elif classificacao == "subgrupo":
      parametro = "7169,7171,7432,7446,7479,7487,7521,7548,7559,7604,7615,7620,7626,7661,7683,7697,7713,7767,7787"
      nome_par = 3   
  
  url = f"https://servicodados.ibge.gov.br/api/v3/agregados/{tabela}/periodos/-1/variaveis/{variaveis}?localidades=N1[all]&classificacao=315[{parametro}]"
  r = requests.get(url, verify=False).json()

  dic = {}
        
  for x in range(len(r[0]["resultados"])-1):
      # nomes dos grupo    
      grupo = (list((r[0]["resultados"][x+1]["classificacoes"][0]["categoria"]).values())[0])[nome_par:]
      # print(grupo)
      # variacao mensal
      mm = float(list((r[0]["resultados"][x+1]["series"][0]["serie"]).values())[0])
      # print(mm)
      # peso
      peso = float(list((r[1]["resultados"][x+1]["series"][0]["serie"]).values())[0])
      # print(peso)
      # contribuicao em pontos percentuais
      cont = (peso/100)*mm
      # print(cont)
      # criando dicionários com contribuicoes
      dic[cont] = grupo
        
  maior_cont = sorted(dic, reverse=True)[0]
  menor_cont = sorted(dic, reverse=False)[0]
  maior_grupo = dic[maior_cont]
  menor_grupo = dic[menor_cont]
        
  #print("------")
  #print(f"Maior contribuição positiva de {classificacao}: {maior_grupo.lower()} ({round(maior_cont, 2)} pp.)")
  #print(f"Menor contribuição negativa de {classificacao}: {menor_grupo.lower()} ({round(menor_cont, 2)} pp.)")

  return {
        "maior_cont": maior_cont,
        "menor_cont": menor_cont,
        "maior_grupo": maior_grupo,
        "menor_grupo": menor_grupo,
        "infl_mm": infl_mm,
        "infl_yy": infl_yy,
        "data_result": data_result
    }