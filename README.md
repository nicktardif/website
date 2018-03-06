## Nick's Website
Displays photos! Uses [PhotoSwipe.js](http://www.photoswipe.com) and lots of image compression techniques.

Live site can be found at [nicktardif.com](http://www.nicktardif.com)

## Dependencies
```
# Install nodejs
curl -sL https://deb.nodesource.com/setup_9.x | sudo -E bash -
sudo apt-get install -y nodejs

# For py3exiv2
sudo apt-get install python3.5-dev python-all-dev libboost-python-dev libexiv2-dev

---

pip install glue pillow # for spritemapping

sudo npm install -g uglify-js grunt-cli
npm install
pipenv install
```

## How to Launch
```
pipenv shell
grunt
```

Visit 127.0.0.1:8000 to visit the site

## How to Deploy
```
grunt deploy
```
