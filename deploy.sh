#!/usr/bin/env bash 
rsync -rv --exclude 'input_images' --exclude '.git' --exclude 'node_modules' . root@138.197.91.238:/root
