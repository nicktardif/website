from web_app import app, db
from flask_api import status
from web_app.models import Album, Portfolio
from web_app.utilities import Validator, Validation
from flask import jsonify, request
from web_app.utilities.custom_roles_required import custom_roles_required
import itertools

import os
import glob
import shutil
import tempfile
import subprocess
from web_app.utilities.file_helper import get_full_path
from jinja2 import Environment, FileSystemLoader

class PortfolioApiView():
    @app.route('/api/v1/portfolios/<int:portfolio_id>')
    @custom_roles_required('admin')
    def api_get_portfolio(portfolio_id):
        validator = Validator([Validation.portfolio_exists(portfolio_id)])
        if not validator.validate(request):
            return validator.get_error_response()

        return jsonify(Portfolio.query.get(portfolio_id)), status.HTTP_200_OK

    @app.route('/api/v1/portfolios')
    @custom_roles_required('admin')
    def api_get_all_portfolios():
        portfolios = Portfolio.query.all()
        if portfolios:
            return jsonify(portfolios), status.HTTP_200_OK
        else:
            return '', status.HTTP_204_NO_CONTENT

    @app.route('/api/v1/portfolios', methods=['POST'])
    @custom_roles_required('admin')
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
    @custom_roles_required('admin')
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
    @custom_roles_required('admin')
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
    @custom_roles_required('admin')
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
    @custom_roles_required('admin')
    def api_delete_portfolio(portfolio_id):
        validator = Validator([Validation.portfolio_exists(portfolio_id)])
        if not validator.validate(request):
            return validator.get_error_response()

        Portfolio.query.get(portfolio_id).delete()
        return '', status.HTTP_200_OK

    @app.route('/api/v1/portfolios/<int:portfolio_id>/generate', methods=['POST'])
    @custom_roles_required('admin')
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

        portfolio = Portfolio.query.get(portfolio_id)

        with tempfile.TemporaryDirectory() as temp_build_dir:
            for directory in ['css', 'js', 'sprites']:
                os.mkdir(os.path.join(temp_build_dir, directory))

            for image in images:
                shutil.copy(get_full_path(image.downsampled_image.path), temp_build_dir)

            for album in portfolio.albums:
                create_gallery_webpage(album, portfolio_id, temp_build_dir)

            primary_album = Album.query.get(portfolio.primary_album_id)
            shutil.copy(os.path.join(temp_build_dir, '{}.html'.format(primary_album.name)), os.path.join(temp_build_dir, 'index.html'))

            ## generate the whole website

            ## Copy in the CSS and JS files
            original_js_dir = get_full_path('js')
            js_files = glob.glob('{}/*.js'.format(original_js_dir))
            concat_files(js_files, os.path.join(temp_build_dir, 'js', 'nicktardif.min.js'))

            original_css_dir = get_full_path('css')
            css_files = glob.glob('{}/*.css'.format(original_css_dir))
            concat_files(css_files, os.path.join(temp_build_dir, 'css', 'nicktardif.min.css'))
            shutil.copy(get_full_path('css/default-skin.svg'), os.path.join(temp_build_dir, 'css'))

            ## Copy in the favicon file
            shutil.copy(get_full_path('assets/favicon.ico'), temp_build_dir)

            shutil.rmtree(app.config['BUILD_DIR'])
            shutil.move(temp_build_dir, app.config['BUILD_DIR'])

        return '', status.HTTP_200_OK

def create_gallery_webpage(album, portfolio_id, build_dir):
    # copy all the thumbnail images in the album to a new folder
    with tempfile.TemporaryDirectory() as temp_images_dir:
        for image in album.images:
            shutil.copy(get_full_path(image.thumbnail_image.path), temp_images_dir)

        album_sprites_dir = os.path.join(build_dir, album.name + '_sprites')
        shutil.rmtree(album_sprites_dir, ignore_errors=True)
        os.mkdir(album_sprites_dir)

        album_css_dir = os.path.join(build_dir, album.name + '_css')
        shutil.rmtree(album_css_dir, ignore_errors=True)
        os.mkdir(album_css_dir)

        # run the glue spritemap generation - outputs are spritemap and css code
        create_spritemaps(temp_images_dir, album_sprites_dir, album_css_dir, album)

        # generate the page HTML
        hash_string = os.path.basename(temp_images_dir)
        generate_html(build_dir, album, Portfolio.query.get(portfolio_id).albums, hash_string)

        shutil.copytree(album_css_dir, os.path.join(build_dir, 'css'), dirs_exist_ok=True)
        shutil.copytree(album_sprites_dir, os.path.join(build_dir, 'sprites'), dirs_exist_ok=True)

# For each category, render an HTML page
def generate_html(html_dir, album, albums, hash_string):
    code_root_dir = os.getcwd()
    template_dir = os.path.join(code_root_dir, 'web_app', 'templates')
    print('template dir: ' + template_dir)
    env = Environment(loader=FileSystemLoader(template_dir))
    env.filters['basename'] = basename
    env.filters['basenameNoExt'] = basenameNoExt
    env.filters['timeSortedImages'] = timeSortedImages
    env.filters['alphabeticalAlbums'] = alphabeticalAlbums
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
    print('Starting to generate the spritemaps for {}'.format(album.name))
    subprocess.check_output(glue_cmd, shell=True)

    print('Finished spritemap generation')

    print('Starting to compress spritemaps for {}'.format(album.name))
    random_name = os.path.basename(thumbnail_dir)
    compress_2x_cmd = 'mogrify -define jpeg:fancy-upsampling=off -quality 35% -format jpg {}/{}@2x*.png'.format(sprites_dir, random_name)
    compress_1_5x_cmd = 'mogrify -define jpeg:fancy-upsampling=off -quality 50% -format jpg {}/{}@1.5x*.png'.format(sprites_dir, random_name)
    compress_1x_cmd = 'mogrify -define jpeg:fancy-upsampling=off -quality 70% -format jpg {}/{}.png'.format(sprites_dir, random_name)
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

def timeSortedImages(images):
    return sorted(images, key=lambda x: x.date, reverse=True)

def alphabeticalAlbums(albums):
    return sorted(albums, key=lambda x: x.name)

def concat_files(input_files, output_file):
    with open(output_file, 'w') as outfile:
        for current_file in input_files:
            with open(current_file) as infile:
                for line in infile:
                    outfile.write(line)
