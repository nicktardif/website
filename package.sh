#!/usr/bin/env bash 

# Clear the output dir
rm -rf images/*
mkdir -p images/sprites
mkdir -p images/downsampled
mkdir -p css/categories/

# Convert the images
python convert.py --input_root_dir test_input/ --output_root_dir images/downsampled/

glue images/downsampled/ --project --cachebuster-filename-only-sprites --img images/sprites/ --css css/categories --ratios=1,1.5,2

dirs=(${PWD}/images/downsampled/*/)
for i in "${dirs[@]}"
do
  category=$(basename $i)
  mogrify -define jpeg:fancy-upsampling=off -quality 25% -format jpg images/sprites/$category@2x*.png
  mogrify -define jpeg:fancy-upsampling=off -quality 45% -format jpg images/sprites/$category@1.5x*.png
  mogrify -define jpeg:fancy-upsampling=off -quality 65% -format jpg images/sprites/$category_*.png
  sed -i -e 's/png/jpg/g' css/categories/$category.css
done

grunt build
