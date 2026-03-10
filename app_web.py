import streamlit as st
from fpdf import FPDF
import calculos_lib

# Configuração da página
st.set_page_config(
    page_title="Arte Preço Pro", 
    page_icon="logo.ico", 
    layout="centered"
)

st.title("🎨 Arte Preço Pro")
st.subheader("Sistema de Precificação")

# Campos de Entrada
empresa = st.text_input("Nome da empresa")
produto = st.text_input("Nome do Produto")
custo_mat = st.number_input("Custo do Material (R$)", min_value=0.0, format="%.2f")
horas = st.number_input("Horas trabalhadas", min_value=0.0)
valor_hora = st.number_input("Valor da hora (R$)", min_value=0.0, format="%.2f")
despesas = st.number_input("Despesas iniciais (R$)", min_value=0.0, format="%.2f")
margem = st.number_input("Margem de Lucro (%)", min_value=0.0)

# Lógica do Botão
if st.button("Calcular e Gerar Orçamento"):
    custo_t, preco_f = calculos_lib.calcular_preco(custo_mat, horas, valor_hora, despesas, margem)
    
    st.success(f"Custo Total: R$ {custo_t:.2f}")
    st.info(f"Preço Sugerido de Venda: R$ {preco_f:.2f}")

    # Gerar PDF em memória
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", 'B', 16)
    pdf.cell(200, 10, txt="ORCAMENTO - ARTE PRECO PRO", ln=True, align='C')
    pdf.set_font("Arial", size=12)
    pdf.ln(10)
    pdf.cell(200, 10, txt=f"Empresa: {empresa}", ln=True)
    pdf.cell(200, 10, txt=f"Produto: {produto}", ln=True)
    pdf.cell(200, 10, txt=f"Custo Total: R$ {custo_t:.2f}", ln=True)
    pdf.cell(200, 10, txt=f"Preco Final Sugerido: R$ {preco_f:.2f}", ln=True)
    
    # Criar o ficheiro para download
    pdf_bytes = pdf.output(dest='S').encode('latin-1')

    st.download_button(
        label="📥 Baixar Orçamento em PDF",
        data=pdf_bytes,
        file_name="orcamento.pdf",
        mime="application/pdf"
    )
