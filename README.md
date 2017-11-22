## Nick's Website

Right now it will just be hosting photos, but its scope will expand in the future.

## Dependencies
```
pip install glue # for spritemapping
npm install uglify-js -g
```


## How to Launch
```
python -m SimpleHTTPServer 8000
```

## How to Deploy
```
rsync -rv --exclude 'input_images' --exclude '.git' --exclude 'node_modules' . root@138.197.91.238:/var/www/nicktardif/
```

Visit 127.0.0.1:8000 to visit the site
