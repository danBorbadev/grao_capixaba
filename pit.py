import csv
with open("dados_limpos/clientes_crm.csv", encoding="utf-8-sig") as f:
    for i, linha in enumerate(csv.reader(f, delimiter=";")):
        print(len(linha), linha)
        if i == 2:
            break