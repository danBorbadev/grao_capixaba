import csv
from decimal import Decimal
from db.connection import conectar_banco


def carregar_csv(caminho):
    conn = None
    cursor = None

    try:
        conn = conectar_banco()
        cursor = conn.cursor()

        linhas_validas = []
        total_google = None

        # 1) LEITURA DO ARQUIVO
        with open(caminho, "r", encoding="utf-8", newline="") as arquivo:
            leitor = csv.reader(arquivo, delimiter=",")

            # pula tudo até achar o cabeçalho
            for linha in leitor:
                if linha and linha[0] == "Day":
                    break
            else:
                raise ValueError("Cabeçalho 'Day' não encontrado no arquivo.")

            # lê os dados até o rodapé de total
            for linha in leitor:
                if not linha:
                    continue
                if linha[0].startswith("Total"):
                    total_google = Decimal(linha[3])
                    break
                linhas_validas.append(linha)

        if not linhas_validas:
            raise ValueError("Nenhuma linha de dados encontrada.")

        # 2) CONFERÊNCIA DO TOTAL (antes de tocar no banco)
        soma_custo = sum(Decimal(l[3]) for l in linhas_validas)

        if total_google is not None:
            diferenca = abs(soma_custo - total_google)
            tolerancia = Decimal("0.005") * len(linhas_validas)  # meio centavo por linha

            if diferenca > tolerancia:
                raise ValueError(
                    f"Soma ({soma_custo}) diferente do total do Google ({total_google}). "
                    f"Diferença {diferenca} acima da tolerância {tolerancia}."
                )
            if diferenca > 0:
                print(f"Aviso: diferença de R$ {diferenca} por arredondamento "
                      f"(tolerância R$ {tolerancia}).")

        # 3) PROTEÇÃO CONTRA CARGA DUPLICADA (consulta, não altera nada)
        data_inicio = min(l[0] for l in linhas_validas)
        data_fim = max(l[0] for l in linhas_validas)

        cursor.execute(
            "SELECT count(*) FROM campanhas_google_ads WHERE dia BETWEEN %s AND %s",
            (data_inicio, data_fim),
        )
        ja_existentes = cursor.fetchone()[0]

        if ja_existentes > 0:
            raise ValueError(
                f"Já existem {ja_existentes} linhas entre {data_inicio} e {data_fim}. "
                f"Carga cancelada para não duplicar dados."
            )

        # 4) GRAVAÇÃO
        cursor.executemany(
            """
            INSERT INTO campanhas_google_ads
                (dia, campanha, status, custo, impressoes, cliques, conversoes)
            VALUES (%s, %s, %s, %s, %s, %s, %s)
            """,
            linhas_validas,
        )

        conn.commit()
        print(f"{len(linhas_validas)} linhas gravadas ({data_inicio} a {data_fim}). "
              f"Custo total: R$ {soma_custo}")

    except Exception as erro:
        if conn:
            conn.rollback()
        print(f"Erro ao carregar CSV: {erro}")

    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()


if __name__ == "__main__":
    carregar_csv("dados_originais/google_ads_report.csv")