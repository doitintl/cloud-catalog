import json
import os
import logging
import argparse
import pandas as pd
from pyspark.sql import SparkSession
from sql_statements import focus_areas_to_skills_sql, exceptions_sql


parser = argparse.ArgumentParser()
parser.add_argument("--debug", action='store_true', help="Additional logging", default=False)
args = parser.parse_args()

log_level = os.environ.get('LOG_LEVEL', logging.INFO)

logging.basicConfig(
    level=logging.DEBUG if args.debug else log_level,
    format='%(asctime)s - %(levelname)s - %(message)s',
    datefmt="%Y-%m-%d %H:%M:%S"
)

data_dir = '../data/'
cc_files = [os.path.join(data_dir, i) for i in ['aws.json', 'gcp.json', 'azure.json', 'gsuite.json', 'ms365.json']]
fa_file = os.path.join(data_dir, 'focus_areas', 'FocusAreas.tsv')
ptfa_file = os.path.join(data_dir, 'focus_areas', 'ProductToFocusArea.tsv')
ctfa_file = os.path.join(data_dir, 'focus_areas', 'CategoryToFocusArea.tsv')

spark = SparkSession \
    .builder \
    .getOrCreate()


def get_platform(file):
    if 'aws' in file:
        return 'AWS'
    elif 'gcp' in file:
        return 'Google Cloud'
    elif 'azure' in file:
        return 'Microsoft Azure'
    elif 'gsuite' in file:
        return 'Google Workspace'
    elif 'ms365' in file:
        return 'Microsoft Office 365'


def process_catalog_files():
    logging.info("Processing Cloud Catalog files")

    product_records = []

    for file in cc_files:
        logging.info(f'Processing {file}')
        file_path = os.path.join(data_dir, file)
        platform = get_platform(file)
        with open(file_path, 'r') as f:
            data = json.load(f)
            for record in data:
                catalog_id = record['id']
                product = record['name']
                for tag_value in record['tags']:
                    tag_type = tag_value.split('/')[1]
                    product_records.append([catalog_id, platform, product, tag_type, tag_value])

    product_tags_df = pd.DataFrame(product_records,
                      columns=['catalog_id', 'platform', 'product', 'tag_type', 'tag_value'])

    product_tags_df.drop_duplicates(inplace=True)

    if args.debug:
        product_tags_df.head(20)

    return spark.createDataFrame(product_tags_df)


def map_focus_area_skills(catalog_product_tags_df, fa_df, ptfa_df, ctfa_df):
    logging.info("Mapping Focus Areas to primary and secondary skills")
    fa_df.createOrReplaceTempView('focus_areas')
    ptfa_df.createOrReplaceTempView('product_to_focus_area')
    ctfa_df.createOrReplaceTempView('category_to_focus_area')
    catalog_product_tags_df.createOrReplaceTempView('catalog_product_tags')

    df = spark.sql(focus_areas_to_skills_sql)

    if args.debug:
        df.show(truncate=False)
    return df


def get_exceptions():
    logging.info("Generating exceptions ")
    exc_df = spark.sql(exceptions_sql)

    if args.debug:
        exc_df.show(4, truncate=False)

    return exc_df


def write_json_file(filename, payload):
    file_name = filename.replace(' ', '_').lower()
    with open(file_name, "w") as outfile:
        logging.info(f"Writing to {file_name}")
        outfile.write(json.dumps(payload, indent=4))


def df_to_json_files(collected, pk, relative_path):
    entire_json = []
    # write one file per focus area
    for line in collected:
        json_line = json.loads(line)

        json_pk = json_line[pk]
        entire_json.append(json_line)

        file_name = f"{os.path.join(relative_path, json_pk.replace('/', '_'))}.json"
        write_json_file(file_name, json_line)

    # Write a file containing all focus areas
    file_name = os.path.join(relative_path, 'all.json')
    write_json_file(file_name, entire_json)


def create_json_files(fa_df, exc_df):
    logging.info("Writing Focus Areas files")
    df_to_json_files(fa_df, 'id', f"{os.path.join(data_dir, 'focus_areas')}")
    df_to_json_files(exc_df, 'platform', f"{os.path.join(data_dir, 'focus_areas', 'exceptions')}")


def main():
    product_tags_df = process_catalog_files()
    fa_df = spark.read.options(delimiter='\t', header=True).csv(fa_file)
    ptfa_df = spark.read.options(delimiter='\t', header=True).csv(ptfa_file)
    ctfa_df = spark.read.options(delimiter='\t', header=True).csv(ctfa_file)

    focus_areas = map_focus_area_skills(product_tags_df, fa_df, ptfa_df, ctfa_df).toJSON().collect()
    exceptions = get_exceptions().toJSON().collect()

    spark.stop()

    create_json_files(focus_areas, exceptions)


if __name__ == "__main__":
    main()
