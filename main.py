from apache_beam.options.pipeline_options import PipelineOptions
import apache_beam as beam
import os
import pandas as pd
import pyarrow
from google.cloud import storage
import logging
import sys
from datetime import datetime

logging.basicConfig(level=logging.INFO, stream=sys.stdout, format="%(asctime)s - %(levelname)s - %(message)s")

serveiceAccount = r'keys/dataflow-modelo-flex.json'
os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = serveiceAccount

now = datetime.now()
formatted_datetime = now.strftime("%Y-%m-%d--%H-%M")

def main(argv=None):
    options = PipelineOptions(
        flags=argv,
        project='dataflow-modelo-flex',
        runner='DataflowRunner',
        streaming=False,
        job_name=f'conection-postgres-{formatted_datetime}',
        temp_location ='gs://bucket-postigres-dataflow/temp',
        staging_location ='gs://bucket-postigres-dataflow/staging',
        template_location=f'gs://bucket-postigres-dataflow/templates/template-conection-postgres-{formatted_datetime}',
        autoscaling_algorithm='THROUGHPUT_BASED',
        worker_machine_type='n1-standard-4',
        service_account_key_file='./keys',
        num_workers=1,
        max_num_workers=3,
        number_of_worker_harness_threads=2,
        disk_size_gb=50,
        region='southamerica-east1',
        save_main_session=True,
        sdk_container_image='southamerica-east1-docker.pkg.dev/dataflow-modelo-flex/conection-postgres-oracle-v2/postgres-dev2:latest',
        sdk_location='container',
        requirements_file='./requirements.txt',
        metabase_file='./metadata.json',
        setup_file='./setup.py',
        service_account_email='consulta-ddos-postgres@dataflow-modelo-flex.iam.gserviceaccount.com'
    )

    from function.get_names import GetNames
    from function.get_tables import GetTables

    with beam.Pipeline(options=options) as p1:
        get_names = (
            p1
            | f'Create get names' >> beam.Create([None])
            | f'Execute Get Names' >> beam.ParDo(GetNames())
        )

        get_tables = (
            get_names
            | f'Execute Get Tables' >> beam.ParDo(GetTables())
        )

if __name__ == '__main__':
    main()