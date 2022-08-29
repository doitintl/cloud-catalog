#!/bin/sh

set -eu

OTHER_JSON=$(cat <<'EOF'
 {
	"id": "gcp/other",
	"name": "Other",
	"summary": "Other GCP services.",
	"url": "",
	"categories": [
		{
			"id": "other",
			"name": "Other"
		}
	],
	"tags": ["gcp/platform"]
}
EOF
)

echo "listing GCP services"

curl -s 'https://cloud.google.com/products/' \
  | pup 'a.cws-card json{}' \
  | jq -r '.[] | {"id": ("gcp/" + ."track-name" | gsub(" ";"-")), "name": .children[0].children[0].children[0].text, "summary": .children[0].children[0].children[1].text, "url": .href, "categories": [{"id": (."track-metadata-module_headline" | gsub(" ";"-")), "name": ."track-metadata-module_headline"}]}' \
  | jq -n '. |= [inputs]' \
  | jq '. | group_by(.id) | map(.[] + {("categories"): map(.categories) | add}) | unique_by(.id)' \
  | jq '.[] | . + {"tags": ["gcp/platform", ("gcp/service/" + .id | sub("/gcp/"; "/")), "gcp/category/\(.categories[] | .id)"]}' \
  | jq -n '. |= [inputs]' \
  | jq -r ". += [$OTHER_JSON]" \
  | jq -r 'sort_by(.id)' > data/gcp.json

echo "done"
