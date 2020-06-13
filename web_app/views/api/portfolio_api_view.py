from web_app import app, db
from flask_api import status
from web_app.models import Album, Portfolio
from web_app.utilities import Validator, Validation
from web_app.utilities.file_helper import get_full_path
from flask import jsonify, request
import itertools
import os
import subprocess

class PortfolioApiView():
    @app.route('/api/v1/portfolios/<int:portfolio_id>')
    def api_get_portfolio(portfolio_id):
        validator = Validator([Validation.portfolio_exists(portfolio_id)])
        if not validator.validate(request):
            return validator.get_error_response()

        return jsonify(Portfolio.query.get(portfolio_id)), status.HTTP_200_OK

    @app.route('/api/v1/portfolios')
    def api_get_all_portfolios():
        portfolios = Portfolio.query.all()
        if portfolios:
            return jsonify(portfolios), status.HTTP_200_OK
        else:
            return '', status.HTTP_204_NO_CONTENT

    @app.route('/api/v1/portfolios', methods=['POST'])
    def api_create_portfolio():
        validator = Validator([
            Validation.is_json_payload(),
            Validation.required_json('name'),
            Validation.required_json('primary_album_id')
        ])
        if not validator.validate(request):
            return validator.get_error_response()

        name = request.get_json().get('name')
        primary_album_id = request.get_json().get('primary_album_id')
        album_ids = request.get_json().get('album_ids', [])
        albums = [Album.query.get(id) for id in album_ids]
        new_portfolio = Portfolio(name, primary_album_id, albums)
        db.session.add(new_portfolio)
        db.session.commit()

        return jsonify(new_portfolio), status.HTTP_201_CREATED

    @app.route('/api/v1/portfolios/<int:portfolio_id>', methods=['PATCH'])
    def api_update_portfolio(portfolio_id):
        validator = Validator([
            Validation.is_json_payload(),
            Validation.portfolio_exists(portfolio_id)
        ])
        if not validator.validate(request):
            return validator.get_error_response()

        portfolio = Portfolio.query.get(portfolio_id)
        name = request.get_json().get('name')
        if name:
            portfolio.update_name(name)

        primary_album_id = request.get_json().get('primary_album_id')
        if primary_album_id:
            portfolio.update_primary_album(primary_album_id)

        album_ids = request.get_json().get('album_ids', [])
        albums = [Album.query.get(id) for id in album_ids]
        if albums:
            portfolio.update_albums(albums)

        return jsonify(portfolio), status.HTTP_200_OK

    @app.route('/api/v1/portfolios/<int:portfolio_id>/albums/<int:album_id>', methods=['POST'])
    def api_portfolio_add_album(portfolio_id, album_id):
        validator = Validator([
            Validation.portfolio_exists(portfolio_id),
            Validation.album_exists(album_id)
        ])
        if not validator.validate(request):
            return validator.get_error_response()

        portfolio = Portfolio.query.get(portfolio_id)
        album = Album.query.get(album_id)
        if album not in portfolio.albums:
            portfolio.add_album(album)
            return '', status.HTTP_200_OK
        else:
            return '', status.HTTP_400_BAD_REQUEST

    @app.route('/api/v1/portfolios/<int:portfolio_id>/albums/<int:album_id>', methods=['DELETE'])
    def api_portfolio_remove_album(portfolio_id, album_id):
        validator = Validator([
            Validation.portfolio_exists(portfolio_id),
            Validation.album_exists(album_id)
        ])
        if not validator.validate(request):
            return validator.get_error_response()

        portfolio = Portfolio.query.get(portfolio_id)
        album = Album.query.get(album_id)
        if album in portfolio.albums:
            portfolio.remove_album(album)
            return '', status.HTTP_200_OK
        else:
            return '', status.HTTP_400_BAD_REQUEST

    @app.route('/api/v1/portfolios/<int:portfolio_id>', methods=['DELETE'])
    def api_delete_portfolio(portfolio_id):
        validator = Validator([Validation.portfolio_exists(portfolio_id)])
        if not validator.validate(request):
            return validator.get_error_response()

        Portfolio.query.get(portfolio_id).delete()
        return '', status.HTTP_200_OK

    @app.route('/api/v1/portfolios/<int:portfolio_id>/generate', methods=['POST'])
    def api_generate_website(portfolio_id):
        thumbnail_size = 400
        downsample_max_size = 2400
        # downsample_size

        images = get_all_images_in_portfolio(portfolio_id)
        image_count = len(images)

        # create thumbnail and downsampled images for all images in the albums
        for idx, image in enumerate(images):
            thumbnail_absolute_path = ImageGenerator.create_thumbnail(image, thumbnail_size)
            print('thumbnail absolute path: ' + thumbnail_absolute_path)

            # TODO: Create a database object for this

            percent = ((idx + 1) / image_count) * 100.0
            print('Thumbnail Generation: {:.2f}% - ({} of {})'.format(percent, idx + 1, image_count))

        for idx, image in enumerate(images):
            downsampled_absolute_path = ImageGenerator.create_downsampled(image, downsample_max_size)
            print('downsampled absolute path: ' + downsampled_absolute_path)

            # TODO: Create a database object for this

            percent = ((idx + 1) / image_count) * 100.0
            print('Fullsize Compression: {:.2f}% - ({} of {})'.format(percent, idx + 1, image_count))

        # for each album:
            # create a spritemap and compress it
            # generate the page HTML
        # generate the whole website

        return '', status.HTTP_200_OK

