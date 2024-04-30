import psycopg2
import apache_beam as beam
import os
import json
import logging

class GetNames(beam.DoFn):
    def process(self, element):
        # Parâmetros de conexão
        with open('config/credentiales.json') as f:
            config = json.load(f)

        # Definindo as variáveis de ambiente
        os.environ['DB_USER'] = config['DB_USER']
        os.environ['DB_PASSWORD'] = config['DB_PASSWORD']
        os.environ['DB_HOST'] = config['DB_HOST']
        os.environ['DB_PORT'] = config['DB_PORT']
        os.environ['DB_DATABASE'] = config['DB_DATABASE']
        
        #Pegando as credenciais via variável de ambiente
        USERNAME = os.getenv('DB_USER')
        PASSWORD = os.getenv('DB_PASSWORD')
        HOST = os.getenv('DB_HOST')
        PORT = os.getenv('DB_PORT')
        DATABASE = os.getenv('DB_DATABASE')

        conn_params = {
            "host": HOST,
            "database": DATABASE,
            "user": USERNAME,
            "password": PASSWORD,
            "port": PORT
        }
        try:
            # Conectar ao banco de dados
            conn = psycopg2.connect(**conn_params)
            
            # Criar um cursor para executar consultas SQL
            cursor = conn.cursor()
            
            # Consulta SQL para obter os nomes das tabelas existentes
            query = """
            SELECT table_name
            FROM information_schema.tables
            WHERE table_schema = 'public'  -- Onde 'public' é o esquema padrão do PostgreSQL
            """
            
            # Executar a consulta
            cursor.execute(query)
            
            # Obter os resultados
            tables = cursor.fetchall()
            
            # Exibir os nomes das tabelas
            list_names = []
            for table in tables:
                list_names.append(table[0])
            
            logging.info(f'Nomes das tabelas:\n{list_names}')
            # Fechar o cursor e a conexão
            cursor.close()
            conn.close()

            yield list_names
            
        except psycopg2.Error as e:
            print("Erro ao conectar ou consultar o banco de dados:", e)
            # Obter os resultados
            tables = cursor.fetchall()

            yield tables