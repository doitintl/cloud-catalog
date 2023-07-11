#!/usr/bin/env bash

set -ex

# Add additional files to parse in the below array
INPUTS=()
INPUTS+=("aws.json")
INPUTS+=("gcp.json")
INPUTS+=("cmp.json")
INPUTS+=("gsuite.json")
INPUTS+=("ms365.json")
INPUTS+=("azure.json")
INPUTS+=("finance.json")
INPUTS+=("credits.json")
INPUTS+=("cre.json")

ROOTDIR=$(dirname $(dirname $(readlink -f "${BASH_SOURCE[0]}")))
DATADIR="$ROOTDIR/data"

jq -r '.[] | .tags' ${INPUTS[@]/#/$DATADIR/} | jq -s 'add | unique | sort' > "$DATADIR/tags.json"
