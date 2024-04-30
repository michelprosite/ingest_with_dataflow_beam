import psycopg2
import apache_beam as beam
import logging
import pandas as pd
from google.cloud import storage
import os
import json

class GetTables(beam.DoFn):
    def process(self, element):
        for table in element:
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

                query = f"select * from {table} limit 10"

                cursor.execute(query)

                col_names = [desc[0] for desc in cursor.description]

                rows = cursor.fetchall()

                df = pd.DataFrame(rows, columns=col_names)

                # Altere pelo nome do seu bucket o o path da parta de destino dentro do bucket
                bucket_name = 'bucket-postigres-dataflow'
                path = f'data-postgres/{table}.parquet'

                client = storage.Client()
                bucket = client.get_bucket(bucket_name)
                blob = bucket.blob(path)

                parquet = df.to_parquet(index=False)

                blob.upload_from_string(parquet)

                cursor.close()
                conn.close()

                logging.info(f'{table} {"=" * (80 - len(table))} {df.shape}')

                yield parquet

            except psycopg2.Error as e:
                logging.info(f"Erro encontrado durante a conecção: {e}")

            