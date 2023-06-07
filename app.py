import os
from dotenv import load_dotenv
from flask import Flask, redirect, url_for, request, render_template, jsonify
from flask_sqlalchemy import SQLAlchemy
from models import db, connect_db, User
from sqlalchemy.exc import IntegrityError
import jwt
from tokens import createToken

app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = os.environ.get("DATABASE_URL", "postgresql:///sharebnb")
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SQLALCHEMY_ECHO'] = True

connect_db(app)
db.init_app(app)

# TODO: models
# TODO: routes


# install jwt / import jwt - https://pyjwt.readthedocs.io/en/stable/
# validation for json -
# create a jsonschema.py file
#     pip install jsonschema
#     write a schema for each model

@app.post('/auth/signup')
def signup():
    """Handle user signup.
    Create new user and add to DB.
    If the there already is a user with that username: return josnified error.
    """
    data = request.json
    try:
            user = User.signup(
            username=data.username,
            first_name=data.first_name,
            last_name=data.last_name,
            email=data.email,
            password=data.password,
            isHost=data.isHost
            )

            db.session.commit(user)

            encoded_jwt = createToken(user)
            return jsonify(token=encoded_jwt)

    except IntegrityError:
            return jsonify(error=IntegrityError)

@app.post('/auth/login')
def login():
    """Handle user login.
    Create new user and add to DB.
    If the there already is a user with that username: return josnified error.
    """
    data = request.json

    user = User.authenticate(
    username=data.username,
    password=data.password
    )

    if user:
        encoded_jwt = createToken(user)
        return jsonify(token=encoded_jwt)
    return jsonify(error="Invalid credentials")
