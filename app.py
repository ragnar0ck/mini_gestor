import streamlit as st
from utils import adicionar_gasto, ler_gastos
import pandas as pd

st.title("Mini Gestor Financeiro Familiar")

# Formulário de novo gasto
with st.form("form_gasto"):
    data = st.date_input("Data")
    descricao = st.text_input("Descrição")
    categoria = st.text_input("Categoria")
    tipo = st.selectbox("Tipo", ["Débito", "Crédito", "Dinheiro"])
    valor = st.number_input("Valor", min_value=0.0, format="%.2f")
    submitted = st.form_submit_button("Adicionar gasto")

    if submitted:
        adicionar_gasto(data, descricao, categoria, tipo, valor)
        st.success("Gasto adicionado!")

# Exibir gastos
st.subheader("Gastos registrados")
df = ler_gastos()
st.dataframe(df)
