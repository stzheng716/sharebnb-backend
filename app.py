import os
from dotenv import load_dotenv
from flask import Flask, request, jsonify
from sqlalchemy import func
from models import db, connect_db, Listing, User, Message, Booking
from sqlalchemy.exc import IntegrityError
from awsUpload import uploadFileToS3
from flask_json_schema import JsonSchema, JsonValidationError
from schemas.userschema import user_schema
from flask_cors import CORS
# from geoCoder import geoCoder
from geoCode import getGeoCode

from flask_jwt_extended import create_access_token
from flask_jwt_extended import current_user
from flask_jwt_extended import jwt_required
from flask_jwt_extended import JWTManager

AMAZON_BASE_URL = "https://sharebnb-bucket.s3.us-west-1.amazonaws.com"

app = Flask(__name__)
CORS(app)

database_url = os.environ['DATABASE_URL']
database_url = database_url.replace('postgres://', 'postgresql://')
app.config["SQLALCHEMY_DATABASE_URI"] = os.environ.get(
    "DATABASE_URL", "postgresql:///sharebnb")
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.config["SQLALCHEMY_ECHO"] = True
app.config["JWT_SECRET_KEY"] = os.environ["JWT_SECRET_KEY"]
app.config['SQLALCHEMY_DATABASE_URI'] = database_url

schema=JsonSchema(app)
jwt = JWTManager(app)
connect_db(app)
load_dotenv()


@app.errorhandler(JsonValidationError)
def validation_error(e):
    return jsonify({ 'error': e.message, 'errors': [validation_error.message for validation_error  in e.errors]})

@jwt.user_lookup_loader
def user_lookup_callback(_jwt_header, jwt_data):
    identity = jwt_data.get('sub')["username"]
    return User.query.filter_by(username=identity).one_or_none()

##############################################################################
# auth routes:

# add try expect
@app.post('/auth/signup')
@schema.validate(user_schema)
def signup():
    """Handle user signup.
    Create new user and add to DB.
    Returns
        {
            token: "asdfasfafd24...."
        }
    """

    data = request.json

    username = data.get('username')
    email = data.get('email')

    # Check if username already exists
    existing_user = User.query.filter_by(username=username).first()
    if existing_user:
        message = {'message': "Username already exists"}
        return (jsonify(error=message), 409)

    # Check if email already exists
    existing_user = User.query.filter_by(email=email).first()
    if existing_user:
        message = {'message': "Email already exists"}
        return (jsonify(error=message), 409)
    
    user = User.signup(
            username=username,
            first_name=data.get('firstName'),
            last_name=data.get('lastName'),
            email=email,
            password=data.get('password'),
            is_host=data.get('isHost')
        )

    

    if user:
        encoded_jwt = create_access_token(identity=user.serialize())
        return (jsonify(token=encoded_jwt), 201)

    message = {'message': "Invalid credentials"}

    return (jsonify(error=message), 401)


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

    message = {'message': "Invalid credentials"}

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

    user = User.query.get(username)

    if user:
        json_user = user.serialize()
        return jsonify(user=json_user)

    message = {'message': f"No user: {username}"}

    return (jsonify(error=message), 404)


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
@jwt_required()
def update_user(username):
    """Update user from data in request. Returns updated data.

    Take in a json and returns the updated user
    return a json
        {"user": {"username", "first_name", "last_name", "email", "is_host",}
        } 
    """

    if current_user != username:
        return jsonify({"error": "Invalid Authorization"})

    data = request.json

    user = User.query.get(username)

    user.first_name = data.get('firstName', user.first_name)
    user.last_name = data.get('lastName', user.last_name)
    user.email = data.get('email', user.email)
    user.is_host = bool(data.get('isHost', user.is_host))

    db.session.commit()

    return jsonify(user=user.serialize())


@app.delete('/users/<username>')
def delete_user(username):
    """Delete user and return confirmation message.

    Returns JSON of {message: "delete successfully"}
    """

    user = User.query.get(username)

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

    lng_lat = getGeoCode(f"{form.get('street')} {form.get('city')}")

    new_listing = Listing(
        title=form['title'],
        details=form['details'],
        street=form['street'],
        city=form['city'],
        state=form['state'],
        latitude=lng_lat['latitude'],
        longitude=lng_lat['longitude'],
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

    listing = Listing.query.get(id)

    image = request.files.get('image', None)
    form = request.form

    full_url = None

    if image:
        image_url = uploadFileToS3(image)
        full_url = f"{AMAZON_BASE_URL}/{image_url}"

    if listing:
        listing.title = form.get('title', listing.title),
        listing.details = form.get('details', listing.details),
        listing.street = form.get('street', listing.street),
        listing.city = form.get('city', listing.city),
        listing.state = form.get('state', listing.state),
        listing.zip = form.get('zip', listing.zip),
        listing.country = form.get('country', listing.country),
        listing.price_per_night = form.get(
            'price_per_night', listing.price_per_night),
        listing.image_url = full_url or listing.image_url
        listing.username = form.get('username', listing.username)

        db.session.commit()

        return (jsonify(listing=listing.serialize()), 200)

    message = {'message': f"No listing: {id}"}

    return (jsonify(error=message), 404)


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

        filtered_listing = [listing.serialize() for listing in Listing.query
                            .filter(func
                                    .lower(Listing.title)
                                    .contains(searchTerm.lower()))
                                    .all()
                            ]
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

    listing = Listing.query.get(id)

    if listing:
        json_listing = listing.serialize()

        return jsonify(listing=json_listing)

    message = {'message': f"No listing: {id}"}

    return (jsonify(error=message), 404)


@app.delete('/listings/<int:id>')
@jwt_required()
def delete_listing(id):
    """Delete listing and return confirmation message.

    Returns JSON of {message: "Deleted listing successfully"}
    """

    listing = Listing.query.get(id)

    if current_user.username != listing.username:
        return jsonify({"error": "Invalid Authorization"})

    if listing:
        for message in listing.messages:
            db.session.delete(message)

        for booking in listing.messages:
            db.session.delete(booking)

        db.session.delete(listing)
        db.session.commit()
        return jsonify(message='Deleted listing successfully')

    message = {'message': f"No listing: {id}"}

    return (jsonify(error=message), 404)


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

    message = Message(body=body, property_id=property_id,
                      from_username=from_username)
    db.session.add(message)
    db.session.commit()

    return (jsonify(message=message.serialize()), 201)


@app.get('/messages/<int:id>')
def get_message(id):
    """Get a message from database by id 
    returns an json with a message
        {"message": { "body", "id", "sent_at_date" }
    """

    message = Message.query.get(id)

    if message:
        return jsonify(message=message.serialize())

    message = {'message': f"No message: {id}"}

    return (jsonify(error=message), 404)


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

    message = {'message': f"No booking: {id}"}

    return (jsonify(error=message), 404)


@app.get('/bookings')
def get_bookings():
    """Get all booking from database 
    returns an json with a booking
        {"booking": [booking, booking, booking]}
    """

    bookings = [booking.serialize() for booking in Booking.query.all()]

    if bookings:
        return jsonify(bookings=bookings)

    message = {'message': f"No booking: {id}"}

    return (jsonify(error=message), 404)


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

    print("username", current_user.username)

    if current_user.username != booking.username:
        return jsonify({"error": "Invalid Authorization"})

    if booking:
        db.session.delete(booking)
        db.session.commit()

        return jsonify(message='Deleted booking successfully')

    message = {'message': f"No booking: {id}"}

    return (jsonify(error=message), 404)
