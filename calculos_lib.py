# calculos_lib.py - Versão pura para Web (sem interface gráfica)

def format_orc(orc_num):
    return f"ORC-{orc_num:04d}"

def load_data():
    # Aqui você pode colocar sua lógica de carregar arquivos, se tiver
    return {"next_orc": 1}

# Se você tinha funções que usavam messagebox, remova o uso de messagebox.
# O Streamlit já tem suas próprias mensagens (st.warning, st.success, etc).
