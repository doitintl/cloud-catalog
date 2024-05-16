import json
import os
import logging
import argparse
import pandas as pd
from pyspark.sql import SparkSession


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
    category_records = []

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
                    if tag_type == 'category':
                        category_records.append([platform, tag_value])

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

    df = spark.sql('''
        WITH meta AS (
            SELECT 'aws' AS platform_short, 'AWS' AS platform
            UNION ALL SELECT 'gcp' AS platform_short, 'Google Cloud' AS platform
            UNION ALL SELECT 'azure' AS platform_short, 'Microsoft Azure' AS platform
            UNION ALL SELECT 'gsuite' AS platform_short, 'Google Workspace' AS platform
            UNION ALL SELECT 'ms365' AS platform_short, 'Microsoft Office 365' AS platform
        ), ptfa AS (
        -- Products that are not VERIFIED should be unassigned
        SELECT
            product,
            platform, 
            CASE 
                WHEN ptfa.status = 'VERIFIED'
                THEN ptfa.p_group
                ELSE 'Unassigned'         
            END AS p_group,
            CASE 
                WHEN ptfa.status = 'VERIFIED'
                THEN ptfa.focus_area
                ELSE 'Unassigned'         
            END AS focus_area,
            ptfa.support_level
        FROM product_to_focus_area ptfa
        )
        SELECT
            -- Create the focus area id
            CONCAT(
                'cre/fa/', 
                meta.platform_short,
                '/',
                REGEXP_REPLACE(LOWER(fa.focus_area), '[ /]', '_')
            ) AS id,
            ARRAY_SORT(
                ARRAY_UNION(
                    -- Aggregate service tags for Products that match cloud catalog
                    ARRAY_AGG(
                        CASE 
                            WHEN 
                                ctfa.support_level = 'PRIMARY' 
                                AND cpt_categories.tag_value IS NOT NULL
                            THEN cpt_categories.tag_value 
                            ELSE NULL 
                        END 
                    ),
                    -- Aggregate category tags for categories that match cloud catalog
                    ARRAY_AGG(
                        CASE 
                            WHEN ctfa.support_level = 'PRIMARY' 
                                AND cpt_services.tag_value IS NOT NULL
                            THEN cpt_services.tag_value 
                            ELSE NULL 
                        END
                    )
                )
            ) AS primary_skills,
            ARRAY_SORT(
                ARRAY_UNION(
                    -- Aggregate service tags for Products that match cloud catalog
                    ARRAY_AGG(
                        CASE 
                            WHEN 
                                ctfa.support_level = 'SECONDARY' 
                                AND cpt_categories.tag_value IS NOT NULL
                            THEN cpt_categories.tag_value 
                            ELSE NULL 
                        END 
                    ),
                    -- Aggregate category tags for categories that match cloud catalog
                    ARRAY_AGG(
                        CASE 
                            WHEN ptfa.support_level = 'SECONDARY' 
                                AND cpt_services.tag_value IS NOT NULL
                            THEN cpt_services.tag_value 
                            ELSE NULL 
                        END
                    )
                )
            ) AS secondary_skills,
            ARRAY_SORT(
                -- Capture products and category tags that are mapped to focus area but do not exist in CC
                ARRAY_UNION(
                    ARRAY_AGG(
                        CASE 
                            WHEN cpt_categories.tag_value IS NULL
                            THEN ctfa.category_tag 
                            ELSE NULL 
                        END 
                    ),
                    ARRAY_AGG(
                        CASE 
                            WHEN cpt_services.tag_value IS NULL
                            THEN ptfa.product 
                            ELSE NULL 
                        END
                    )
                )
            ) AS exceptions
        FROM focus_areas fa
        JOIN meta ON fa.platform = meta.platform
        JOIN category_to_focus_area ctfa 
            ON fa.platform = ctfa.platform
            AND fa.focus_area = ctfa.focus_area
            AND ctfa.support_level != 'NONE'
        JOIN ptfa
            ON fa.platform = ptfa.platform
            AND fa.focus_area = ptfa.focus_area
        LEFT OUTER JOIN catalog_product_tags cpt_services
            ON fa.platform = cpt_services.platform
            AND ptfa.product = cpt_services.product 
            AND cpt_services.tag_type = 'service'
        LEFT OUTER JOIN catalog_product_tags cpt_categories
            ON fa.platform = cpt_categories.platform
            AND ctfa.category_tag = cpt_categories.tag_value 
            AND cpt_categories.tag_type = 'category'
        GROUP BY 1
        ORDER BY 1
    ''')

    if args.debug:
        df.show(truncate=False)
    return df


def create_focus_area_files(df):
    logging.info("Writing Focus Areas files")
    focus_areas = df.toJSON().collect()
    # spark is no longer needed
    spark.stop()

    all_focus_areas = []

    # write one file per focus area
    for line in focus_areas:
        focus_area = json.loads(line)
        focus_area_id = focus_area['id']
        all_focus_areas.append(focus_area)

        file_name = f"{os.path.join(data_dir, 'focus_areas', focus_area_id.replace('/', '_'))}.json"
        with open(file_name, "w") as outfile:
            logging.info(f"Writing to {file_name}")
            outfile.write(json.dumps(focus_area, indent=4))

    # Write a file containing all focus areas
    file_name = os.path.join(data_dir, 'focus_areas', 'focus_areas.json')
    with open(file_name, "w") as outfile:
        logging.info(f"Writing to {file_name}")
        outfile.write(json.dumps(all_focus_areas, indent=4))


def main():
    product_tags_df = process_catalog_files()
    fa_df = spark.read.options(delimiter='\t', header=True).csv(fa_file)
    ptfa_df = spark.read.options(delimiter='\t', header=True).csv(ptfa_file)
    ctfa_df = spark.read.options(delimiter='\t', header=True).csv(ctfa_file)

    fa_df = map_focus_area_skills(product_tags_df, fa_df, ptfa_df, ctfa_df)

    create_focus_area_files(fa_df)


if __name__ == "__main__":
    main()
