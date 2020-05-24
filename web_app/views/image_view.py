from web_app import app
from web_app.models import Image
from flask import render_template

class ImageView():
    @app.route('/images/<int:image_id>')
    def get_image(image_id):
        image = Image.query.get(image_id)
        return render_template('images.html', images=[image])
        return jsonify(Image.query.get(image_id)), status.HTTP_200_OK

    @app.route('/images')
    def get_all_images():
        images = Image.query.all()
        return render_template('images.html', images=images)

    @app.route('/images/upload')
    def upload_image():
        return render_template('upload_image.html')
