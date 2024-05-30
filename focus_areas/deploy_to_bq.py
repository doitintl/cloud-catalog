import os
import logging
import argparse
import pandas as pd
import shutil
from google.cloud import bigquery

parser = argparse.ArgumentParser()
parser.add_argument("--project_id", default=os.environ.get('CLOUDSDK_CORE_PROJECT', None))
parser.add_argument("--build", action='store_true', help="Run the build stage", default=True)
parser.add_argument("--deploy", action='store_true', help="Run the deploy stage", default=False)
parser.add_argument("--debug", action='store_true', help="Additional logging", default=False)
args = parser.parse_args()

log_level = os.environ.get('LOG_LEVEL', logging.INFO)

logging.basicConfig(
    level=logging.DEBUG if args.debug else log_level,
    format='%(asctime)s - %(levelname)s - %(message)s',
    datefmt="%Y-%m-%d %H:%M:%S"
)

build_dir = '../build/focus_areas/bq'
fa_file = '../data/focus_areas/all.json'
fa_parquet_file = os.path.join(build_dir, 'focus_areas.parquet')
bq_project_id = args.project_id
bq_dataset_id = 'focus_areas_analysis'
fa_table_id = 'focus_areas'
build = args.build
deploy = args.deploy


def prep_build():
    if os.path.exists(build_dir):
        shutil.rmtree(build_dir)
    os.makedirs(build_dir)


def json_to_parquet(input_file, output_file):
    df = pd.read_json(input_file)
    df.to_parquet(output_file, index=False)
    if args.debug:
        df.head()
    logging.info(f"Output written to {output_file}")


def get_load_job_config(table_id):
    parquet_options = bigquery.format_options.ParquetOptions()
    parquet_options.enable_list_inference = True

    load_job_config = {
        'focus_areas': {
            'load_job_config': bigquery.LoadJobConfig(
                schema=[
                    bigquery.SchemaField("id", "STRING"),
                    bigquery.SchemaField("name", "STRING"),
                    bigquery.SchemaField("practice_area", "STRING"),
                    bigquery.SchemaField("primary_skills", "STRING", mode="REPEATED"),
                    bigquery.SchemaField("secondary_skills", "STRING", mode="REPEATED")
                ],
                source_format=bigquery.SourceFormat.PARQUET,
                write_disposition='WRITE_TRUNCATE',
                create_disposition='CREATE_IF_NEEDED',
                parquet_options=parquet_options
            ),
            'source_file': fa_parquet_file
        }
    }
    return load_job_config[table_id]


def load_data_to_bigquery(project_id, dataset_id, table_id):
    client = bigquery.Client(project=project_id)
    dataset_ref = bigquery.DatasetReference(project=project_id, dataset_id=dataset_id)
    table_ref = bigquery.TableReference(dataset_ref=dataset_ref, table_id=table_id)

    load_job_config = get_load_job_config(table_id)
    job_config = load_job_config['load_job_config']
    source_file = load_job_config['source_file']

    with open(source_file, "rb") as f:
        load_job = client.load_table_from_file(
            f,
            table_ref,
            job_config=job_config,
        )

    try:
        load_job.result()

    except Exception as e:
        logging.exception(e)

    logging.info("Loaded {} rows into {}:{}.".format(load_job.output_rows, dataset_id, table_id))


def main():
    prep_build()
    json_to_parquet(fa_file, fa_parquet_file)
    if args.deploy and bq_project_id is not None:
        load_data_to_bigquery(bq_project_id, bq_dataset_id, fa_table_id)


if __name__ == "__main__":
    main()
