def calcular_preco(custo_material, horas, valor_hora, despesas, margem):
    # Calcula o custo total
    custo_total = custo_material + (horas * valor_hora) + despesas
    # Aplica a margem de lucro
    preco_final = custo_total * (1 + (margem / 100))
    return custo_total, preco_final
