"""
This module fetches AWS services from the AWS Products Directory API and returns a list of services.
"""
import argparse
from bs4 import BeautifulSoup
from bs4 import MarkupResemblesLocatorWarning
import json
import logging
import os
import requests
import warnings


AWS_PRODUCTS_API = 'https://aws.amazon.com/api/dirs/items/search'
MAX_AWS_SERVICES = 1000


def clean_string(s: str) -> str:
    """
    Cleans a string by replacing spaces, commas, and ampersands with hyphens and converting it to lowercase.

    Args:
        s: The string to clean.

    Returns:
        The cleaned string.
    """
    return s.replace(" ", "-").replace(",", "").replace("&", "and").lower()


def clean_summary(s: str) -> str:
    """
    Cleans a summary by removing HTML tags, newlines, and carriage returns.

    Args:
        s: The summary to clean.

    Returns:
        The cleaned summary.
    """
    if not s:
        return ""
    return BeautifulSoup(s, "lxml").get_text().replace("\n", "").replace("\r", "").strip()


def fetch_aws_services(custom_services_path: str = "custom-services/aws.json") -> list:
    """
    Fetches AWS services from the AWS Products Directory API and returns a list of services.

    Args:
        custom_services_path: The path to the custom services JSON file.

    Returns:
        A list of AWS services.
    """
    try:
        # Read custom services JSON file if it exists
        if os.path.exists(custom_services_path):
            with open(custom_services_path, "r") as f:
                custom_services = json.load(f)
        else:
            custom_services = []

        # Download JSON data
        params = {
            'item.directoryId': 'aws-products',
            'sort_by': 'item.additionalFields.productCategory',
            'sort_order': 'asc',
            'size': MAX_AWS_SERVICES,
            'item.locale': 'en_US',
            'tags.id': ['!aws-products#type#feature', '!aws-products#type#variant']
        }
        with requests.Session() as session:
            response = session.get(AWS_PRODUCTS_API, params=params)
            response.raise_for_status()
        data = response.json()

        services = []
        for item in data["items"]:
            categories = sorted(
                [
                    {
                        "id": clean_string(tag["name"]),
                        "name": tag["description"]
                    }
                    for tag in item["tags"]
                    if tag["tagNamespaceId"] == "GLOBAL#tech-category"
                ],
                key=lambda x: x["id"],
            )
            if len(categories) == 0:
                category = item["item"]["additionalFields"]["productCategory"]
                categories = [
                    {
                        "id": clean_string(category),
                        "name": category
                    }
                ]

            tags = sorted(
                [
                    "aws/platform",
                    clean_string(f"aws/service/{item['item']['name']}"),
                    *[
                        f"aws/category/{category['id']}"
                        for category in categories
                    ],
                ]
            )

            summary = item["item"]["additionalFields"]["productSummary"]
            summary = clean_summary(summary)

            service = {
                "id": clean_string(f"aws/{item['item']['name']}"),
                "name": item["item"]["additionalFields"]["productName"],
                "summary": summary,
                "url": item["item"]["additionalFields"]["productUrl"].replace("/?did=ap_card&trk=ap_card", ""),
                "categories": categories,
                "tags": tags,
            }
            services.append(service)

        # Add custom services and sort by 'id'
        services.extend(custom_services)
        services.sort(key=lambda x: x["id"])
        return services
    except Exception as e:
        logging.error(f"Failed to fetch AWS services: {e}")
        return []


def main(custom_services_path: str) -> None:
    """
    Fetches AWS services and prints them to the console.
    """
    warnings.filterwarnings("ignore", category=MarkupResemblesLocatorWarning)
    services = fetch_aws_services(custom_services_path)
    print(json.dumps(services, indent=4))


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Fetches AWS services.')
    parser.add_argument('--custom-services', dest='custom_services_path', default='custom-services/aws.json',
                        help='Path to the custom services JSON file.')
    args = parser.parse_args()

    logging.basicConfig(level=logging.INFO)
    main(args.custom_services_path)
