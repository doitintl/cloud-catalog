#!/bin/sh

set -e

echo "listing Workspace services"
CUSTOM_SERVICES=$(cat custom-services/gsuite.json)

curl -s 'https://cloud.google.com/products/' \
  | pup 'a.cws-card json{}' \
  | jq -r '.[]
          # workspace services only
          | select(.href | startswith("https://workspace.google.com"))

          # drop workspace itself
          | select(."track-name" != "google workspace")

          # drop workspace essentials, we have those more detailed in custom-services
          | select(."track-name" != "google workspace essentials")

          | {
              "id": ("gsuite/" + ."track-name" | gsub(" ";"-")),
              "name": .children[0].children[0].children[0].text,
              "summary": .children[0].children[0].children[1].text,
              "url": (if .href | startswith("https://") then .href else "https://cloud.google.com" + .href end),
              "categories":
              [
                {
                  "id": ("gsuite/" + ."track-metadata-module_headline" | gsub(" ";"-")),
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
                "gsuite/platform",
                ("gsuite/service/" + .id | sub("/gsuite/"; "/"))
              ] + 
              (
                ["gsuite/category/\(.categories[] | (.id | sub("gsuite/"; "")))"] | sort
              )
            )
          }' \
  | jq -n '. |= [inputs]' \
  | jq -r ". += $CUSTOM_SERVICES" \
  | jq -r 'sort_by(.id)' > data/gsuite.json

echo "done"
