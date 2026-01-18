import streamlit as st
from utils import adicionar_gasto, ler_gastos, resumo_mes_atual

st.title("Mini Gestor Financeiro Familiar")

# ===== FORMULÁRIO =====
with st.form("form_gasto"):
    data = st.date_input("Data")
    descricao = st.text_input("Descrição")
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
    categoria_selecionada = st.selectbox(
        "Categoria",
        CATEGORIAS_PADRAO,
        key="categoria_select"
    )

    categoria_final = categoria_selecionada

    if categoria_selecionada == "Outros":
        categoria_final = st.text_input(
            "Digite a categoria",
            key="categoria_custom"
        )

    tipo = st.selectbox("Tipo", ["Débito", "Crédito", "Dinheiro"])
    valor = st.number_input("Valor", min_value=0.0, format="%.2f")
    submitted = st.form_submit_button("Adicionar gasto")

    if submitted:
        adicionar_gasto(data, descricao, categoria_final, tipo, valor)
        st.success("Gasto adicionado!")

# ===== RESUMO =====
st.divider()
st.subheader("Resumo do mês")

total_mes, gastos_categoria = resumo_mes_atual()

st.metric("Total gasto no mês", f"R$ {total_mes:.2f}")

if not gastos_categoria.empty:
    st.bar_chart(
        gastos_categoria.set_index("categoria")
    )

# ===== LISTA DE GASTOS =====
st.divider()
st.subheader("Gastos registrados")
df = ler_gastos()
st.dataframe(df)
