from web_app import app, db
from flask_api import status
from web_app.models import Album, Portfolio
from web_app.utilities import Validator, Validation
from flask import jsonify, request
import itertools

import os
import shutil
import tempfile
import subprocess
from web_app.utilities.file_helper import get_full_path, get_full_build_path
from jinja2 import Environment, FileSystemLoader

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

        # TODO: Clear the build dir, create CSS and JS dirs
        shutil.rmtree(app.config['BUILD_DIR'], ignore_errors=True)
        for directory in [app.config['BUILD_DIR'], app.config['BUILD_CSS_DIR'], app.config['BUILD_JS_DIR']]:
            os.mkdir(directory)

        # create thumbnail and downsampled images for all images in the albums
        for idx, image in enumerate(images):
            if not image.thumbnail_image:
                image.generate_thumbnail(thumbnail_size)

            if not image.downsampled_image:
                image.generate_downsampled(downsample_max_size)

            percent = ((idx + 1) / image_count) * 100.0
            print('Derived Image Generation: {:.2f}% - ({} of {})'.format(percent, idx + 1, image_count))

        for album in Album.query.all():
            create_gallery_webpage(album)

        ## generate the whole website

        ## Copy in the CSS and JS files
        #original_js_dir = os.path.join(code_root_dir, 'js')
        #js_files = get_all_js(original_js_dir)
        #concat_files(js_files, os.path.join(js_dir, 'nicktardif.min.js'))

        #original_css_dir = os.path.join(code_root_dir, 'css')
        #css_files = get_all_css(original_css_dir)
        #concat_files(css_files, os.path.join(css_dir, 'nicktardif.min.css'))
        #shutil.copy(os.path.join(original_css_dir, 'default-skin.svg'), css_dir)

        ## Copy in the favicon file
        #shutil.copy(os.path.join(code_root_dir, 'assets', 'favicon.ico'), output_root_dir)

        return '', status.HTTP_200_OK

def create_gallery_webpage(album):
    # copy all the thumbnail images in the album to a new folder
    with tempfile.TemporaryDirectory() as temporary_directory:
        for image in album.images:
            shutil.copy(get_full_path(image.thumbnail_image.path), temporary_directory)

        album_sprites_dir = get_full_build_path(album.name + '_sprites')
        shutil.rmtree(album_sprites_dir, ignore_errors=True)
        os.mkdir(album_sprites_dir)

        album_css_dir = get_full_build_path(album.name + '_css')
        shutil.rmtree(album_css_dir, ignore_errors=True)
        os.mkdir(album_css_dir)

        # run the glue spritemap generation - outputs are spritemap and css code
        create_spritemaps(temporary_directory, album_sprites_dir, album_css_dir, album)

        # generate the page HTML
        hash_string = os.path.basename(temporary_directory)
        generate_html(app.config['BUILD_DIR'], album, Album.query.all(), hash_string)

        shutil.copytree(album_css_dir, app.config['BUILD_CSS_DIR'], dirs_exist_ok=True)
        shutil.copytree(album_sprites_dir, app.config['BUILD_SPRITES_DIR'], dirs_exist_ok=True)

# For each category, render an HTML page
def generate_html(html_dir, album, albums, hash_string):
    code_root_dir = os.getcwd()
    template_dir = os.path.join(code_root_dir, 'web_app', 'templates')
    print('template dir: ' + template_dir)
    env = Environment(loader=FileSystemLoader(template_dir))
    env.filters['basename'] = basename
    env.filters['basenameNoExt'] = basenameNoExt
    template = env.get_template('gallery_template.html')

    output_from_parsed_template = template.render(hash_string=hash_string, album=album, albums=albums)

    # Write out the HTML file
    html_file = '{}.html'.format(album.name)
    with open(os.path.join(html_dir, html_file), 'w') as f:
        f.write(output_from_parsed_template)

def create_spritemaps(thumbnail_dir, sprites_dir, css_dir, album):
    glue_cmd = 'glue {} --img {} --force --css {} --ratios=2,1.5,1'.format(
            thumbnail_dir,
            sprites_dir,
            css_dir)
    print('Starting to generate the spritemaps')
    subprocess.check_output(glue_cmd, shell=True)

    print('Finished spritemap generation')

    print('Starting to compress spritemaps')
    random_name = os.path.basename(thumbnail_dir)
    compress_2x_cmd = 'mogrify -define jpeg:fancy-upsampling=off -quality 25% -format jpg {}/{}@2x*.png'.format(sprites_dir, random_name)
    compress_1_5x_cmd = 'mogrify -define jpeg:fancy-upsampling=off -quality 45% -format jpg {}/{}@1.5x*.png'.format(sprites_dir, random_name)
    compress_1x_cmd = 'mogrify -define jpeg:fancy-upsampling=off -quality 65% -format jpg {}/{}.png'.format(sprites_dir, random_name)
    sed_switch_image_type_cmd = "sed -i -e 's/png/jpg/g' {}/{}.css".format(css_dir, random_name)
    sed_update_sprite_path_cmd = "sed -i -e 's/..\/{}_sprites/\/sprites/g' {}/{}.css".format(album.name, css_dir, random_name)
    rm_png_cmd = 'rm {}/{}*.png'.format(sprites_dir, random_name)

    subprocess.check_output(compress_2x_cmd, shell=True)
    subprocess.check_output(compress_1_5x_cmd, shell=True)
    subprocess.check_output(compress_1x_cmd, shell=True)
    subprocess.check_output(sed_switch_image_type_cmd, shell=True)
    subprocess.check_output(sed_update_sprite_path_cmd, shell=True)
    subprocess.check_output(rm_png_cmd, shell=True)
    print('Compressed {} album'.format(album.name))

def get_all_images_in_portfolio(portfolio_id):
    return set(list(itertools.chain.from_iterable([album.images for album in Portfolio.query.get(portfolio_id).albums])))

def basename(path):
    return os.path.basename(path)

def basenameNoExt(path):
    return os.path.splitext(os.path.basename(path))[0]
