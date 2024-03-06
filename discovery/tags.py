import json

# List of input JSON files
input_files = [
    "data/aws.json",
    "data/gcp.json",
    "data/cmp.json",
    "data/gsuite.json",
    "data/ms365.json",
    "data/azure.json",
    "data/finance.json",
    "data/credits.json",
    "data/cre.json",
    "data/gcp-firebase.json"
]

all_tags = []

# Loop through each file to collect all tags
for file in input_files:
    with open(file, 'r') as f:
        data = json.load(f)
        for item in data:
            if 'tags' in item:
                all_tags.extend(item['tags'])

# Remove duplicates and sort
all_tags = sorted(set(all_tags))

# Save to output file
with open("data/tags.json", 'w') as f:
    json.dump(all_tags, f, indent=4)

print("done")