#!/usr/bin/env bash 

# Clear the output dir
mkdir -p images/full
mkdir -p images/thumbs
mkdir -p images/sprites
mkdir -p js/min
mkdir -p css/min
rm images/full/*
rm images/thumbs/*
rm images/sprites/*
rm js/min/*

# Convert the images
./convert.py --input_dir input_images/ --output_dir images/ --previous_json images/images.json --output_json images/images.json

glue images/thumbs/ --cachebuster-filename-only-sprites --img images/sprites/ --css css
mogrify -define jpeg:fancy-upsampling=off -quality 65% -format jpg images/sprites/thumbs*.png
sed -i -e 's/png/jpg/g' css/thumbs.css

./minify_js.sh
./minify_css.sh
