#!/bin/sh

set -e

jq -r '.[] | .tags ' data/aws.json data/gcp.json | jq -s 'add | unique | sort' > data/tags.json