def get_all_images_in_portfolio(portfolio_id):
    return set(list(itertools.chain.from_iterable([album.images for album in Portfolio.query.get(portfolio_id).albums])))

class ImageGenerator:
    def create_thumbnail(image, min_dimension):
        image_full_path = get_full_path(image.original_path)
        width, height = ImageGenerator.calculate_dimensions(image_full_path, min_dimension, False)
        thumbnail_file = ImageGenerator.create_thumbnail_file(image_full_path, width, height, min_dimension)
        print('Thumbnail: {}x{}, Destination: {}'.format(width, height, thumbnail_file))
        return thumbnail_file

    def create_downsampled(image, max_dimension):
        image_full_path = get_full_path(image.original_path)
        width, height = ImageGenerator.calculate_dimensions(image_full_path, max_dimension, True)
        downsampled_file = ImageGenerator.create_downsampled_file(image_full_path, width, height)
        print('Downsampled: {}x{}, Destination: {}'.format(width, height, downsampled_file))
        return downsampled_file

    def calculate_dimensions(image_full_path, request_dimension, is_max):
        # TODO: Find a Python library to get the width and height
        width = int(subprocess.check_output("identify -format '%w' \"{}\"".format(image_full_path), shell=True))
        height = int(subprocess.check_output("identify -format '%h' \"{}\"".format(image_full_path), shell=True))

        aspect_ratio = float(width) / float(height)
        max_dimension = max(width, height)
        min_dimension = min(width, height)

        new_width = width
        new_height = height
        scale_ratio = 1.0

        if(is_max): # Reduce max dimension to request_dimension
            if(max_dimension > request_dimension):
                scale_ratio = float(request_dimension) / float(max_dimension)
        else: # Reduce min dimension to request_dimension
            if(min_dimension > request_dimension):
                scale_ratio = float(request_dimension) / float(min_dimension)

        if(aspect_ratio > 1.0): # Landscape
            new_width = int(max_dimension * scale_ratio)
            new_height = int(min_dimension * scale_ratio)
        else: # Square or portrait
            new_width = int(min_dimension * scale_ratio)
            new_height = int(max_dimension * scale_ratio)

        return new_width, new_height

    def create_thumbnail_file(image_full_path, scaled_width, scaled_height, square_size):
        downscaled_full_path = ImageGenerator.get_downscaled_file_name(image_full_path, square_size, square_size)
        convert_cmd = "convert -resize {}x{}^ -extent {}x{} -gravity Center \( \"{}\" -strip -resize {}x{} \) \"{}\"".format(
                square_size, square_size,
                square_size, square_size,
                image_full_path,
                scaled_width, scaled_height,
                downscaled_full_path)

        subprocess.check_output(convert_cmd, shell=True)
        return downscaled_full_path

    def create_downsampled_file(image_full_path, width, height):
        downscaled_full_path = ImageGenerator.get_downscaled_file_name(image_full_path, width, height)
        convert_cmd = "convert -strip -interlace Plane -quality 85% \"{}\" -resize {}x{} \"{}\"".format(
                image_full_path,
                width, height,
                downscaled_full_path)

        subprocess.check_output(convert_cmd, shell=True)
        return downscaled_full_path

    def get_downscaled_file_name(image_full_path, width, height):
        basename, extension = os.path.splitext(os.path.basename(image_full_path))
        full_name = '{}_{}x{}{}'.format(basename, width, height, extension)
        return get_full_path(full_name)
