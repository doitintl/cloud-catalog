# Public Cloud Services

Unfortunately, all cloud vendors do not provide a friendly API to list all public cloud services and categories, as listed on [AWS Products](https://aws.amazon.com/products), [GCP Products](https://cloud.google.com/products) and [Azure Services](https://azure.microsoft.com/en-us/services/) pages.

The idea is to have a unified `JSON` schema for all cloud services.

```json
{
  "$schema": "http://json-schema.org/draft-04/schema#",
  "type": "array",
  "items": [
    {
      "type": "object",
      "properties": {
        "id": {
          "type": "string"
        },
        "name": {
          "type": "string"
        },
        "summary": {
          "type": "string"
        },
        "url": {
          "type": "string"
        },
        "categories": {
          "type": "array",
          "items": [
            {
              "type": "object",
              "properties": {
                "id": {
                  "type": "string"
                },
                "name": {
                  "type": "string"
                }
              },
              "required": [
                "id",
                "name"
              ]
            }
          ]
        },
        "tags": {
          "type": "array",
          "items": [
            {
              "type": "string"
            }
          ]
        }
      },
      "required": [
        "id",
        "name",
        "summary",
        "url",
        "categories",
        "tags"
      ]
    }
  ]
}
```

## Scraping AWS Cloud Services

The AWS Products page uses **undocumented** `https://aws.amazon.com/api/dirs/items/search` endpoint to fetch paged JSON records for available cloud products.

```sh
# download AWS service JSON file and generate data/aws.json
pip install -r requirements.txt
python discovery/aws.py > data/aws.json
```

## Scraping GCP Cloud Services

The GCP Products page is rendered on the server side and all data is embedded into the web page.

```sh
# scrap GCP Products page to get all services and generate data/gcp.json
pip install -r requirements.txt
python discovery/gcp.py > data/gcp.json
```

## Scraping Azure Cloud Services

The [Azure Services](https://azure.microsoft.com/en-us/products/) page is rendered on the server side and all data is embedded into the web page.

```sh
# scrap Azure Services page to get all services and generate data/azure.json 
pip install -r requirements.txt
python discovery/azure.py > data/azure.json
```

## Microsoft365 Services

Edit the `ms365.json` file. Use data from this [page](https://www.microsoft.com/en-us/microsoft-365/compare-microsoft-365-enterprise-plans).

## Scraping Google Workspace Services (GSuite)

The [page](https://workspace.google.com/features/) page contains all Google Workspace services.

```sh
# scrap Google Workspace page to get all services and generate data/gsuite.json
pip install -r requirements.txt
python discovery/gsuite.py > data/gsuite.json
```

## CMP Services

Edit the `cmp.json` file. Use the CMP UI and documentation.

## Credits

Edit the `credits.json` file.

## Update/merge all tags

Run the `tags.sh` script to regenerate the `tags.json` file that contains all platform, category and services tags from all services.

## Public static location

Upload all generated `json` files to the public [cloud_tags](https://console.cloud.google.com/storage/browser/cloud_tags;tab=objects?forceOnBucketsSortingFiltering=false&project=zenrouter) Cloud Storage bucket.
