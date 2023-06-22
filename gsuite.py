import json
import requests
from bs4 import BeautifulSoup


def clean_string(s):
    # trip prefix and suffix whitespaces, remove newlines
    clean = s.strip().replace("\n", "")
    # remove multiple whitespaces
    clean = " ".join(clean.split())
    return clean


def id_from_name(name):
    return name.replace(" ", "-").replace(",", "").replace("&", "and").lower()


def id_from_label(label):
    return label.replace('connect: ', '').replace('google', '').strip().replace(" ", "-").replace(",", "").replace("&", "and")


url = "https://workspace.google.com/features/"
# force US locale: need to pass Accept-Language header with US locale and non US locale in order to get the US locale
response = requests.get(url, headers={"Accept-Language": "en-US,en;q=0.5,de;q=0.3"})

if response.status_code == 200:
    html_content = response.text
    print("Successfully fetched the page")
else:
    print("Failed to fetch the page")
    exit()

soup = BeautifulSoup(html_content, 'lxml')
replace_dict = {
    'Included applications': 'Applications',
}
summary_dict = {
    'admin-console': 'Manage Google Workspace for your organization.',
    'appsheet': 'Enable everyone in your organization to build and extend applications without coding.',
    'calendar': 'Business calendar and scheduling.',
    'endpoint': 'Endpoint management for Android, iOS, Windows, Chrome OS, MacOS, and Linux is easy to set up and use.',
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
    'meet-hardware': 'Meet hardware brings the same reliable, easy-to-join video meeting experience of Google Meet to '
                     'the conference room.',
    'add-ons': 'Extend Google Workspace with apps that improve productivity.',
    'work-insights': 'Work Insights helps you understand how your organization uses Google Workspace tools.',
}
services_dict = {}

groups = soup.find_all('article', class_='tools-group')
for group in groups:
    category = group.find('div', class_='tools-group--title')
    category_name = clean_string(category.text)
    if category_name in replace_dict:
        category_name = replace_dict[category_name]
    category_id = id_from_name(category_name)
    category_id = f'gsuite/category/{category_id}'
    print(f'processing category: {category_name}')
    products = group.find_all('li', class_='tools-group--product')
    for product in products:
        span = product.find('span', class_='tools-group--product__name')
        product_name = clean_string(span.text)
        link = product.find('a')
        product_url = link['href']
        if not product_url.startswith('https'):
            product_url = product_url.lstrip('../')
            product_url = f'https://workspace.google.com/{product_url}'
        product_id = id_from_label(link['data-g-label'])
        print(f'processing product: {product_name}')
        if product_id not in services_dict:
            services_dict[product_id] = {
                'id': f'gsuite/{product_id}',
                'name': product_name,
                'summary': summary_dict.get(product_id, ''),
                'url': product_url,
                'categories': [{'id': category_id, 'name': category_name}],
                'tags': [f'gsuite/platform', f'gsuite/service/{product_id}', category_id]
            }
        else:
            services_dict[product_id]['categories'].append({'id': category_id, 'name': category_name})
            services_dict[product_id]['tags'].append(category_id)

with open('data/gsuite.json', 'w') as outfile:
    services = list(services_dict.values())
    services.sort(key=lambda x: x['id'])
    json.dump(services, outfile, indent=4)

print("done")
