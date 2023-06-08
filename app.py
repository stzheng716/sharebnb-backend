import os
from dotenv import load_dotenv
from flask import Flask, redirect, url_for, request, render_template, jsonify
from flask_sqlalchemy import SQLAlchemy
from models import db, connect_db, Listing, User, Message
from sqlalchemy.exc import IntegrityError
from awsUpload import uploadFileToS3
# import jwt
# from tokens import createToken, authenitcateJWT

AMAZON_BASE_URL = "https://sharebnb-bucket2.s3.us-west-1.amazonaws.com"

app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = os.environ.get("DATABASE_URL", "postgresql:///sharebnb")
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SQLALCHEMY_ECHO'] = True

connect_db(app)

# TODO: models
# TODO: routes

#JWT https://flask-jwt-extended.readthedocs.io/en/stable/automatic_user_loading.html

@app.post('/auth/signup')
def signup():
    """Handle user signup.
    Create new user and add to DB.
    If the there already is a user with that username: return josnified error.
    """

    data = request.json

    user = User.signup(
        username=data['username'],
        first_name=data['firstName'],
        last_name=data['lastName'],
        email=data['email'],
        password=data['password'],
        is_host=data['isHost']
        )

    db.session.commit()

    return jsonify(user=user.serialize())
            # encoded_jwt = createToken(user)
            # return jsonify(token=encoded_jwt)

    # except IntegrityError:
    #         return jsonify(error=IntegrityError)

# @app.post('/auth/login')
# def login():
#     """Handle user login.
#     Create new user and add to DB.
#     If the there already is a user with that username: return josnified error.
#     """
#     data = request.json

#     user = User.authenticate(
#     username=data.username,
#     password=data.password
#     )

#     if user:
#         encoded_jwt = createToken(user)
#         return jsonify(token=encoded_jwt)
#     return jsonify(error="Invalid credentials")

@app.get('/users/<username>')
def get_user(username):

    user = User.query.get_or_404(username)
    
    return jsonify(user=user.serialize())



@app.patch('/users/<username>')
def update_user(username):

    data = request.json

    user = User.query.get_or_404(username)
    if user:
        user.first_name = data.get('firstName', user.first_name)
        user.last_name = data.get('lastName', user.last_name)
        user.email = data.get('email', user.email)
        user.is_host = bool(data.get('isHost', user.is_host))

        db.session.add(user)
        db.session.commit()

        return jsonify(user=user.serialize())

    return jsonify(error="You can only update your own profile information")

@app.delete('/users/<username>')
def delete_user(username):

    user = User.query.get_or_404(username)
    if user:
        db.session.delete(user)
        db.session.commit()

        return jsonify(message="delete successfully")

    return jsonify(error="You can only delete your own profile information")


# @app.get('/bookings/<int:id>')
# def get_booking(id):
#     headers = request.headers
#     token = headers['token']

#     booking = Booking.one_or_none(id)

#     guest = booking.username
#     host = booking.listing.username

#     if authenitcateJWT(token) == guest or host:

#         return jsonify(booking=booking)

#     return jsonify(error="You can't look at a booking if your not the host or guest")

@app.post('/listings')
def make_listing():

    file = request.files['image']

    title = request.form['title']
    details = request.form['details']
    street = request.form['street']
    city = request.form['city']
    state = request.form['state']
    zip = request.form['zip']
    country = request.form['country']
    price_per_night = request.form['price_per_night']

    image = file

    image_url = uploadFileToS3(image)
    full_url = f"{AMAZON_BASE_URL}/{image_url}"
    new_listing = Listing(title=title, details=details, street=street, state=state, zip=zip, country=country, city=city, price_per_night=price_per_night, image_url=full_url)

    db.session.add(new_listing)
    db.session.commit()

    return (jsonify(listing=new_listing.serialize()), 201)

@app.get('/listings')
def get_listings():

    listings = [listing.serialize() for listing in Listing.query.all()]

    return jsonify(listings=listings)

@app.get('/listings/<int:id>')
def get_listing(id):

    listing = Listing.query.get(id)

    return jsonify(listing=listing.serialize())

@app.post('/messages')
def create_message():
    
    data = request.json

    body = data['body']

    message = Message(body=body)

    return jsonify(message=message.serialize())