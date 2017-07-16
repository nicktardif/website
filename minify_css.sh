#!/usr/bin/env bash 
rm css/nicktardif.min.css && cat css/*.css > css/combo.css && sqwish css/combo.css -o css/nicktardif.min.css && rm css/combo.css
