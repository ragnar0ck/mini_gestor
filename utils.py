import pandas as pd

CSV_FILE = "gastos.csv"

def adicionar_gasto(data, descricao, categoria, tipo, valor):
    df = pd.read_csv(CSV_FILE)
    novo = pd.DataFrame([[data, descricao, categoria, tipo, valor]],
                        columns=["data","descricao","categoria","tipo","valor"])
    df = pd.concat([df, novo], ignore_index=True)
    df.to_csv(CSV_FILE, index=False)

def ler_gastos():
    df = pd.read_csv(CSV_FILE)
    return df
