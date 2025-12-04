def limpar_lote(lote):
    """
    Limpa os lotes do dataframe, tirando espaços e caracteres "estranhos"
    Args:
        lote (_type_): lote que deve ser limpo

    Returns:
        _type_: Retorna o lote limpo
    """
    
    lote = str(lote).strip()
    lote = lote.replace(" ", "").replace("-", "").replace(".", "").replace("/", "")

    letras = ''.join([c for c in lote if c.isalpha()])
    numeros = ''.join([c for c in lote if c.isdigit()])

    if letras == "" or numeros == "":
        return lote.upper()

    return f"{letras.upper()}{numeros.zfill(2)}"