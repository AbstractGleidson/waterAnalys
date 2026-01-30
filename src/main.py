import pandas
import matplotlib.pyplot as plt
from pathlib import Path
from limpa_lote import limpar_lote
from readCsv import readCSV
from leituras_duplicadas import limpar_leitura_duplicada


if __name__ == "__main__":
    
    # realizando a leitura dos data frame
    moradores = readCSV("Moradores.csv")
    leit_set = readCSV("leitura_setembro.csv")
    leit_out = readCSV("leitura_outubro.csv")

    # Remover espaços extras nos nomes das colunas
    moradores.columns = moradores.columns.str.strip()
    leit_set.columns = leit_set.columns.str.strip()
    leit_out.columns = leit_out.columns.str.strip()

    # Limpeza do campo Lote
    moradores["Lote"] = moradores["Lote"].apply(limpar_lote)
    leit_set["Lote"] = leit_set["Lote"].apply(limpar_lote)
    leit_out["Lote"] = leit_out["Lote"].apply(limpar_lote)

    # Garantir valores numéricos para a leitura do consumo
    leit_set["Leitura"] = pandas.to_numeric(leit_set["Leitura"], errors="coerce")
    leit_out["Leitura"] = pandas.to_numeric(leit_out["Leitura"], errors="coerce")

    # Renomeia as colunas
    leit_set = leit_set.rename(columns={"Leitura": "Leitura_Setembro"})
    leit_out = leit_out.rename(columns={"Leitura": "Leitura_Outubro"})

    # Combina  os dataframes
    dataframe = moradores.copy()
    dataframe = dataframe.merge(leit_set, on="Lote", how="left")
    dataframe = dataframe.merge(leit_out, on="Lote", how="left")

    # Coluna extra para o consumo e status
    dataframe["consumo_bruto"] = 0
    dataframe["status"] = ""
    
    # Tira leituras duplicadas colocando o valor da leitura como 0 alterando o status para "leitura invalida"
    limpar_leitura_duplicada(dataframe, "Leitura_Setembro")
    limpar_leitura_duplicada(dataframe, "Leitura_Outubro")
    
    # Remove leituras duplicadas
    dataframe = dataframe.drop_duplicates(subset=["Lote"], keep="first")
    
    # Localiza leitura negativas
    negativo_set = dataframe["Leitura_Setembro"] < 0
    negativo_out = dataframe["Leitura_Outubro"] < 0

    # Aplicar status "Leitura inválida" para qualquer leitura negativa
    dataframe.loc[negativo_set | negativo_out, "status"] = "Leitura inválida"

    # Zerar apenas as leituras negativas
    # dataframe.loc[negativo_set, "Leitura_Setembro"] = 0
    # dataframe.loc[negativo_out, "Leitura_Outubro"] = 0
    
    # pega os valores NaN e coloca 0 e classifica como leitura invalida
    elementos_nan = dataframe["Leitura_Outubro"].isna()
    dataframe["Leitura_Outubro"] = dataframe["Leitura_Outubro"].fillna(0).astype(int) # Transformar NaN em 0
    dataframe.loc[elementos_nan, "status"] = "Leitura inválida" # Alterar status apenas para os que eram NaN
     
    # Ordena pelo lote
    dataframe = dataframe.sort_values(by="Lote")

    #Calcula o consumo bruto
    dataframe["consumo_bruto"] = dataframe["Leitura_Outubro"] - dataframe["Leitura_Setembro"]

    #Atribue o status Consumo Negativo 
    dataframe.loc[(dataframe["consumo_bruto"] < 0) & (dataframe["status"].str.strip().str.lower() != "leitura inválida"), "status"] = "Consumo negativo"
    
    #Atribue o status Consumo Excessivo
    dataframe.loc[dataframe["consumo_bruto"] > 500, "status"] = "Consumo Excessivo"

    #Atribue o status OK para as linhas que não são anomalias/inválidas
    dataframe.loc[dataframe["status"].str.strip().str.lower() == "", "status"] = "OK"

    #Atribue 0 aos consumos negativos e leituras inválidas
    dataframe.loc[dataframe["status"].str.strip().str.lower() == "consumo negativo", "Leitura_Outubro"] = 0
    dataframe.loc[dataframe["status"].str.strip().str.lower() == "leitura inválida", "Leitura_Outubro"] = 0

    #Ordena em ordem decrescente pelo consumo bruto
    dataframe = dataframe.sort_values(by="consumo_bruto", ascending=False)

    #Separa apenas os consumos válidos
    validos = dataframe[dataframe["status"] == "OK"] .sort_values(by="consumo_bruto", ascending=False)

    #Ordena os tops 10 validos e inválidos
    top10validos = validos .head(10)
    top10invalidos = dataframe[dataframe["status"] != "OK"] .sort_values(by="consumo_bruto", ascending=False) .head(10)


    # Armazena as informações a respeito dos lotes, separados nas seguintes faixas
    # 0 = 0 - 50
    # 1 = 51 - 100
    # 2 = 101 - 150
    # 3 = 151 - 200
    # 4 = 201 - 300
    # 5 = 300 - +

    quantidade = [None] * 6
    consumo_total = [None] * 6

    #Quantidade de elementos de cada faixa 
    quantidade[0] = len(validos.loc[(validos["consumo_bruto"] >= 0) & (validos["consumo_bruto"] <= 50), "consumo_bruto"])
    quantidade[1] = len(validos.loc[(validos["consumo_bruto"] >= 51) & (validos["consumo_bruto"] <= 100), "consumo_bruto"])
    quantidade[2] = len(validos.loc[(validos["consumo_bruto"] >= 101) & (validos["consumo_bruto"] <= 150), "consumo_bruto"])
    quantidade[3] = len(validos.loc[(validos["consumo_bruto"] >= 151) & (validos["consumo_bruto"] <= 200), "consumo_bruto"])
    quantidade[4] = len(validos.loc[(validos["consumo_bruto"] >= 201) & (validos["consumo_bruto"] <= 300), "consumo_bruto"])
    quantidade[5] = len(validos.loc[validos["consumo_bruto"] >= 301, "consumo_bruto"])

    #consumo de cada faixa 
    consumo_total[0] = validos.loc[(validos["consumo_bruto"] >= 0) & (validos["consumo_bruto"] <= 50), "consumo_bruto"] .sum()
    consumo_total[1] = validos.loc[(validos["consumo_bruto"] >= 51) & (validos["consumo_bruto"] <= 100), "consumo_bruto"] .sum()
    consumo_total[2] = validos.loc[(validos["consumo_bruto"] >= 101) & (validos["consumo_bruto"] <= 150), "consumo_bruto"] .sum()
    consumo_total[3] = validos.loc[(validos["consumo_bruto"] >= 151) & (validos["consumo_bruto"] <= 200), "consumo_bruto"] .sum()
    consumo_total[4] = validos.loc[(validos["consumo_bruto"] >= 201) & (validos["consumo_bruto"] <= 300), "consumo_bruto"] .sum()
    consumo_total[5] = validos.loc[validos["consumo_bruto"] >= 301, "consumo_bruto"] .sum()
    

    #Geração de gráficos 
    labels = ["300+", "201 - 300", "151 - 200", "101 - 150", "0 - 50"]
    quant = quantidade[::-1]
    
    # Calcula as porcentagens
    total = len(validos)
    percentuais = [(v / total) * 100 for v in quant]

    # Monta os textos para a legenda
    legendas = [f"{l} — {q} — {p:.1f}%" for l, q, p in zip(labels, quant, percentuais)]

    # Criar figura pequena
    fig, ax = plt.subplots(figsize=(5, 5))  # 🔹 ajuste aqui para deixar maior/menor

    # 🔹 shrink - deixa o círculo menor dentro da figura
    ax.pie(quant, radius=1.0, startangle=90)  # quanto menor o radius, menor o círculo

    plt.title('Quantidade de lotes por faixa de consumo', loc="center")
    plt.text(0.5, 0, f"Total: {total}", ha="center", va="center", transform=ax.transAxes)

    # 🔹 legenda embaixo
    ax.legend(
        legendas,
        loc="upper center",
        bbox_to_anchor=(0.5, -0.15),  # empurra para baixo
        ncol=1                         # 1 coluna (pode mudar)
    )

    plt.tight_layout()
    plt.savefig("Quantidade.png", dpi=300, bbox_inches="tight")

    # Gera um csv do dataframe
    # dataframe.to_csv("limpo.csv", index=False, encoding="utf-8-sig")
   