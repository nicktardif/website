#!/usr/bin/env bash 

# Clear the output dir
rm -rf images/*
mkdir -p images/sprites
mkdir -p images/downsampled

# Convert the images
python convert.py --input_root_dir test_input/ --output_root_dir images/downsampled/

# Read the images.json in images/downsamples/images.json
# for each keyword, copy the images into a subfolder with that keyword
python make_folders.py --input_json images/downsampled/images.json --output_root_dir images/downsampled/

glue images/downsampled/ --project --cachebuster-filename-only-sprites --img images/sprites/ --css css --ratios=1,1.5,2

dirs=(${PWD}/images/downsampled/*)
for i in "${dirs[@]}"
do
  category=$(basename $i)
  mogrify -define jpeg:fancy-upsampling=off -quality 25% -format jpg images/sprites/$category@2x*.png
  mogrify -define jpeg:fancy-upsampling=off -quality 45% -format jpg images/sprites/$category@1.5x*.png
  mogrify -define jpeg:fancy-upsampling=off -quality 65% -format jpg images/sprites/$category_*.png
  sed -i -e 's/png/jpg/g' css/$category.css
done

grunt build
