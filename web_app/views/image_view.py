from web_app import app
from web_app.models import Album, Image
from flask import render_template

class ImageView():
    @app.route('/images/<int:image_id>')
    def get_image(image_id):
        image = Image.query.get(image_id)
        albums = Album.query.all()
        return render_template('image.html', image=image, albums=albums)

    @app.route('/images')
    def get_all_images():
        images = Image.query.all()
        return render_template('images.html', images=images)

    @app.route('/images/upload')
    def upload_image():
        return render_template('upload_image.html')

    @app.template_filter()
    def thumbnail_image_with_fallback(image):
        """ Return the thumbnail image if it exists, otherwise return fullsized image """
        if image.thumbnail_image:
            return image.thumbnail_image.path
        else:
            return image.original_path

    @app.template_filter()
    def timeSortedImages(images):
        return sorted(images, key=lambda x: x.date, reverse=True)
