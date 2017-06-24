#!/usr/bin/env bash
for arg; do
  fullfile=$arg
  echo $fullfile

  filename=$(basename "$fullfile")
  extension="${filename##*.}"
  filename="${filename%.*}"

  quarter_filename=${filename}_quarter.${extension}
  thumbnail_filename=${filename}_thumbnail.${extension}

  convert $fullfile -resize 2448x1632 $quarter_filename
  convert $fullfile -resize 300x200 $thumbnail_filename
done
