#!/bin/sh

set -e

jq -r '.[] | .tags ' data/aws.json data/gcp.json data/cmp.json data/gsuite.json data/ms365.json data/azure.json | jq -s 'add | unique | sort' > data/tags.json