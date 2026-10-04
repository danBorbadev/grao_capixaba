import csv 
from db.connection import conectar_banco


def carregar_csv(caminho):
    conn = None
    cursor = None

    try:
        conn = conectar_banco()
        cursor = conn.cursor()

        with open(caminho, "r", encoding="utf-8") as arquivo:

            leitor = csv.reader(arquivo, delimiter=";")

            # Pula o cabeçalho
            next(leitor)

            for linha in leitor:
            
                cursor.execute(
                    """
                    INSERT INTO pedidos_ecommerce(
                        id_pedido,
                        data_pedido,
                        email,
                        canal_venda,
                        utm_source,
                        utm_medium,
                        utm_campaign,
                        cupom,
                        valor_produtos,
                        desconto,
                        frete,
                        valor_total,
                        status
                    )
                    VALUES (
                        %s,
                        %s,
                        %s,
                        %s,
                        %s,
                        %s,
                        %s,
                        %s,
                        %s,
                        %s,
                        %s,
                        %s,
                        %s
        
                        
                    )
                    """,
                    linha
                )

        conn.commit()

        print("Dados carregados com sucesso!")

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
    carregar_csv("dados_limpos/pedidos_ecommerce.csv")