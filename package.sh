#!/usr/bin/env bash 

# Clear the output dir
mkdir -p images/full
mkdir -p images/thumbs
mkdir -p images/sprites
rm images/full/*
rm images/thumbs/*
rm images/sprites/*

# Convert the images
./convert.py --input_dir input_images/ --output_dir images/ --previous_json images/images.json --output_json images/images.json

glue images/thumbs/ --cachebuster-filename-only-sprites --img images/sprites/ --css css
mogrify -quality 50% -format jpg images/sprites/thumbs*.png
sed -i -e 's/png/jpg/g' css/thumbs.css
