#!/bin/sh

set -e

echo "listing AWS services"
CUSTOM_SERVICES=$(cat custom-services/aws.json)

curl -s 'https://aws.amazon.com/api/dirs/items/search?item.directoryId=aws-products&sort_by=item.additionalFields.productCategory&sort_order=asc&size=500&item.locale=en_US&tags.id=!aws-products%23type%23feature&tags.id=!aws-products%23type%23variant' \
  | jq -r '.items[]
            | {
                "id": "aws/\(.item.name)",
                "name": .item.additionalFields.productName,
                "summary": .item.additionalFields.productSummary,
                "url": .item.additionalFields.productUrl,
                "categories":
                  [
                    .tags[]
                    | select(.tagNamespaceId=="GLOBAL#tech-category")
                    | {
                        "id": (.name | gsub(" "; "-") | gsub(","; "") | gsub("&"; "and") | ascii_downcase),
                        "name": .description
                      }
                  ] | sort_by(.id),
                "tags": 
                  (
                    [
                      "aws/platform",
                      "aws/service/\(.item.name)"
                     ] + 
                     (
                       [
                         "aws/category/\(.tags[] | select(.tagNamespaceId=="GLOBAL#tech-category") | .name | gsub(" "; "-") | gsub(","; "") | gsub("&"; "and") | ascii_downcase)"
                       ] | sort
                     )
                   )
              }' \
  | jq -n '. |= [inputs]' \
  | jq -r ". += $CUSTOM_SERVICES" \
  | jq -r 'sort_by(.id)' > data/aws.json

# fix wrong category descriptions
sed -i.bak 's/<p>containers<\/p>\\r\\n/Containers/g' data/aws.json
sed -i.bak 's/<p>media-services<\/p>\\r\\n/Media Services/g' data/aws.json
sed -i.bak 's/<p>Quantum Technologies<\/p>\\r\\n/Quantum Technologies/g' data/aws.json
sed -i.bak 's/<p>Empower your organization with Alexa<\/p>\\r\\n/Empower your organization with Alexa/g' data/aws.json
sed -i.bak 's/<p>Build mobile &amp; web apps without programming<\/p>\\r\\n/Build mobile web apps without programming/g' data/aws.json

# cleanup url
sed -i.bak 's/\/?did=ap_card&trk=ap_card//g' data/aws.json
rm -f data/aws.json.bak

echo "done"
