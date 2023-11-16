"""
This module fetches Azure services from the Azure Products page and returns them as a list of services.
"""
import argparse
import json
import logging
import os
import re
import requests
from bs4 import BeautifulSoup

AZURE_PRODUCTS_URL = "https://azure.microsoft.com/en-us/products"
AZURE_PRODUCT_URL_PREFIX = "https://azure.microsoft.com"
AZURE_PRODUCT_CATEGORIES_SELECTOR = 'div.container'
AZURE_PRODUCT_SELECTOR = 'div.card-body'
AZURE_PRODUCT_SUMMARY_SELECTOR = 'p'
AZURE_PRODUCT_NAME_REPLACEMENTS = {
    'QnA Maker': 'qnamaker',
    'Azure CycleCloud': 'azure-cyclecloud',
    'Load Balancer': 'azure-load-balancing',
    'Azure Data Lake Storage Gen1': 'data-lake-storage-gen1',
    'SDKs': 'sdk',
    'Azure Applied AI Services': 'applied-ai-services',
    'Azure Kubernetes Service Edge Essentials': 'kubernetes-service-edge-essentials',
}

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def fetch_azure_services(custom_services_path: str = "custom-services/azure.json") -> list:
    """
    Fetches Azure services from the Azure website and returns them as a list of dictionaries.

    Returns:
        A list of dictionaries representing Azure services.
    """
    try:
        # Read custom services JSON file if it exists
        if os.path.exists(custom_services_path):
            with open(custom_services_path, "r") as f:
                custom_services = json.load(f)
        else:
            custom_services = []

        with requests.Session() as session:
            response = session.get(AZURE_PRODUCTS_URL)
            response.raise_for_status()

        soup = BeautifulSoup(response.text, 'lxml')
        services_dict = {}

        categories = soup.select(AZURE_PRODUCT_CATEGORIES_SELECTOR)
        for category in categories:
            # skip if category does not have an id or if it is a layout container
            if not category.get('id') or category['id'].startswith('layout-container-'):
                continue
            category_id = f'azure/category/{category["id"]}'
            h2_element = category.find('h2')
            # skip if category does not have an h2 element
            if not h2_element:
                continue
            category_name = h2_element.text.strip()
            # top category header
            category_header_div = category.find_parent('div').find_parent('div')
            category_products_div = category_header_div.find_next_sibling().find_next_sibling()
            products = category_products_div.select(AZURE_PRODUCT_SELECTOR)
            for product in products:
                # skip if product element has no h3 element
                if not product.find('h3'):
                    continue
                link_element = product.find('a')
                if not link_element:
                    continue
                # get product name from aria-label attribute
                product_name = link_element['aria-label']
                # replace strange Preview text ᴾᴿᴱⱽᴵᴱᵂ with Preview
                product_name = product_name.replace('ᴾᴿᴱⱽᴵᴱᵂ', 'Preview')
                # replace strange Preview text PREVIEW with Preview
                product_name = product_name.replace('PREVIEW', 'Preview')
                # get product url from href attribute
                product_url = product.find('a')['href']
                if not product_url.startswith('https'):
                    product_url = f'{AZURE_PRODUCT_URL_PREFIX}{product_url}'
                # construct product id from url
                tokens = re.split('/products/|/services/|/features/', product_url)
                token = tokens[1] if len(tokens) > 1 else product_url.split('/')[-2]
                # trim all after /? to remove query params
                token = token.split('/?')[0]
                token = token.rstrip('/').replace('/', '-')
                product_id = AZURE_PRODUCT_NAME_REPLACEMENTS.get(product_name, token)
                summary_element = product.find(AZURE_PRODUCT_SUMMARY_SELECTOR)
                if not summary_element:
                    continue
                product_summary = summary_element.text.strip()
                # remove last dot from summary
                if product_summary.endswith('.'):
                    product_summary = product_summary[:-1]
                if product_id not in services_dict:
                    services_dict[product_id] = {
                        'id': f'azure/{product_id}',
                        'name': product_name,
                        'summary': product_summary,
                        'url': product_url,
                        'categories': [{'id': category_id, 'name': category_name}],
                        'tags': ['azure/platform', f'azure/service/{product_id}', category_id]
                    }
                else:
                    services_dict[product_id]['categories'].append({'id': category_id, 'name': category_name})
                    services_dict[product_id]['tags'].append(category_id)

        services = list(services_dict.values())
        services.extend(custom_services)
        services = sorted(services, key=lambda x: x['id'])
        return services
    except Exception as e:
        logger.error(f"An error occurred while fetching Azure services: {e}")
        return []


def main(custom_services_path: str) -> None:
    """
    Fetches Azure services and prints them as a JSON string.

    Args:
        custom_services_path: The path to the custom services JSON file.
    """
    services = fetch_azure_services(custom_services_path)
    print(json.dumps(services, indent=4))


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Fetches Azure services.')
    parser.add_argument('--custom-services', dest='custom_services_path', default='custom-services/azure.json',
                        help='Path to the custom services JSON file.')
    args = parser.parse_args()

    logging.basicConfig(level=logging.INFO)
    main(args.custom_services_path)
