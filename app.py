import streamlit as st
from utils import adicionar_gasto, ler_gastos, listar_meses_disponiveis, resumo_por_mes

st.set_page_config(page_title="Mini Gestor Financeiro Familiar", layout="centered")

st.title("Mini Gestor Financeiro Familiar")

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

st.subheader("Novo gasto")

categoria_selecionada = st.selectbox(
    "Categoria",
    CATEGORIAS_PADRAO
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
    tipo = st.selectbox("Tipo de pagamento", ["Débito", "Crédito", "Dinheiro"])
    valor = st.number_input("Valor", min_value=0.0, format="%.2f")

    submitted = st.form_submit_button("Adicionar gasto")

    if submitted:
        if not categoria_final:
            st.warning("Informe a categoria do gasto.")
        else:
            adicionar_gasto(data, descricao, categoria_final, tipo, valor)
            st.success("Gasto adicionado com sucesso!")

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

    st.metric("Total gasto no mês", f"R$ {total_mes:.2f}")

    if not gastos_categoria.empty:
        st.bar_chart(
            gastos_categoria.set_index("categoria")
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
