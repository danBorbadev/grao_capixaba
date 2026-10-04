
import os 
import psycopg
from dotenv import load_dotenv
load_dotenv()

def conectar_banco():
    try:
        conn = psycopg.connect(
            host=os.getenv("DBHOST"),
            port=os.getenv("DBPORT"),
            dbname=os.getenv("DBNAME"),
            user=os.getenv("DBUSER"),
            password=os.getenv("DBPASSWORD")
        )
        print("Conectado ao banco com sucesso")
        return conn
    except Exception as erro:
        print('Falha ao conectar ao banco, verifique as credenciais')
        print(f'Erro: {erro}')
        return None

conn = conectar_banco()

if conn: 
    print('Banco Disponível')


cursor = conn.cursor()

cursor.execute("SELECT * FROM clientes");

dados = cursor.fetchall()
print(dados)