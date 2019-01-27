from image import Image
from jinja2 import Environment, FileSystemLoader
import json
import os
import shutil

class Category:
    def __init__(self, name, pretty_name, images):
        self.name = name
        self.pretty_name = pretty_name

        # If initialize the category with one image, make a list
        # and put it in
        if isinstance(images, Image):
            self.images = []
            self.images.append(images)
        # Otherwise, just set the internal list to the input list
        elif isinstance(images, list):
            self.images = images

    def add_image(self, image):
        self.images.append(image)

    def make_thumbnail_folder(self, output_root_dir):
        category_dir = os.path.join(output_root_dir, self.name)
        os.makedirs(category_dir, exist_ok=True)

        # Copy all the images into the category directory
        for image in self.images:
            shutil.copy(image.thumbnail_path, category_dir)

    # For each category, render an HTML page
    def generate_html(self, template_dir, sorted_categories):
        env = Environment(loader=FileSystemLoader(template_dir))
        template = env.get_template('gallery_template.html')

        output_from_parsed_template = template.render(
                current_category=self,
                categories=sorted_categories)

        # Write out the HTML file
        html_file = '{}.html'.format(self.name)
        with open(html_file, 'w') as f:
            f.write(output_from_parsed_template)
