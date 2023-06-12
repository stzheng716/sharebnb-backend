import os
from dotenv import load_dotenv
from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from models import db, connect_db, Listing, User, Message, Booking
from sqlalchemy.exc import IntegrityError
from awsUpload import uploadFileToS3
from jsonschema import validate
from schemas.userschema import userschema
from flask_cors import CORS

from flask_jwt_extended import create_access_token
from flask_jwt_extended import current_user
from flask_jwt_extended import jwt_required
from flask_jwt_extended import JWTManager

AMAZON_BASE_URL = "https://sharebnb-bucket.s3.us-west-1.amazonaws.com"

app = Flask(__name__)
CORS(app)

app.config["SQLALCHEMY_DATABASE_URI"] = os.environ.get("DATABASE_URL", "postgresql:///sharebnb")
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.config["SQLALCHEMY_ECHO"] = True
app.config["JWT_SECRET_KEY"] = os.environ["JWT_SECRET_KEY"]

jwt = JWTManager(app)
connect_db(app)
load_dotenv()

#JWT https://flask-jwt-extended.readthedocs.io/en/stable/automatic_user_loading.html

@jwt.user_lookup_loader
def user_lookup_callback(_jwt_header, jwt_data):
    identity = jwt_data.get('sub')["username"]
    return User.query.filter_by(username=identity).one_or_none()

##############################################################################
# auth routes:

@app.post('/auth/signup')
def signup():
    """Handle user signup.
    Create new user and add to DB.
    Returns
        {
            token: "asdfasfafd24...."
        }
    """

    data = request.json


    user = User.signup(
        username=data.get('username'),
        first_name=data.get('firstName'),
        last_name=data.get('lastName'),
        email=data.get('email'),
        password=data.get('password'),
        is_host=data.get('isHost')
    )
    db.session.commit()

    encoded_jwt = create_access_token(identity=user.serialize())

    return (jsonify(token=encoded_jwt), 201)


@app.post('/auth/login')
def login():
    """Handle user login.
    Verify if the user information. If valid returns a json web token
    Returns
        {
            token: "asdfasfafd..."
        }
    """
    data = request.json

    user = User.authenticate(
        username=data['username'],
        password=data['password']
        )

    if user:
        encoded_jwt = create_access_token(identity=user.serialize())
        return jsonify(token=encoded_jwt)
    
    message = {'message':"Invalid credentials"}

    return (jsonify(error=message), 401)

##############################################################################
# User routes:

@app.get('/users/<username>')
def get_user(username):
    """Get a user from database and returns.
    returns
    {
        "user": {
            "username", "email", "first_name", "is_host", "last_name",
            "sent_message": [message, message],
            "listing": [listing, listing],
        }
    }
    """

    user = User.query.get_or_404(username)
    json_user = user.serialize()

    if user and user.listing:
            listings = [listing.serialize() for listing in user.listing]
            json_user['listings'] = listings

    if user and user.booking:
            bookings = [booking.serialize() for booking in user.booking]
            json_user['bookings'] = bookings

    if user and user.sent_messages:
            sent_messages = [sent_message.serialize() for sent_message in user.sent_messages]
            json_user['sent_messages'] = sent_messages

    return jsonify(user=json_user)


@app.get('/users')
def get_users():
    """Get all user from database and returns an json with a list of users
    {
        "users": [{user}, {user}, {user}]
    }
    """

    users = [user.serialize() for user in User.query.all()]

    return jsonify(user=users)


@app.patch('/users/<username>')
def update_user(username):
    """Update user from data in request. Returns updated data.

    Take in a json and returns the updated user
    return a json
        {"user": {"username", "first_name", "last_name", "email", "is_host",}
        } 
    """

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

    return (jsonify(error='You can only update your own profile information'), 401)


@app.delete('/users/<username>')
def delete_user(username):
    """Delete user and return confirmation message.

    Returns JSON of {message: "delete successfully"}
    """

    user = User.query.get_or_404(username)
    if user:
        db.session.delete(user)
        db.session.commit()

        return jsonify(message='delete successfully')

    return (jsonify(error='You can only delete your own profile information'), 401)

##############################################################################
# Listing routes:

@app.post('/listings')
def create_listing():
    """create a listing by receiving 
        {
            "city", "country", "details", "image", "price_per_night", "state",
            "street", "title", "username", "zip"
        }
    return a json
        {
        "listing": {"city", "country", "details", "id", "image_url", "price_per_night",
            "state", "street", "title", "username", "zip"}
        } 
    """
    image = request.files.get('image', None)

    form = request.form

    full_url = None

    if image:
        image_url = uploadFileToS3(image)
        full_url = f"{AMAZON_BASE_URL}/{image_url}"

    new_listing = Listing(
        title=form['title'],
        details=form['details'],
        street=form['street'],
        city=form['city'],
        state=form['state'],
        zip=form['zip'],
        country=form['country'],
        price_per_night=form['price_per_night'],
        image_url=full_url,
        username=form['username'])

    db.session.add(new_listing)
    db.session.commit()

    return (jsonify(listing=new_listing.serialize()), 201)

