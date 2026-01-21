import pandas as pd
import json
import os
from dateutil.relativedelta import relativedelta

CSV_FILE = "gastos.csv"
CONFIG_FILE = "config.json"

def adicionar_gasto(data, descricao, categoria, valor, tipo, cartao=None):
    df = ler_gastos()

    data = pd.to_datetime(data)

    dia_fechamento = None
    if tipo == "Credit" and cartao:
        dia_fechamento = obter_fechamento_cartao(cartao)

    mes_referencia = calcular_mes_referencia(
        data,
        tipo,
        dia_fechamento
    )

    novo_gasto = {
        "data": data.strftime("%Y-%m-%d"),
        "descricao": descricao,
        "categoria": categoria,
        "valor": valor,
        "tipo": tipo,
        "cartao": cartao,
        "mes_referencia": mes_referencia
    }

    df = pd.concat([df, pd.DataFrame([novo_gasto])], ignore_index=True)
    df.to_csv(CSV_FILE, index=False)

def ler_gastos():
    if not os.path.exists(CSV_FILE):
        return pd.DataFrame()

    df = pd.read_csv(CSV_FILE)

    if "mes_referencia" not in df.columns:
        df["data"] = pd.to_datetime(df["data"])
        df["mes_referencia"] = df["data"].dt.to_period("M").astype(str)

    return df

def listar_meses_disponiveis():
    df = pd.read_csv(CSV_FILE)
    if df.empty:
        return []

    df["data"] = pd.to_datetime(df["data"])
    df["mes_ano"] = df["data"].dt.to_period("M").astype(str)

    meses = sorted(df["mes_ano"].unique(), reverse=True)
    return meses

def resumo_por_mes(mes_referencia):
    df = ler_gastos()
    if df.empty:
        return 0, pd.DataFrame()

    df_mes = df[df["mes_referencia"] == mes_referencia]

    total = df_mes["valor"].sum()
    por_categoria = (
        df_mes.groupby("categoria")["valor"]
        .sum()
        .reset_index()
    )

    return total, por_categoria

def comparar_meses(mes_base, mes_comparacao):
    df = pd.read_csv(CSV_FILE)
    if df.empty:
        return pd.DataFrame()

    df["data"] = pd.to_datetime(df["data"])
    df["mes_ano"] = df["data"].dt.to_period("M").astype(str)

    df_filtrado = df[df["mes_ano"].isin([mes_base, mes_comparacao])]

    comparacao = (
        df_filtrado
        .groupby(["mes_ano", "categoria"])["valor"]
        .sum()
        .reset_index()
        .pivot(index="categoria", columns="mes_ano", values="valor")
        .fillna(0)
    )

    comparacao["Diferença"] = (
        comparacao[mes_comparacao] - comparacao[mes_base]
    )

    return comparacao.reset_index()

def gastos_por_categoria_mes(mes_referencia):
    df = ler_gastos()
    if df.empty:
        return pd.Series(dtype=float)

    df_mes = df[df["mes_referencia"] == mes_referencia]

    return (
        df_mes.groupby("categoria")["valor"]
        .sum()
        .sort_values(ascending=False)
    )

def total_por_mes():
    df = ler_gastos()
    if df.empty:
        return pd.Series(dtype=float)

    return (
        df.groupby("mes_referencia")["valor"]
        .sum()
        .sort_index()
    )

def gerar_insights(mes_referencia):
    df = ler_gastos()
    if df.empty:
        return []

    df_mes = df[df["mes_referencia"] == mes_referencia]
    insights = []

    por_categoria = (
        df_mes.groupby("categoria")["valor"]
        .sum()
        .sort_values(ascending=False)
    )

    if not por_categoria.empty:
        cat = por_categoria.index[0]
        val = por_categoria.iloc[0]
        insights.append(
            f"💡 Sua maior despesa nesta fatura foi **{cat}** (${val:.2f})"
        )

    return insights

# =============================
# GERAR ALERTAS AUTOMÁTICOS
# =============================
def gerar_alertas(mes_referencia, teto):
    alertas = []

    estourou, total = verificar_teto(mes_referencia, teto)

    if estourou:
        alertas.append(
            f"🚨 Você ultrapassou o teto da fatura ({total:.2f})"
        )
    elif total >= teto * 0.8:
        alertas.append(
            f"⚠️ Atenção: você já usou 80% do teto da fatura"
        )

    return alertas


# =============================
# GERENCIAR TETO MENSAL
# =============================
def ler_teto():
    if not os.path.exists(CONFIG_FILE):
        return 0

    with open(CONFIG_FILE, "r") as f:
        data = json.load(f)

    return data.get("teto_mensal", 0)

def salvar_teto(valor):
    with open(CONFIG_FILE, "w") as f:
        json.dump({"teto_mensal": valor}, f)

def verificar_teto(mes_referencia, teto):
    df = ler_gastos()
    if df.empty:
        return False, 0

    total = df[df["mes_referencia"] == mes_referencia]["valor"].sum()

    return total >= teto, total


# =============================
# GERENCIAR PROGRESSO TETO
# =============================
def progresso_teto():
    teto = ler_teto()
    if teto <= 0:
        return None

    df = pd.read_csv(CSV_FILE)
    if df.empty:
        return None

    df["data"] = pd.to_datetime(df["data"])
    df["mes"] = df["data"].dt.to_period("M").astype(str)

    mes_atual = df["mes"].max()
    gasto_atual = df[df["mes"] == mes_atual]["valor"].sum()

    percentual = min(gasto_atual / teto, 1)

    return {
        "gasto": gasto_atual,
        "teto": teto,
        "percentual": percentual
    }

# =============================
# VERIFICAR OBJETIVO DE GASTOS
# =============================
def verificar_objetivo():
    df = pd.read_csv(CSV_FILE)
    if df.empty:
        return None

    df["data"] = pd.to_datetime(df["data"])
    df["mes"] = df["data"].dt.to_period("M").astype(str)

    resumo = (
        df.groupby("mes")["valor"]
        .sum()
        .reset_index()
        .sort_values("mes")
    )

    if len(resumo) < 2:
        return None

    atual = resumo.iloc[-1]
    anterior = resumo.iloc[-2]

    diferenca = atual["valor"] - anterior["valor"]

    if diferenca < 0:
        return f"🎯 Parabéns! Você gastou **R$ {abs(diferenca):.2f} a menos** que no mês passado."
    else:
        return f"⚠️ Você está gastando **R$ {diferenca:.2f} a mais** que no mês passado."

# =============================
# CALCULAR MÊS DE REFERÊNCIA
# =============================
def calcular_mes_referencia(data, tipo, dia_fechamento=None):
    if tipo == "Crédito" and dia_fechamento:
        if data.day > dia_fechamento:
            data_ref = data + relativedelta(months=1)
        else:
            data_ref = data
    else:
        data_ref = data

    return data_ref.strftime("%Y-%m")

# =============================
# OBTER FECHAMENTO DO CARTÃO
# =============================
def obter_fechamento_cartao(nome_cartao):
    df = pd.read_csv("cartoes.csv")
    linha = df[df["cartao"] == nome_cartao]
    if linha.empty:
        return None
    return int(linha.iloc[0]["fechamento"])


'''
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
'''