import argparse, glob, json, os, shutil

def parse_arguments():
    parser = argparse.ArgumentParser()
    parser.add_argument('--input_json', help='Input json file', dest='input_json', required=True)
    parser.add_argument('--output_root_dir', help='Output dir', dest='output_root_dir', required=True)
    args = parser.parse_args()
    return args

def get_keywords(json_data):
    # Get all the keywords
    keywords = []
    for key in json_data:
        image_json = json_data[key]
        for tag in image_json['tags']:
            if tag not in keywords:
                keywords.append(tag)
    keywords.remove('Website')
    print(keywords)
    return keywords

def main():
    args = parse_arguments()
    input_json = args.input_json
    output_root_dir = args.output_root_dir

    json_data = json.load(open(input_json))
    keywords = get_keywords(json_data)

    # Copy the images into new folders, generate new JSON files
    for keyword in keywords:
        keyword_dir = os.path.join(output_root_dir, keyword)
        os.makedirs(keyword_dir, exist_ok=True)

        # Select the JSON data
        new_json_data = { }
        for key in json_data:
            image_json = json_data[key]
            if keyword in image_json['tags']:
                new_json_data[key] = image_json

        # Copy the files into the subfolder
        for key in json_data:
            image_json = json_data[key]
            image_path = os.path.join(output_root_dir, image_json['thumbnail_path'])
            shutil.copy(image_path, keyword_dir)

        # Save the new JSON file
        json_filename = '{}.json'.format(keyword)
        json_path = os.path.join(output_root_dir, json_filename)
        with open(json_path, 'w') as outfile:
            json.dump(new_json_data, outfile)

    # TODO: Make a JSON file for all images
    # TODO: Make a JSON file for 30 most recent images (for homepage)

if __name__ == "__main__":
    main()
