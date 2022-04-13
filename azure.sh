#!/bin/sh

set -e

echo "listing Azure services"

curl -s 'https://azure.microsoft.com/en-us/services/' \
  | pup ':parent-of(h3.text-heading5) json{}' \
  | jq -r '.[] | {"id": "azure/\(.children[0].children[0].href | split("/")[-2])", "name": .children[0].children[0].children[0].text, "summary": .children[1].text, "url": ("https://azure.microsoft.com" + .children[0].children[0].href)}' \
  | jq -n '. |= [inputs]' \
  | jq '.[] | . + {"tags": ["azure/platform", "azure/service/\(.id)"]}' \
  | jq -n '. |= [inputs]' > data/azure-services.json

curl -s 'https://azure.microsoft.com/en-us/services/' \
  | pup 'h2[id] json{}' | jq -r '.[] | {"id": .id, "name": .text}' \
  | jq -n '. |= [inputs]' > data/azure-categories.json

echo "-> manually remove '-headers' from azure-categories.json"
echo
echo "-> merge categories into azure.json following Azure service page"
echo
echo "-> replace service ids:"
echo "    Overview: qnamaker"
echo "    downloads: sdk"
echo "    aka.ms: applied-ai-services; fix url too"
echo "    data-lake-storage (2nd): data-lake-storage-gen1"
echo "    sql-server: sql-server-vm"
echo "    database: azure-sql-database"
echo "    edge: azure-sql-edge"
echo "    managed-instance: azure-sql-managed-instance"
echo "    edge(Stack): azure-stack-edge"
echo

echo "-> run the following command manually to recreate data/azure.json"
echo
echo "    jq '. | group_by(.id) | map(.[] + {(\"categories\"): map(.categories) | add}) | unique_by(.id)' data/azure-services.json | jq '.[] | . + {\"tags\": [\"azure/platform\", \"azure/service/\(.id)\",  \"azure/category/\(.categories[] | .id)\"]}' | jq -n '. |= [inputs]' > data/azure.j
son"


echo "done"
