## Nick's Website

Right now it will just be hosting photos, but its scope will expand in the future.


## How to Launch
```
python -m SimpleHTTPServer 8000
```

## How to Deploy
```
rsync -rv --exclude 'input_images' --exclude '.git' . root@138.197.91.238:/root
```

Visit 127.0.0.1:8000 to visit the site
