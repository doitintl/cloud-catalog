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

## Scrapping AWS Cloud Services

The AWS Products page uses **undocumented** `https://aws.amazon.com/api/dirs/items/search` endpoint to fetch paged JSON records for available cloud products.

With a combination of [curl](https://curl.se/), [jq](https://stedolan.github.io/jq/) and [sed](https://www.gnu.org/software/sed/manual/sed.html) commands, it is possible to extract the required information.

```sh
./aws.sh
```

```json
[
  //...,
  {
    "id": "aws/amazon-eventbridge",
    "name": "Amazon EventBridge",
    "summary": "Serverless event bus for SaaS apps & AWS services",
    "url": "https://aws.amazon.com/eventbridge",
    "categories": [
      {
        "id": "serverless",
        "name": "Serverless"
      },
      {
        "id": "app-integration",
        "name": "Application Integration"
      }
    ],
    "tags": [
      "aws/service/amazon-eventbridge",
      "aws/category/serverless",
      "aws/category/app-integration"
    ]
  },
  //...
]
```

## Scrapping GCP Cloud Services

The GCP Products page is rendered on the server side and all data is embedded into the web page.

With the combination of [curl](https://curl.se/), [jq](https://stedolan.github.io/jq/) and [pup](https://github.com/ericchiang/pup) commands it is possible to extract the required information.

```sh
./gcp.sh
```

```json
[
  //...,
  {
    "id": "gcp/app-engine",
    "name": "App Engine",
    "summary": "Serverless application platform for apps and back ends.",
    "url": "https://cloud.google.com/appengine",
    "categories": [
      {
        "id": "compute",
        "name": "compute"
      },
      {
        "id": "serverless-computing",
        "name": "serverless computing"
      }
    ],
    "tags": [
      "gcp/service/app-engine",
      "gcp/category/compute",
      "gcp/category/serverless-computing"
    ]
  },
  //...
]
```

## Scrapping Azure Cloud Services

The [Azure Services](https://azure.microsoft.com/en-us/services/) page is rendered on the server side and all data is embedded into the web page.

Currently, service scrapping is done half-automated.

The combination of [curl](https://curl.se/), [jq](https://stedolan.github.io/jq/) and [pup](https://github.com/ericchiang/pup) commands allows extracting services and categories from the page. Unfortunately, correlating services to categories, using the above tools, is not an easy task. So, the process incudes manual steps.

```sh
# run
./azure.sh

# output: azure-services.json and azure-categories.json

# follow manual steps displayed by the script
# generate azure.json file

```

## Microsoft365 Services

Edit the `ms365.json` file. Use data from this [page](https://www.microsoft.com/en-us/microsoft-365/compare-microsoft-365-enterprise-plans).

## Google Workspace Services (GSuite)

Edit the `gsuite.json` file. use data from this [page](https://workspace.google.com/features/).

## CMP Services

Edit the `cmp.json` file. Use the CMP UI and documentation.

## Update/merge all tags

Run the `tags.sh` script to regenerate the `tags.json` file that contains all platform, category and services tags from all services.

## Public static location

Upload all generated `json` files to the public [cloud_tags](https://console.cloud.google.com/storage/browser/cloud_tags;tab=objects?forceOnBucketsSortingFiltering=false&project=zenrouter) Cloud Storage bucket.
