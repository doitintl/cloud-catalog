import json
import requests
from bs4 import BeautifulSoup

url = "https://cloud.google.com/products/"
response = requests.get(url)

if response.status_code == 200:
    html_content = response.text
    print("Successfully fetched the page")
else:
    print("Failed to fetch the page")
    exit()

soup = BeautifulSoup(html_content, 'lxml')

services_dict = {}
skip_categories = ['featured-products', 'additional-google-products']
skip_products = ['google-workspace-essentials']

categories = soup.find_all('section', class_=['link-card-grid-section', 'cloud-jump-section'])
for category in categories:
    category_id = category.find('h2')['id']
    if category_id in skip_categories:
        continue
    category_id = f'gcp/category/{category_id}'
    category_name = category.get('data-cloud-main-text')
    print(f'processing category: {category_name}')

    products = category.find_all('a', class_='cws-card')
    for product in products:
        product_id = product.get('track-metadata-child_headline').rstrip().replace('.', '-').replace(' ', '-')
        if product_id in skip_products:
            continue
        product_name = product.find('div', class_='cws-headline').text
        product_url = product['href']
        if not product_url.startswith('https'):
            product_url = f'https://cloud.google.com{product_url}'
        product_summary = product.find('div', class_='cws-body').text
        print(f'processing product: {product_name}')

        if product_id not in services_dict:
            services_dict[product_id] = {
                'id': f'gcp/{product_id}',
                'name': product_name,
                'summary': product_summary,
                'url': product_url,
                'categories': [{'id': category_id, 'name': category_name}],
                'tags': [f'gcp/platform', f'gcp/service/{product_id}', category_id]
            }
        else:
            services_dict[product_id]['categories'].append({'id': category_id, 'name': category_name})
            services_dict[product_id]['tags'].append(category_id)

with open('custom-services/gcp.json') as json_file:
    custom_data = json.load(json_file)
    for product in custom_data:
        product_id = product['id'].replace('gcp/', '')
        product_name = product['name']
        services_dict[product_id] = product
        print(f'processing product (json): {product_name}')

with open('data/gcp.json', 'w') as outfile:
    services = list(services_dict.values())
    services.sort(key=lambda x: x['id'])
    json.dump(services, outfile, indent=4)

print('done')