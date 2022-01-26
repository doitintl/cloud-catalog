# Public Cloud Services

Currently, AWS and GCP do not provide a friendly API to list all public cloud services and categories, as listed on [AWS Products](https://aws.amazon.com/products) and [GCP Products](https://cloud.google.com/products) pages.

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
    "id": "amazon-eventbridge",
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

With the combination of  [curl](https://curl.se/), [jq](https://stedolan.github.io/jq/) and [pup](https://github.com/ericchiang/pup) commands it is possible to extract the required information.

```sh
./gcp.sh
```

```json
[
  //...,
  {
    "id": "app-engine",
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