@app.patch('/listings/<int:id>')
def update_listing(id):
    """Update listing from data in request. Returns updated data.

    Take in a json and returns the updated listing
    return a json
        {"listing": {"city", "country", "details", "id", "image_url", 
        "price_per_night", "state", "street", "title", "username", "zip"}
        } 
    """

    listing = Listing.query.get_or_404(id)

    image = request.files.get('image', None)
    form = request.form

    full_url = None

    if image:
        image_url = uploadFileToS3(image)
        full_url = f"{AMAZON_BASE_URL}/{image_url}"

    if listing:
        listing.title=form.get('title', listing.title),
        listing.details=form.get('details', listing.details),
        listing.street=form.get('street', listing.street),
        listing.city=form.get('city', listing.city),
        listing.state=form.get('state', listing.state),
        listing.zip=form.get('zip', listing.zip),
        listing.country=form.get('country', listing.country),
        listing.price_per_night=form.get('price_per_night', listing.price_per_night),
        listing.image_url= full_url or listing.image_url
        listing.username=form.get('username', listing.username)

    db.session.commit()

    return (jsonify(listing=listing.serialize()), 200)



@app.get('/listings')
def get_listings():
    """Get all listings from database or filter if there is a query string passed in 
    returns an json with a list of users
    {
        "listings": [{listing}, {listing}, {listing}]
    }
    """
    

    searchTerm = request.args.get('q', None)

    if searchTerm:
        
        filtered_listing = [listing.serialize() for listing in Listing.query.filter_by(title=searchTerm)]
        return jsonify(listings=filtered_listing)

    listings = [listing.serialize() for listing in Listing.query.all()]

    return jsonify(listings=listings)


@app.get('/listings/<int:id>')
def get_listing(id):
    """Get a listings from database based on the url params 
    returns an json with a user
    {
        "listing":{"city", "country", "details", "id", "image_url", 
        "price_per_night", "state", "street", "title", "username", "zip"}]
    }
    """

    listing = Listing.query.get_or_404(id)

    if listing:
        json_listing = listing.serialize()

        if listing.messages:
            json_listing['messages'] = [message.serialize() for message in listing.messages]

        if listing.bookings:
            json_listing['bookings'] = [booking.serialize() for booking in listing.bookings]

        return jsonify(listing=json_listing)

    return jsonify(listing=listing.serialize())


@app.delete('/listings/<int:id>')
def delete_listing(id):
    """Delete listing and return confirmation message.

    Returns JSON of {message: "Deleted listing successfully"}
    """

    listing = Listing.query.get_or_404(id)

    if listing:
        db.session.delete(listing)
        db.session.commit()

    return jsonify(message='Deleted listing successfully')

##############################################################################
#  Message routes:


@app.post('/messages')
def create_message():
    """create a message by receiving
        {"body", "property_id", "from_username"}
    return a json
        {"message": { "body", "id", "sent_at_date" } 
    """

    data = request.json

    body = data['body']
    property_id = data['property_id']
    from_username = data['from_username']

    message = Message(body=body, property_id=property_id,from_username=from_username)
    db.session.add(message)
    db.session.commit()

    return (jsonify(message=message.serialize()), 201)


@app.get('/messages/<int:id>')
def get_message(id):
    """Get a message from database by id 
    returns an json with a message
        {"message": { "body", "id", "sent_at_date" }
    """

    message = Message.query.get_or_404(id)

    return jsonify(message=message.serialize())


##############################################################################
#  Booking routes:

@app.get('/bookings/<int:id>')
def get_booking(id):
    """Get a booking from database by id 
    returns an json with a booking
        {"booking": {"id", "booking_price_per_night", "check_in_date", "check_out_date"
        "property_id", "username"}
    """

    booking = Booking.query.get_or_404(id)

    if booking:
        return jsonify(booking=booking.serialize())

    return jsonify(error='You cannot look at a booking if your not the host or guest')


@app.get('/bookings')
def get_bookings():
    """Get all booking from database 
    returns an json with a booking
        {"booking": [booking, booking, booking]}
    """

    bookings = [booking.serialize() for booking in Booking.query.all()]

    if bookings:
        return jsonify(bookings=bookings)

    return (jsonify(error='You cannot look at a booking if your not the host or guest'), 401)


@app.post('/bookings')
def create_booking():
    """create a booking by receiving
        {
        "username", "property_id", "check_in_date", "check_out_date", 
        "booking_price_per_night"}

    return a json
        {
        "booking": {
            "booking_price_per_night", "check_in_date", "check_out_date", "id", 
            "property_id", "username"}
        } 
    """

    data = request.json

    booking = Booking(
        username=data['username'],
        property_id=data['property_id'],
        check_in_date=data['check_in_date'],
        check_out_date=data['check_out_date'],
        booking_price_per_night=data['booking_price_per_night']
        )

    db.session.add(booking)
    db.session.commit()

    return (jsonify(booking=booking.serialize()), 201)


@app.delete('/bookings/<int:id>')
@jwt_required()
def delete_booking(id):
    """Delete a booking and return confirmation message.

    Returns JSON of {message: "Deleted booking successfully"}
    """

    booking = Booking.query.get_or_404(id)

    if current_user.username == booking.username:
        if booking:
            db.session.delete(booking)
            db.session.commit()

            return jsonify(message='Deleted booking successfully')

    return (jsonify(message='could not delete booking'), 401)

