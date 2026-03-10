def format_orc(orc_num):
    return f"ORC-{orc_num:04d}"

def calcular_preco(custo_material, horas, valor_hora, despesas, margem):
    custo_total = custo_material + (horas * valor_hora) + despesas
    preco_final = custo_total * (1 + (margem / 100))
    return custo_total, preco_final
