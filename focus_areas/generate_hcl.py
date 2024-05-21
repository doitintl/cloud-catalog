import json

def main():
    hcl_dict = {}

    with open('../data/focus_areas/all.json', 'r') as f:
        focus_areas = json.load(f)
        for i in focus_areas:
            node = i['id'].replace('/', '::')
            hcl_dict[node] = i

        print(json.dumps(hcl_dict, indent=2, separators=[",", " = "]))


if __name__ == '__main__':
    main()