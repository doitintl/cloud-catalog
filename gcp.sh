#!/bin/sh

set -e

echo "listing GCP services"

curl -s 'https://cloud.google.com/products/' \
  | pup 'a.cws-card json{}' \
  | jq -r '.[]
          | {
              "id": ("gcp/" + ."track-name" | gsub(" ";"-")),
              "name": .children[0].children[0].children[0].text,
              "summary": .children[0].children[0].children[1].text,
              "url": (if .href | startswith("https://cloud.google.com/") then .href else "https://cloud.google.com" + .href end),
              "categories":
              [
                {
                  "id": (."track-metadata-module_headline" | gsub(" ";"-")),
                  "name": ."track-metadata-module_headline"
                }
              ]
            }' \
  | jq -n '. |= [inputs]' \
  | jq '. | group_by(.id) | map(.[] + {("categories"): map(.categories) | add}) | unique_by(.id)' \
  | jq '.[] 
        | . +
          {
            "tags":
            (
              [
                "gcp/platform",
                ("gcp/service/" + .id | sub("/gcp/"; "/"))
              ] + 
              (
                ["gcp/category/\(.categories[] | .id)"] | sort
              )
            )
          }' \
  | jq -n '. |= [inputs]' \
  | jq -r 'sort_by(.id)' > data/gcp.json

echo "done"
