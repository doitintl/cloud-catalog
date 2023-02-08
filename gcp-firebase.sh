#!/bin/sh

set -e

echo "listing Firebase services"

pages=(
  https://firebase.google.com/products-build
  https://firebase.google.com/products-release
  https://firebase.google.com/products-engage
)

printf "%s\n" "${pages[@]}" \
    | xargs -t -n 1 bash -c 'curl -s $1 | pup "div.product-grid__content json{}"' _ \
    | jq -r '.[]
             | {
                  "id": ("gcp/firebase-" + .children[0].children[0].id | gsub(" ";"-")),
                  "name": .children[0].children[0].children[0].text,
                  "summary": .children[1].children[0].text,
                  "url": (
                    if (.children[0].children[0].children[0].href | startswith("https://") ) then
                      .children[0].children[0].children[0].href
                    else
                      "https://firebase.google.com" + .children[0].children[0].children[0].href
                    end
                  ),
                  "categories": [
                    {
                      "id": "firebase",
                      "name": "Firebase"
                    }
                  ],
                  "tags": [
                    "gcp/platform",
                    "gcp/category/firebase",
                    (
                      "gcp/service/firebase-" + (
                        .children[0].children[0].id
                          | gsub(" ";"-")
                          | gsub("firebase";"")
                          | sub("^-";"")
                      )
                    )
                  ]
               }' \
    | jq -n '. |= [inputs]' \
    | jq 'unique_by(.id) | sort_by(.id)' \
    > data/gcp-firebase.json

echo "done"
