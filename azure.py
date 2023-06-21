import requests
import json
import re
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
categories = soup.find_all('h2', class_=['product-category'])

replace_dict = {
    'QnA Maker': 'qnamaker',
    'Azure Data Lake Storage Gen1': 'data-lake-storage-gen1',
    'SDKs': 'sdk',
    'Azure Applied AI Services': 'applied-ai-services',
    'Azure Kubernetes Service Edge Essentials': 'kubernetes-service-edge-essentials',
}
services_dict = {}

for category in categories:
    category_id = 'azure/category/' + category['id']
    category_name = category.text
    print('processing category: ' + category_name)

    # get 3rd parent div
    category_div = category.find_parent('div').find_parent('div').find_parent('div')

    # find all div siblings with class 'row row-size2'
    matching_siblings = []
    current_sibling = category_div.find_next_sibling()

    # get all matching siblings while class is 'row row-size2' or 'row row-divided'
    while current_sibling and current_sibling.get('class') in [['row', 'row-divided'], ['row', 'row-size2']]:
        matching_siblings.append(current_sibling)
        current_sibling = current_sibling.find_next_sibling()

    # get all products from matching siblings
    products = []
    for sibling in matching_siblings:
        products.extend(sibling.find_all('h3'))

    for product in products:
        # get product name from <a><span>Product Name</span></a>
        product_name = product.find('span').text
        # get product url
        product_url = product.find('a')['href']
        if not product_url.startswith('https'):
            product_url = 'https://azure.microsoft.com' + product_url
        # get service name as everything in the href after '/products/' or '/services/'
        tokens = re.split('/products/|/services/|/features/', product.find('a')['href'])
        if len(tokens) > 1:
            token = tokens[1]
        else:
            token = product.find('a')['href'].split('/')[-2]
        # trim trailing slash
        if token[-1] == '/':
            token = token[:-1]
        # replace '/' with '-'
        token = token.replace('/', '-')
        # replace token if it's in the replace dict
        if product_name in replace_dict:
            token = replace_dict[product_name]

        product_id = token
        product_summary = product.find_next_sibling('p').text
        print('processing product: ' + product_name)

        if product_id not in services_dict:
            services_dict[product_id] = {
                'id': 'azure/' + product_id,
                'name': product_name,
                'summary': product_summary,
                'url': product_url,
                'categories': [{'id': category_id, 'name': category_name}],
                'tags': ['azure/platform', 'azure/service/' + product_id, category_id]
            }
        else:
            services_dict[product_id]['categories'].append({'id': category_id, 'name': category_name})
            services_dict[product_id]['tags'].append(category_id)

    # export to json array sorted by product id
    with open('data/azure.json', 'w') as outfile:
        services = list(services_dict.values())
        services.sort(key=lambda x: x['id'])
        json.dump(services, outfile, indent=4)

print('done')
