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
pipenv run python main.py generate <input_dir> <output_dir>
```

## How to Launch Local Server
```
pipenv run python main.py host <build_dir>
```
Visit `127.0.0.1:8000` to visit the site

## How to Deploy
```
pipenv run python main.py deploy <build_dir>
```
