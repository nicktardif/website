## Nick's Website
Displays photos! Uses [PhotoSwipe.js](http://www.photoswipe.com) and lots of image compression techniques.

Live site can be found at [nicktardif.com](http://www.nicktardif.com)

## Dependencies
```
sudo apt-get install python3.5-dev python-all-dev libboost-python-dev libexiv2-dev imagemagick
pipenv install
```

## Building
```
pipenv run python convert.py <input_dir> <output_dir>
```

## How to Launch Local Server
```
cd build && python -m SimpleHTTPServer
```

Visit `127.0.0.1:8000` to visit the site

## How to Deploy
```
pipenv run grunt deploy
# You may need to run the `windows_10_rsync_fix.sh` in another shell so that `rsync` works correctly
```
