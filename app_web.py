import streamlit as st
import calculos_lib
import os

# Configuração da página
st.set_page_config(page_title="Arte Preco Pro", page_icon="💰")

# Exibir a logo se ela existir na pasta
if os.path.exists("logo.ico"):
    st.image("logo.ico", width=200)
elif os.path.exists("logo.png"):
    st.image("logo.png", width=200)

st.title("Arte Preco Pro")
st.subheader("Sistema de Precificação")

# Entradas de dados
empresa_nome = st.text_input("Nome da Empresa")
empresa_tel = st.text_input("Telefone / WhatsApp")

st.divider()

produto = st.text_input("Nome do Produto")
material = st.number_input("Custo do Material (R$)", min_value=0.0, format="%.2f")
horas = st.number_input("Horas Trabalhadas", min_value=0.0, format="%.2f")
valor_hora = st.number_input("Valor da Hora (R$)", min_value=0.0, format="%.2f")
despesas = st.number_input("Despesas Extras (R$)", min_value=0.0, format="%.2f")
margem = st.number_input("Margem de Lucro (%)", min_value=0.0, format="%.2f")
validade = st.number_input("Validade (dias)", min_value=1, value=7, step=1)
obs = st.text_area("Observações para o PDF")

# Botão de cálculo
if st.button("Calcular e Gerar Resultado"):
    if not produto:
        st.warning("Por favor, informe o nome do produto.")
    else:
        custo_mao_obra = horas * valor_hora
        custo_total = material + custo_mao_obra + despesas
        preco_final = custo_total + (custo_total * margem / 100.0)
        
        st.success(f"Preço Final Sugerido: R$ {preco_final:,.2f}")
        st.info("Cálculo realizado com sucesso!")