import streamlit as st
from utils import (
    adicionar_gasto,
    ler_gastos,
    listar_meses_disponiveis,
    resumo_por_mes,
    gastos_por_categoria_mes,
    total_por_mes,
    gerar_insights,
    gerar_alertas,
    salvar_teto,
    ler_teto,
    verificar_teto,
    progresso_teto,
    verificar_objetivo,
    gerar_despesas_fixas_mes_atual,
)

# =============================

st.set_page_config(page_title="Mini Gestor Financeiro Familiar", layout="centered")

# =============================
# CATEGORIAS (FORA DO FORM)
# =============================
CATEGORIAS_PADRAO = [
    "Mercado",
    "Alimentação",
    "Moradia",
    "Transporte",
    "Lazer",
    "Saúde",
    "Educação",
    "Outros"
]

# =============================
# SIDEBAR MENU
# =============================
st.sidebar.title("📊 Mini Gestor")
menu = st.sidebar.radio(
    "Navegação",
    [
        "➕ Registrar gasto",
        "📌 Visão geral",
        "📈 Histórico",
        "🧠 Insights & alertas",
        "⚙️ Configurações"
    ]
)

if menu == "➕ Registrar gasto":
    st.title("Novo gasto")
    # 👉 código do formulário aqui
    st.subheader("Novo gasto")

    categoria_selecionada = st.selectbox(
        "Categoria", CATEGORIAS_PADRAO
    )

    if categoria_selecionada == "Outros":
        categoria_final = st.text_input("Digite a categoria")
    else:
        categoria_final = categoria_selecionada

    st.divider()

# =============================
# FORMULÁRIO (ENVIO)
# =============================
    with st.form("form_gasto"):
        data = st.date_input("Data")
        descricao = st.text_input("Descrição")

        tipo = st.selectbox(
            "Tipo de pagamento",
            ["Débito", "Crédito", "Dinheiro"]
        )

        valor = st.number_input(
            "Valor",
            min_value=0.0,
            format="%.2f"
        )

        fixo = st.checkbox("Despesa fixa (repete mensalmente)")

        submitted = st.form_submit_button("Adicionar gasto")

        if submitted:
            if not categoria_final:
                st.warning("Informe a categoria do gasto.")
            elif valor <= 0:
                st.warning("Informe um valor maior que zero.")
            else:
                adicionar_gasto(
                    data=data,
                    descricao=descricao,
                    categoria=categoria_final,
                    valor=valor,
                    forma_pagamento=tipo,
                    fixo=fixo
                )
                st.success("Gasto adicionado com sucesso!")


elif menu == "📌 Visão geral":
    st.title("Visão geral do mês")
    # resumo do mês
    # progresso do teto
    # objetivo mensal

# =============================
# RESUMO MENSAL
# =============================

    st.divider()
    st.subheader("Resumo financeiro")

    meses_disponiveis = listar_meses_disponiveis()

    if not meses_disponiveis:
        st.info("Nenhum gasto registrado ainda.")
    else:
        mes_selecionado = st.selectbox(
            "Selecione o mês",
            meses_disponiveis
        )

        total_mes, gastos_categoria = resumo_por_mes(mes_selecionado)

        st.metric("Total gasto no mês", f"CAD {total_mes:.2f}")

        if not gastos_categoria.empty:
            st.bar_chart(
                gastos_categoria.set_index("categoria")
            )

# =============================
# PROGRESSO DO TETO
# =============================

    st.divider()
    st.subheader("Progresso do mês")

    dados_progresso = progresso_teto()

    if dados_progresso:
        gasto = dados_progresso["gasto"]
        teto = dados_progresso["teto"]
        percentual = dados_progresso["percentual"]

        st.progress(percentual)

        restante = max(teto - gasto, 0)

        st.write(
            f"💸 Gasto atual: **CAD {gasto:.2f}**  \n"
            f"🎯 Teto mensal: **CAD {teto:.2f}**  \n"
            f"🟢 Restante: **CAD {restante:.2f}**"
        )
    else:
        st.info("Defina um teto mensal para acompanhar o progresso.")

# =============================
# OBJETIVO MENSAL
# =============================
    st.divider()
    st.subheader("Objetivo mensal")

    mensagem_objetivo = verificar_objetivo()

    if mensagem_objetivo:
        st.info(mensagem_objetivo)
    else:
        st.info("Ainda não há dados suficientes para avaliar o objetivo.")




