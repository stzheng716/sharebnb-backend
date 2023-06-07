import os
from dotenv import load_dotenv
from flask import Flask, redirect, url_for, request, render_template
from flask_sqlalchemy import SQLAlchemy
from models import db, connect_db

app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = os.environ.get("DATABASE_URL", "postgresql:///sharebnb")
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SQLALCHEMY_ECHO'] = True

connect_db(app)
db.init_app(app)

# TODO: models
# TODO: routes


#install jwt / import jwt - https://pyjwt.readthedocs.io/en/stable/
#validation for json - 
#create a jsonschema.py file
    #pip install jsonschema
    #write a schema for each model