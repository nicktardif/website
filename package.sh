#!/usr/bin/env bash 
SOURCE_IMAGE_DIR=$1

# Clear the output dir
rm -rf images/*
mkdir -p images/sprites
mkdir -p images/downsampled
mkdir -p css/categories/

# Convert the images
convert_start=`date +%s`
python convert.py --input_root_dir $SOURCE_IMAGE_DIR --output_root_dir images/downsampled/
convert_end=`date +%s`

# Move these images out for now, so they're not added to the sprites or minified
mv images/downsampled/full images/full

glue_start=`date +%s`
glue images/downsampled/ --project --cachebuster-filename-only-sprites --img images/sprites/ --css css/categories --ratios=2,1
glue_end=`date +%s`

compress_start=`date +%s`
dirs=(${PWD}/images/downsampled/*/)
for i in "${dirs[@]}"
do
  category=$(basename $i)
  mogrify -define jpeg:fancy-upsampling=off -quality 25% -format jpg images/sprites/$category@2x*.png
  mogrify -define jpeg:fancy-upsampling=off -quality 45% -format jpg images/sprites/$category@1.5x*.png
  mogrify -define jpeg:fancy-upsampling=off -quality 65% -format jpg images/sprites/$category_*.png
  sed -i -e 's/png/jpg/g' css/categories/$category.css
done
compress_end=`date +%s`

# Move them back
mv images/full images/downsampled/full

convert_runtime=$((convert_end-convert_start))
glue_runtime=$((glue_end-glue_start))
compress_runtime=$((compress_end-compress_start))

echo "Convert runtime: ${convert_runtime}"
echo "Glue runtime: ${glue_runtime}"
echo "Compress runtime: ${compress_runtime}"

grunt build
