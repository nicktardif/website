#!/usr/bin/env bash 
cat css/*.css > css/combo.css && sqwish css/combo.css -o css/nicktardif.min.css && rm css/combo.css
