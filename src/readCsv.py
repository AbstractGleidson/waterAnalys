from pathlib import Path
import pandas

def readCSV(arq: str):
    """
    Realiza a leitura de um arquivo csv
    Args:
        arq (str): nome do arquivo

    Returns:
        _type_: Dataframe do arquivo csv
    """
    
    path = Path(__file__).parent.parent / "assets" / "Dados" / arq
    
    return pandas.read_csv(path)
    