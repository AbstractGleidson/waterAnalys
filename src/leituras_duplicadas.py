def limpar_leitura_duplicada(dataframe, coluna):
    """
    Tira leituras duplicadas colocando o valor da leitura como 0 alterando o status para "leitura invalida"
    """
    
    # Identificar lotes com leituras diferentes
    grupo = dataframe.groupby("Lote")[coluna]

    # Lotes com 2 ou mais valores diferentes
    duplicado = grupo.nunique()
    duplicado = duplicado[duplicado > 1].index

    # Zerar leitura dos lotes problemáticos
    dataframe.loc[dataframe["Lote"].isin(duplicado), coluna] = 0

    # Marcar status como leitura inválida 
    dataframe.loc[dataframe["Lote"].isin(duplicado), "status"] = "Leitura inválida"