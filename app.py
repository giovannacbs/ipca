from flask import Flask, request, render_template
import requests

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')

@app.route("/ipca.html", methods=["GET", "POST"])
def ipca():
    if request.method == "POST":
        periodicidade = request.form.get('periodicidade')
        classificacao = request.form.get('classificacao')
    else:
        periodicidade = request.args.get('periodicidade')
        classificacao = request.args.get('classificacao')

    result_ipca = calc_ipca(periodicidade, classificacao)
    if result_ipca is None:
        return "Erro ao calcular IPCA"

    if periodicidade == '15':
        per = 'prévia da'
    else:
        per = ''

    yy = result_ipca['infl_yy']
    yy_txt = f"{float(yy):,.2f}".replace(",", "TEMP").replace(".", ",").replace("TEMP", ".")
    mm = result_ipca['infl_mm']
    mm_txt = f"{float(mm):,.2f}".replace(",", "TEMP").replace(".", ",").replace("TEMP", ".")
    menor_valor = result_ipca['menor_cont']
    menor_valor_txt = f"{float(menor_valor):,.2f}".replace(",", "TEMP").replace(".", ",").replace("TEMP", ".")
    maior_valor = result_ipca['maior_cont']
    maior_valor_txt = f"{float(maior_valor):,.2f}".replace(",", "TEMP").replace(".", ",").replace("TEMP", ".")
    maior_grupo = result_ipca['maior_grupo'].lower()
    menor_grupo = result_ipca['menor_grupo'].lower()
    data = result_ipca['data_result']
    classificacao = result_ipca['classificacao']

    if menor_valor >= 0:
        txt_menor = 'menor contribuição'
    else:
        txt_menor = 'maior contribuição negativa'

    return render_template('ipca.html', menor_valor=menor_valor,
                           menor_valor_txt=menor_valor_txt,
                           maior_valor=maior_valor,
                           maior_valor_txt=maior_valor_txt,
                           maior_grupo=maior_grupo,
                           menor_grupo=menor_grupo,
                           yy=yy,
                           yy_txt=yy_txt,
                           mm=mm,
                           mm_txt=mm_txt,
                           data=data,
                           per=per,
                           classificacao=classificacao,
                           txt_menor=txt_menor)

def calc_ipca(periodicidade, classificacao):
    if periodicidade == "mensal":
        tabela = "7060"
        variaveis = "63|66|2265"
    elif periodicidade == "15":
        tabela = "7062"
        variaveis = "355|357|1120"
    else:
        print("Erro")
        return None

    url = f"https://servicodados.ibge.gov.br/api/v3/agregados/{tabela}/periodos/-1/variaveis/{variaveis}?localidades=N1[all]&classificacao=315[7169]"
    r = requests.get(url).json()

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

    if classificacao == "grupo":
        parametro = "7169,7170,7445,7486,7558,7625,7660,7712,7766,7786"
        nome_par = 2
    elif classificacao == "subgrupo":
        parametro = "7169,7171,7432,7446,7479,7487,7521,7548,7559,7604,7615,7620,7626,7661,7683,7697,7713,7767,7787"
        nome_par = 3

    url = f"https://servicodados.ibge.gov.br/api/v3/agregados/{tabela}/periodos/-1/variaveis/{variaveis}?localidades=N1[all]&classificacao=315[{parametro}]"
    r = requests.get(url).json()

    dic = {}

    for x in range(len(r[0]["resultados"]) - 1):
        grupo = (list((r[0]["resultados"][x + 1]["classificacoes"][0]["categoria"]).values())[0])[nome_par:]
        mm = float(list((r[0]["resultados"][x + 1]["series"][0]["serie"]).values())[0])
        peso = float(list((r[1]["resultados"][x + 1]["series"][0]["serie"]).values())[0])
        cont = (peso / 100) * mm
        dic[cont] = grupo

    maior_cont = sorted(dic, reverse=True)[0]
    menor_cont = sorted(dic, reverse=False)[0]
    maior_grupo = dic[maior_cont]
    menor_grupo = dic[menor_cont]

    return {
        "maior_cont": maior_cont,
        "menor_cont": menor_cont,
        "maior_grupo": maior_grupo,
        "menor_grupo": menor_grupo,
        "infl_mm": infl_mm,
        "infl_yy": infl_yy,
        "data_result": data_result,
        "classificacao": classificacao
    }

if __name__ == '__main__':
    app.run(debug=True)
