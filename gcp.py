import requests
import json
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

# handle categories
categories = soup.find_all('section', class_=['link-card-grid-section', 'cloud-jump-section'])
for category in categories:
    # get category id from <h2 id="category-id">Category Name</h2> child of <section> tag
    id = category.find('h2')['id']
    if id in skip_categories:
        continue
    category_id = 'gcp/category/' + id
    category_name = category.get('data-cloud-main-text')
    print('processing category: ' + category_name)

    # handle products within category
    # get all category_element children <a> tags with class 'cws-card'
    products = category.find_all('a', class_='cws-card')
    for product in products:
        # get track-metadata-child_headline attribute
        attr = product.get('track-metadata-child_headline')
        # trim ending whitespaces from the attribute value
        attr = attr.rstrip()
        # replace all '.' with '-'
        attr = attr.replace('.', '-')
        # replace all whitespaces with '-'
        attr = attr.replace(' ', '-')
        # construct product id
        product_id = attr
        # get product name from <div class="cws-headline">Product Name</div> child of <a> tag
        product_name = product.find('div', class_='cws-headline').text
        # get product url
        product_url = product['href']
        # add 'https://cloud.google.com' to product url if it doesn't start with 'https'
        if not product_url.startswith('https'):
            product_url = 'https://cloud.google.com' + product_url
        # get product summary from <div class="cws-body">Product Summary</div> child of <a> tag
        product_summary = product.find('div', class_='cws-body').text
        print('processing product: ' + product_name)

        if product_id not in services_dict:
            services_dict[product_id] = {
                'id': 'gcp/' + product_id,
                'name': product_name,
                'summary': product_summary,
                'url': product_url,
                'categories': [{'id': category_id, 'name': category_name}],
                'tags': ['gcp/platform', 'gcp/service/' + product_id, category_id]
            }
        else:
            services_dict[product_id]['categories'].append({'id': category_id, 'name': category_name})
            services_dict[product_id]['tags'].append(category_id)

    # add products from custom-services/gcp.json file
    with open('custom-services/gcp.json') as json_file:
        data = json.load(json_file)
        for product in data:
            product_id = product['id'].replace('gcp/', '')
            product_name = product['name']
            services_dict[product_id] = product
            print('processing product (json): ' + product_name)

    # export to json array sorted by product id
    with open('data/gcp.json', 'w') as outfile:
        services = list(services_dict.values())
        services.sort(key=lambda x: x['id'])
        json.dump(services, outfile, indent=4)

print('done')