elif menu == "📈 Histórico":
    st.title("Histórico e comparações")
    # gráfico últimos meses
    # comparação por categoria

# =============================
# COMPARAÇÃO ENTRE MESES
# =============================

    st.divider()
    st.subheader("Comparação de gastos")

    meses_disponiveis = listar_meses_disponiveis()

    if len(meses_disponiveis) < 2:
        st.info("É necessário ter pelo menos dois meses para comparar.")
    else:
        mes_atual = meses_disponiveis[0]
        mes_anterior = meses_disponiveis[1]

        gerar_despesas_fixas_mes_atual(mes_atual)

        df_atual = gastos_por_categoria_mes(mes_atual).reset_index()
        df_anterior = gastos_por_categoria_mes(mes_anterior).reset_index()

        df_linhas = (
            df_atual
            .merge(
                df_anterior,
                on="categoria",
                how="outer",
                suffixes=(f" ({mes_atual})", f" ({mes_anterior})")
            )
            .fillna(0)
            .set_index("categoria")
        )

        st.line_chart(df_linhas)



# =============================
# EVOLUÇÃO DE GASTOS
# =============================
    st.divider()
    st.subheader("Evolução de gastos")

    qtd_meses = st.slider(
        "Selecione quantos meses deseja comparar",
        min_value=2,
        max_value=12,
        value=6
    )

    serie_evolucao = total_por_mes()

    if serie_evolucao.empty:
        st.info("Ainda não há dados suficientes.")
    else:
        df_evolucao = (
            serie_evolucao
            .rename("total")
            .reset_index()
        )

        df_evolucao.columns = ["mes_referencia", "total"]
        df_evolucao = df_evolucao.tail(qtd_meses)

        st.line_chart(
            df_evolucao.set_index("mes_referencia")["total"]
        )



# =============================
# LISTA DE GASTOS
# =============================
    st.divider()
    st.subheader("Gastos registrados")

    df = ler_gastos()
    if df.empty:
        st.info("Nenhum gasto registrado ainda.")
    else:
        st.dataframe(df)


elif menu == "🧠 Insights & alertas":
    st.title("Insights e alertas")
    # insights automáticos
    # alertas

# =============================
# PAINEL DE ALERTAS E INSIGHTS
# =============================
    st.divider()
    st.subheader("Alertas e Insights da fatura")

    # 1️⃣ Garantir que temos faturas
    meses_disponiveis = listar_meses_disponiveis()
    if not meses_disponiveis:
        st.info("Ainda não há faturas registradas.")
    else:
        mes_atual = meses_disponiveis[0]       # fatura mais recente
        teto_global = ler_teto() or 0          # pega o teto global ou 0 como fallback

        # 2️⃣ Verificar gastos
        estourou, total_gasto = verificar_teto(mes_atual, teto_global)
        percentual = (total_gasto / teto_global) * 100 if teto_global > 0 else 0

        # 3️⃣ Renderização de alerta de teto
        if estourou:
            st.error(f"🚨 Você ultrapassou o teto da fatura! Total gasto: ${total_gasto:.2f} / Teto: ${teto_global:.2f}")
        elif percentual >= 80:
            st.warning(f"⚠️ Atenção: você já utilizou {percentual:.0f}% do teto da fatura. Total gasto: ${total_gasto:.2f} / Teto: ${teto_global:.2f}")
        else:
            st.info(f"✅ Total gasto até agora: ${total_gasto:.2f} / Teto: ${teto_global:.2f}")

        # 4️⃣ Barra visual de progresso
        st.progress(min(int(percentual), 100))

        # 5️⃣ Insights automáticos
        insights = gerar_insights(mes_atual)
        if insights:
            st.subheader("Insights automáticos")
            for insight in insights:
                st.info(f"💡 {insight}")
        else:
            st.info("Ainda não há insights suficientes para esta fatura.")

elif menu == "⚙️ Configurações":
    st.title("Configurações")
    # teto mensal

# =============================
# TETO MENSAL
# =============================

    st.divider()
    st.subheader("Teto mensal")

    teto_atual = ler_teto()

    novo_teto = st.number_input(
        "Defina seu teto mensal de gastos",
        min_value=0.0,
        format="%.2f",
        value=float(teto_atual)
    )

    if st.button("Salvar teto"):
        salvar_teto(novo_teto)
        st.success("Teto mensal atualizado!")








