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

def copy_to_folder(json_data, original_dir, output_dir):
    # Copy the files into the subfolder
    for key in json_data:
        image_json = json_data[key]
        image_path = os.path.join(original_dir, image_json['thumbnail_path'])
        shutil.copy(image_path, output_dir)

# Save the new JSON file
def generate_json_file(filename, output_dir, json_data):
    json_filename = '{}.json'.format(filename)
    json_path = os.path.join(output_dir, json_filename)
    with open(json_path, 'w') as outfile:
        json.dump(json_data, outfile)

def make_category_folder(category, root_dir, json_images):
    category_dir = os.path.join(root_dir, category)
    os.makedirs(category_dir, exist_ok=True)
    copy_to_folder(json_images, root_dir, category_dir)
    generate_json_file(category, root_dir, json_images)

def main():
    args = parse_arguments()
    input_json = args.input_json
    output_root_dir = args.output_root_dir

    json_data = json.load(open(input_json))

    # Make a JSON file for all of the images
    make_category_folder('All', output_root_dir, json_data)

    # Copy the images into folders for each of their keywords
    keywords = get_keywords(json_data)
    for keyword in keywords:
        # Filter the JSON file by images that match the keyword
        keyword_json_data = { key: json_data[key] for key in json_data if keyword in json_data[key]['tags'] }
        make_category_folder(keyword, output_root_dir, keyword_json_data)

    # Make a category for n most recent images - for homepage
    time_sorted_list = sorted(json_data, key=lambda j: json_data[j]['date'], reverse=True)
    recent_count = 30
    time_sorted_list = time_sorted_list[:recent_count]
    time_sorted_json = { }
    for key in time_sorted_list:
        time_sorted_json[key] = json_data[key]

    make_category_folder('Recent', output_root_dir, time_sorted_json)

if __name__ == "__main__":
    main()
