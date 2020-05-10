from flask import Flask
app = Flask(__name__)

API_VERSION = '1.0.0'

app.config['API_VERSION'] = API_VERSION
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:////tmp/app.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SWAGGER_TEMPLATE'] = {
    "swagger": "2.0",
    "info": {
        "version": API_VERSION,
        "title": "Night King's Intinerary",
        "description": "Programatically planning a Westeros vacation",
        "contact": {
            "name": "Nick Tardif",
            "email": "nicktardif@gmail.com",
            "url": "",
        },
    },
    "host": "127.0.0.1:8000",
    "basePath": "/",
    "schemes": [
        "http"
    ],
    "consumes": [
        "application/json"
    ],
    "produces": [
        "application/json"
    ]
}
