"""
This module fetches GCP services from the GCP products page and returns them as a list of services.
"""
import argparse
import json
import logging
import os
import requests
from bs4 import BeautifulSoup

GCP_PRODUCTS_URL = "https://cloud.google.com/products/"


def fetch_gcp_services(custom_services_path: str) -> list:
    """
    Fetches GCP services from the GCP products page and custom services from a JSON file.

    Args:
        custom_services_path: Path to the custom services JSON file.

    Returns:
        A list of dictionaries representing GCP services.
    """
    try:
        # Read custom services JSON file if it exists
        if os.path.exists(custom_services_path):
            with open(custom_services_path, "r") as f:
                custom_services = json.load(f)
        else:
            custom_services = []

        with requests.Session() as session:
            response = session.get(GCP_PRODUCTS_URL)
            response.raise_for_status()

        soup = BeautifulSoup(response.text, 'lxml')

        services_dict = {}
        skip_categories = ['featured-products', 'additional-google-products']
        skip_products = ['google-workspace-essentials']

        categories = soup.find_all('section', class_=['cws-jump-section'])
        for category in categories:
            category_id = category.get('id')
            if category_id in skip_categories:
                continue
            category_id = f'gcp/category/{category_id}'
            category_name = category.get('data-cws-menu-text')
            # find all 'a' tags with 'track-type' attribute 'card'
            products = category.find_all('a', {'track-type': 'card'})
            for product in products:
                product_id = product.get('track-metadata-child_headline').rstrip().replace('.', '-').replace(' ', '-').\
                    replace('(', '').replace(')', '').replace('*', '').lower()
                if product_id in skip_products:
                    continue
                # find all 'div' tags
                divs = product.find_all('div')
                # get non-empty divs (with text)
                non_empty_divs = [div for div in divs if div.string and div.string.strip()]
                if not non_empty_divs:
                    continue
                product_name = non_empty_divs[0].text.strip().replace('*', '')
                if len(non_empty_divs) > 1:
                    product_summary = non_empty_divs[1].text.strip()
                else:
                    product_summary = ''

                product_url = product['href']
                if not product_url.startswith('https'):
                    product_url = f'https://cloud.google.com{product_url}'

                # noinspection DuplicatedCode
                if product_id not in services_dict:
                    services_dict[product_id] = {
                        'id': f'gcp/{product_id}',
                        'name': product_name,
                        'summary': product_summary,
                        'url': product_url,
                        'categories': [{'id': category_id, 'name': category_name}],
                        'tags': ['gcp/platform', f'gcp/service/{product_id}', category_id]
                    }
                else:
                    services_dict[product_id]['categories'].append({'id': category_id, 'name': category_name})
                    services_dict[product_id]['tags'].append(category_id)

        # Add custom services and sort by 'id'
        services = list(services_dict.values())
        services.extend(custom_services)
        services.sort(key=lambda x: x["id"])
        return services
    except Exception as e:
        logging.error(f'Error fetching GCP services: {e}')
        return []


def main(custom_services_path: str):
    """
    Fetches GCP services and writes them to a JSON file.

    Args:
        custom_services_path: Path to the custom services JSON file.
    """
    services = fetch_gcp_services(custom_services_path)
    print(json.dumps(services, indent=4))


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Fetch GCP services.')
    parser.add_argument('--custom-services', dest='custom_services_path', default='custom-services/gcp.json',
                        help='Path to the custom services JSON file.')
    args = parser.parse_args()

    logging.basicConfig(level=logging.INFO)
    main(args.custom_services_path)
