import json
import re
import requests
from bs4 import BeautifulSoup

url = "https://azure.microsoft.com/en-us/products/"
response = requests.get(url)
if response.status_code == 200:
    html_content = response.text
    print("Successfully fetched the page")
else:
    print("Failed to fetch the page")
    exit()

soup = BeautifulSoup(html_content, 'lxml')
replace_dict = {
    'QnA Maker': 'qnamaker',
    'Azure Data Lake Storage Gen1': 'data-lake-storage-gen1',
    'SDKs': 'sdk',
    'Azure Applied AI Services': 'applied-ai-services',
    'Azure Kubernetes Service Edge Essentials': 'kubernetes-service-edge-essentials',
}
services_dict = {}

categories = soup.find_all('h2', class_=['product-category'])
for category in categories:
    category_id = f'azure/category/{category["id"]}'
    category_name = category.text
    print(f'processing category: {category_name}')
    category_div = category.find_parent('div').find_parent('div').find_parent('div')
    matching_siblings = []
    current_sibling = category_div.find_next_sibling()
    while current_sibling and current_sibling.get('class') in [['row', 'row-divided'], ['row', 'row-size2']]:
        matching_siblings.append(current_sibling)
        current_sibling = current_sibling.find_next_sibling()
    products = []
    for sibling in matching_siblings:
        products.extend(sibling.find_all('h3'))
    for product in products:
        product_name = product.find('span').text
        product_url = product.find('a')['href']
        if not product_url.startswith('https'):
            product_url = f'https://azure.microsoft.com{product_url}'
        tokens = re.split('/products/|/services/|/features/', product.find('a')['href'])
        token = tokens[1] if len(tokens) > 1 else product.find('a')['href'].split('/')[-2]
        token = token.rstrip('/').replace('/', '-')
        product_id = replace_dict.get(product_name, token)
        product_summary = product.find_next_sibling('p').text
        print(f'processing product: {product_name}')
        if product_id not in services_dict:
            services_dict[product_id] = {
                'id': f'azure/{product_id}',
                'name': product_name,
                'summary': product_summary,
                'url': product_url,
                'categories': [{'id': category_id, 'name': category_name}],
                'tags': [f'azure/platform', f'azure/service/{product_id}', category_id]
            }
        else:
            services_dict[product_id]['categories'].append({'id': category_id, 'name': category_name})
            services_dict[product_id]['tags'].append(category_id)

with open('data/azure.json', 'w') as outfile:
    services = list(services_dict.values())
    services.sort(key=lambda x: x['id'])
    json.dump(services, outfile, indent=4)

print('done')
