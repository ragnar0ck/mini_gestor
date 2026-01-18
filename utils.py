import pandas as pd

CSV_FILE = "gastos.csv"

def adicionar_gasto(data, descricao, categoria, tipo, valor):
    df = pd.read_csv(CSV_FILE)
    novo = pd.DataFrame([[data, descricao, categoria, tipo, valor]],
                        columns=["data","descricao","categoria","tipo","valor"])
    df = pd.concat([df, novo], ignore_index=True)
    df.to_csv(CSV_FILE, index=False)

def ler_gastos():
    return pd.read_csv(CSV_FILE)

def listar_meses_disponiveis():
    df = pd.read_csv(CSV_FILE)
    if df.empty:
        return []

    df["data"] = pd.to_datetime(df["data"])
    df["mes_ano"] = df["data"].dt.to_period("M").astype(str)

    meses = sorted(df["mes_ano"].unique(), reverse=True)
    return meses


def resumo_por_mes(mes_ano):
    df = pd.read_csv(CSV_FILE)
    if df.empty:
        return 0, pd.DataFrame()

    df["data"] = pd.to_datetime(df["data"])
    df["mes_ano"] = df["data"].dt.to_period("M").astype(str)

    df_mes = df[df["mes_ano"] == mes_ano]

    total = df_mes["valor"].sum()
    por_categoria = df_mes.groupby("categoria")["valor"].sum().reset_index()

    return total, por_categoria

    df = pd.read_csv(CSV_FILE)
    if df.empty:
        return 0, pd.DataFrame()

    df["data"] = pd.to_datetime(df["data"])
    mes_atual = pd.Timestamp.now().month
    ano_atual = pd.Timestamp.now().year

    df_mes = df[
        (df["data"].dt.month == mes_atual) &
        (df["data"].dt.year == ano_atual)
    ]

    total = df_mes["valor"].sum()
    por_categoria = df_mes.groupby("categoria")["valor"].sum().reset_index()

    return total, por_categoria
