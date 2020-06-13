from web_app import app, db
from flask_api import status
from web_app.models import Album, Portfolio
from web_app.utilities import Validator, Validation
from flask import jsonify, request
import itertools

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
            if not image.thumbnail_image:
                image.generate_thumbnail(thumbnail_size)

            if not image.downsampled_image:
                image.generate_downsampled(downsample_max_size)

            percent = ((idx + 1) / image_count) * 100.0
            print('Derived Image Generation: {:.2f}% - ({} of {})'.format(percent, idx + 1, image_count))

        # for each album:
            # create a spritemap and compress it
            # generate the page HTML
        # generate the whole website

        return '', status.HTTP_200_OK

def get_all_images_in_portfolio(portfolio_id):
    return set(list(itertools.chain.from_iterable([album.images for album in Portfolio.query.get(portfolio_id).albums])))
