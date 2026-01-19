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

def gastos_por_categoria_mes(mes_ano):
    df = pd.read_csv(CSV_FILE)
    if df.empty:
        return pd.DataFrame()

    df["data"] = pd.to_datetime(df["data"])
    df["mes_ano"] = df["data"].dt.to_period("M").astype(str)

    df_mes = df[df["mes_ano"] == mes_ano]

    return (
        df_mes
        .groupby("categoria")["valor"]
        .sum()
        .reset_index()
    )

def total_por_mes(ultimos_meses=12):
    df = pd.read_csv(CSV_FILE)
    if df.empty:
        return pd.DataFrame()

    df["data"] = pd.to_datetime(df["data"])
    df["mes"] = df["data"].dt.to_period("M").astype(str)

    resumo = (
        df.groupby("mes")["valor"]
        .sum()
        .reset_index()
        .sort_values("mes")
        .tail(ultimos_meses)
        .set_index("mes")
    )

    return resumo

def gerar_insights():
    df = pd.read_csv(CSV_FILE)
    if df.empty:
        return []

    df["data"] = pd.to_datetime(df["data"])
    df["mes"] = df["data"].dt.to_period("M").astype(str)

    resumo_mes = (
        df.groupby("mes")["valor"]
        .sum()
        .reset_index()
        .sort_values("mes")
    )

    insights = []

    # Insight 1 - tendência
    if len(resumo_mes) >= 3:
        ultimos = resumo_mes.tail(3)["valor"]
        if ultimos.is_monotonic_increasing:
            insights.append("📈 Seus gastos estão aumentando nos últimos meses.")
        elif ultimos.is_monotonic_decreasing:
            insights.append("📉 Seus gastos estão diminuindo nos últimos meses.")
        else:
            insights.append("➖ Seus gastos estão relativamente estáveis.")

    # Insight 2 - comparação mês atual x anterior
    if len(resumo_mes) >= 2:
        atual = resumo_mes.iloc[-1]["valor"]
        anterior = resumo_mes.iloc[-2]["valor"]

        if anterior > 0:
            variacao = ((atual - anterior) / anterior) * 100
            if variacao > 0:
                insights.append(f"⚠️ Você gastou {variacao:.1f}% a mais que no mês anterior.")
            else:
                insights.append(f"✅ Você gastou {abs(variacao):.1f}% a menos que no mês anterior.")

    # Insight 3 - categoria com maior gasto no mês atual
    mes_atual = resumo_mes.iloc[-1]["mes"]
    df_mes_atual = df[df["mes"] == mes_atual]

    top_categoria = (
        df_mes_atual
        .groupby("categoria")["valor"]
        .sum()
        .idxmax()
    )

    insights.append(f"💸 A categoria que mais pesou este mês foi **{top_categoria}**.")

    # Insight 4 - acima da média
    media = resumo_mes["valor"].mean()
    atual = resumo_mes.iloc[-1]["valor"]

    if atual > media * 1.1:
        insights.append("🚨 Seus gastos deste mês estão bem acima da média.")

    return insights

# =============================
# GERAR ALERTAS AUTOMÁTICOS
# =============================
def gerar_alertas():
    df = pd.read_csv(CSV_FILE)
    if df.empty:
        return []

    df["data"] = pd.to_datetime(df["data"])
    df["mes"] = df["data"].dt.to_period("M").astype(str)

    alertas = []

    resumo_mes = (
        df.groupby("mes")["valor"]
        .sum()
        .reset_index()
        .sort_values("mes")
    )

    if len(resumo_mes) < 2:
        return alertas

    mes_atual = resumo_mes.iloc[-1]
    mes_anterior = resumo_mes.iloc[-2]

    # 🔔 ALERTA 1 — acima da média
    media = resumo_mes["valor"].mean()
    if mes_atual["valor"] > media * 1.2:
        alertas.append(
            "🚨 Atenção: seus gastos deste mês estão **bem acima da média histórica**."
        )

    # 🔔 ALERTA 2 — crescimento brusco
    if mes_anterior["valor"] > 0:
        variacao = ((mes_atual["valor"] - mes_anterior["valor"]) / mes_anterior["valor"]) * 100
        if variacao > 20:
            alertas.append(
                f"📈 Seus gastos aumentaram **{variacao:.1f}%** em relação ao mês passado."
            )

    # 🔔 ALERTA 3 — categoria fora do padrão
    df_cat = (
        df.groupby(["mes", "categoria"])["valor"]
        .sum()
        .reset_index()
    )

    atual_cat = df_cat[df_cat["mes"] == mes_atual["mes"]]

    medias_cat = (
        df_cat.groupby("categoria")["valor"]
        .mean()
    )

    for _, row in atual_cat.iterrows():
        media_categoria = medias_cat.get(row["categoria"], 0)
        if media_categoria > 0 and row["valor"] > media_categoria * 1.5:
            alertas.append(
                f"💣 Gasto elevado em **{row['categoria']}** este mês."
            )

    return alertas


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
