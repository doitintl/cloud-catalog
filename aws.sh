#!/bin/sh

set -e

echo "listing AWS services"

curl -s 'https://aws.amazon.com/api/dirs/items/search?item.directoryId=aws-products&sort_by=item.additionalFields.productCategory&sort_order=asc&size=500&item.locale=en_US&tags.id=!aws-products%23type%23feature&tags.id=!aws-products%23type%23variant' \
  | jq -r '.items[] | {"id": .item.name, "name": .item.additionalFields.productName, "summary": .item.additionalFields.productSummary, "url": .item.additionalFields.productUrl, "categories": [.tags[] | select(.tagNamespaceId=="GLOBAL#tech-category") | {"id": .name, "name": .description}], "tags": ["aws/platform", "aws/service/\(.item.name)", "aws/category/\(.tags[] | select(.tagNamespaceId=="GLOBAL#tech-category") | .name)"] }' \
  | jq -n '. |= [inputs]' > data/aws.json

# fix wrong category descriptions
sed -i.bak 's/<p>containers<\/p>\\r\\n/Containers/g' data/aws.json
sed -i.bak 's/<p>media-services<\/p>\\r\\n/Media Services/g' data/aws.json
sed -i.bak 's/<p>Quantum Technologies<\/p>\\r\\n/Quantum Technologies/g' data/aws.json

# cleanup url
sed -i.bak 's/\/?did=ap_card&trk=ap_card//g' data/aws.json
rm -f data/aws.json.bak

echo "done"
