import pandas as pd

CSV_FILE = "gastos.csv"

def adicionar_gasto(data, descricao, categoria, tipo, valor):
    df = pd.read_csv(CSV_FILE)
    novo = pd.DataFrame(
        [[data, descricao, categoria, tipo, valor]],
        columns=["data", "descricao", "categoria", "tipo", "valor"]
    )
    df = pd.concat([df, novo], ignore_index=True)
    df.to_csv(CSV_FILE, index=False)

def ler_gastos():
    return pd.read_csv(CSV_FILE)

def resumo_total(df):
    return df["valor"].sum()

def gastos_por_categoria(df):
    return (
        df.groupby("categoria")["valor"]
        .sum()
        .sort_values(ascending=False)
    )

def gastos_por_tipo(df):
    return (
        df.groupby("tipo")["valor"]
        .sum()
    )
