import requests
import json
from bs4 import BeautifulSoup

pages = [
    "https://firebase.google.com/products-build",
    "https://firebase.google.com/products-release",
    "https://firebase.google.com/products-engage"
]

output_data = []

for page in pages:
    response = requests.get(page)
    soup = BeautifulSoup(response.text, 'html.parser')
    divs = soup.select('div.product-grid__content')

    for div in divs:
        item = {}
        a_tag = div.select_one("a")
        p_tag = div.select_one("p")

        href = a_tag.get("href", "")
        item_id = a_tag.get("href", "").replace("/products/", "").replace("firebase", "").lstrip("-")

        item["id"] = f"gcp/firebase-{item_id}"
        item["name"] = a_tag.text.replace("\n", "").strip().replace("                         ", "-")
        item["summary"] = p_tag.text.strip()
        item["url"] = href if href.startswith("https://") else f"https://firebase.google.com{href}"
        item["categories"] = [{"id": "firebase", "name": "Firebase"}]
        item["tags"] = [
            "gcp/platform",
            "gcp/category/firebase",
            f"gcp/service/firebase-{item_id}"
        ]

        output_data.append(item)

# Remove duplicates and sort by id
output_data = sorted({d['id']: d for d in output_data}.values(), key=lambda x: x['id'])

with open("data/gcp-firebase.json", "w") as f:
    json.dump(output_data, f, indent=4)

print("done")