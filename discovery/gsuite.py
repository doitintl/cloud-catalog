import argparse
import json
import logging
import os
import requests
from bs4 import BeautifulSoup

GSUITE_PRODUCTS_URL = "https://workspace.google.com/features/"


def clean_string(s: str) -> str:
    """Cleans a string by removing whitespace and newlines."""
    clean = s.strip().replace("\n", "")
    clean = " ".join(clean.split())
    return clean


def id_from_name(name: str) -> str:
    """Converts a name to a URL-friendly ID."""
    return name.replace(" ", "-").replace(",", "").replace("&", "and").lower()


def id_from_label(label: str) -> str:
    """Converts a label to a URL-friendly ID."""
    return label.replace('connect: ', '').replace('google', '').\
        strip().replace(" ", "-").replace(",", "").replace("&", "and")


def fetch_gsuite_services(custom_services_path: str) -> list:
    """
    Fetches Google Workspace (GSuite) services.

    Args:
        custom_services_path: The path to the custom services JSON file.

    Returns:
        A list of dictionaries representing the services.
    """
    # Read custom services JSON file if it exists
    if os.path.exists(custom_services_path):
        with open(custom_services_path, "r") as f:
            custom_services = json.load(f)
    else:
        custom_services = []

    # Force US locale: need to pass Accept-Language header with US locale
    # and non US locale in order to get the US locale
    with requests.Session() as session:
        response = session.get(GSUITE_PRODUCTS_URL, headers={"Accept-Language": "en-US,en;q=0.5,de;q=0.3"})
        response.raise_for_status()

    soup = BeautifulSoup(response.content, 'lxml')
    replace_dict = {
        'Included applications': 'Applications',
    }
    summary_dict = {
        'admin-console': 'Manage Google Workspace for your organization.',
        'appsheet': 'Enable everyone in your organization to build and extend applications without coding.',
        'calendar': 'Business calendar and scheduling.',
        'endpoint': 'Endpoint management for Android, iOS, Windows, Chrome OS, MacOS, and Linux '
                    'is easy to set up and use.',
        'gmail': 'Custom business email.',
        'apps-script': 'Automate, integrate, and extend with Google Workspace.',
        'chat': 'Secure team messaging.',
        'cloud-search': 'Enterprise search for Google Workspace.',
        'docs': 'Collaborative text documents.',
        'drive': 'Cloud storage and file sharing.',
        'forms': 'Surveys and forms.',
        'jamboard': 'Interactive whiteboard.',
        'keep': 'Note taking.',
        'meet': 'Video conferencing.',
        'sheets': 'Collaborative spreadsheets.',
        'sites': 'Team sites.',
        'slides': 'Collaborative presentations.',
        'vault': 'Archiving and eDiscovery.',
        'voice': 'Cloud-based phone system.',
        'meet-hardware': 'Meet hardware brings the same reliable, easy-to-join video meeting experience of '
                         'Google Meet to the conference room.',
        'add-ons': 'Extend Google Workspace with apps that improve productivity.',
        'work-insights': 'Work Insights helps you understand how your organization uses Google Workspace tools.',
    }
    services_dict = {}

    # find all div without class under div with class _staticContent_1faic_23
    products_section = soup.find('div', class_='_staticContent_1faic_23')
    groups = products_section.find_all('div', class_=None)
    for group in groups:
        category = group.find('h2')
        category_name = clean_string(category.text)
        if category_name in replace_dict:
            category_name = replace_dict[category_name]
        category_id = id_from_name(category_name)
        category_id = f'gsuite/category/{category_id}'
        products = group.find_all('li', class_=None)
        for product in products:
            span = product.find('span')
            product_name = clean_string(span.text)
            link = product.find('a')
            product_url = link['href']
            if not product_url.startswith('https'):
                product_url = product_url.lstrip('../')
                product_url = f'https://workspace.google.com/{product_url}'
            product_id = id_from_label(link['data-g-label'])
            if product_id not in services_dict:
                services_dict[product_id] = {
                    'id': f'gsuite/{product_id}',
                    'name': product_name,
                    'summary': summary_dict.get(product_id, ''),
                    'url': product_url,
                    'categories': [{'id': category_id, 'name': category_name}],
                    'tags': ['gsuite/platform', f'gsuite/service/{product_id}', category_id]
                }
            else:
                services_dict[product_id]['categories'].append({'id': category_id, 'name': category_name})
                services_dict[product_id]['tags'].append(category_id)
    services = list(services_dict.values())
    services.extend(custom_services)
    services = sorted(services, key=lambda x: x['id'])
    return services


def main(custom_services_path: str) -> None:
    """
    Fetches Google Workspace (GSuite) services and prints them as a JSON string.

    Args:
        custom_services_path: The path to the custom services JSON file.
    """
    services = fetch_gsuite_services(custom_services_path)
    print(json.dumps(services, indent=4))


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Fetches Google Workspace services.')
    parser.add_argument('--custom-services', dest='custom_services_path', default='custom-services/gsuite.json',
                        help='Path to the custom services JSON file.')
    args = parser.parse_args()

    logging.basicConfig(level=logging.INFO)
    main(args.custom_services_path)
