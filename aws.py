import json
import requests

# Read custom services JSON file
with open("custom-services/aws.json", "r") as f:
    custom_services = json.load(f)

# Download JSON data
url = 'https://aws.amazon.com/api/dirs/items/search?' \
    'item.directoryId=aws-products&' \
    'sort_by=item.additionalFields.productCategory&' \
    'sort_order=asc&' \
    'size=1000&' \
    'item.locale=en_US&' \
    'tags.id=!aws-products%23type%23feature&' \
    'tags.id=!aws-products%23type%23variant'
response = requests.get(url)
data = response.json()

# Create a new JSON array
new_data = []
for item in data["items"]:
    categories = sorted(
        [
            {
                "id": tag["name"].replace(" ", "-").replace(",", "").replace("&", "and").lower(),
                "name": tag["description"]
            }
            for tag in item["tags"]
            if tag["tagNamespaceId"] == "GLOBAL#tech-category"
        ],
        key=lambda x: x["id"],
    )

    tags = [
            "aws/platform",
            f"aws/service/{item['item']['name']}",
            *[
                f"aws/category/{tag['name'].replace(' ', '-').replace(',', '').replace('&', 'and').lower()}"
                for tag in item["tags"]
                if tag["tagNamespaceId"] == "GLOBAL#tech-category"
            ],
        ]

    summary = item["item"]["additionalFields"]["productSummary"]
    summary = summary.replace("<p>", "").replace("</p>", "").replace("\n", "").replace("\r", "")

    new_item = {
        "id": f"aws/{item['item']['name']}",
        "name": item["item"]["additionalFields"]["productName"],
        "summary": summary,
        "url": item["item"]["additionalFields"]["productUrl"].replace("/?did=ap_card&trk=ap_card", ""),
        "categories": categories,
        "tags": tags,
    }
    new_data.append(new_item)

# Add custom services and sort by 'id'
new_data.extend(custom_services)
new_data.sort(key=lambda x: x["id"])

# Write the final JSON array to a file
with open("data/aws.json", "w") as f:
    json.dump(new_data, f, ensure_ascii=False, indent=4)

print("done")
