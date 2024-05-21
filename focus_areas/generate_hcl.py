import json
import re

def main():
    hcl_dict = {}

    with open('../data/focus_areas/all.json', 'r') as f:
        focus_areas = json.load(f)
        for i in focus_areas:
            node = i['id'].replace('/', '::')
            if len(i['secondary_skills']) == 0:
                del(i['secondary_skills'])

            hcl_dict[node] = i

        json_string = json.dumps(hcl_dict, indent=2, separators=[",", "\t= "])

        hcl_string = re.sub('"(id|practice_area|name|primary_skills|secondary_skills)"', '\\1', json_string)
        print(hcl_string)


if __name__ == '__main__':
    main()
