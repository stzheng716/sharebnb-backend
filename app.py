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
    If the there already is a user with that username: return josnified error.
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
    Create new user and add to DB.
    If the there already is a user with that username: return josnified error.
    """
    data = request.json

    user = User.authenticate(
        username=data['username'],
        password=data['password']
        )

    if user:
        encoded_jwt = create_access_token(identity=user.serialize())
        return jsonify(token=encoded_jwt)
    return jsonify(error="Invalid credentials")

##############################################################################
# User routes:

@app.get('/users/<username>')
def get_user(username):

    user = User.query.get_or_404(username)
    json_user = user.serialize()

    if user and user.listing:
            listings = [listing.serialize() for listing in user.listing]
            json_user['listing'] = listings

    if user and user.booking:
            bookings = [booking.serialize() for booking in user.booking]
            json_user['booking'] = bookings

    if user and user.sent_messages:
            sent_messages = [sent_message.serialize() for sent_message in user.sent_messages]
            json_user['sent_message'] = sent_messages

    return jsonify(user=json_user)


@app.get('/users')
def get_users():

    users = [user.serialize() for user in User.query.all()]

    return jsonify(user=users)


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

    return jsonify(error='You can only update your own profile information')


@app.delete('/users/<username>')
def delete_user(username):

    user = User.query.get_or_404(username)
    if user:
        db.session.delete(user)
        db.session.commit()

        return jsonify(message='delete successfully')

    return jsonify(error='You can only delete your own profile information')

##############################################################################
# Listing routes:

@app.post('/listings')
def create_listing():
    """create a listing by receiving {
                "city": "city value",
                "country": "USA",
                "details": "details value",
                "image": an image file,
                "price_per_night": 200,
                "state": "ca",
                "street": "street value",
                "title": "house2",
                "username": "testuser1",
                "zip": 12345
            }
       return a json
            {
            "listing": {
                "city": "city value",
                "country": "USA",
                "details": "details value",
                "id": 5,
                "image_url": "https://www.keywestnavalhousing.com/media/com_posthousing/images/nophoto.png",
                "price_per_night": 200,
                "state": "ca",
                "street": "street value",
                "title": "house2",
                "username": "testuser1",
                "zip": 12345
            }
        } """
    image = request.files.get('image', None)

    print("IMAGE", request.files.get('image', None))

    form = request.form

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

    searchTerm = request.args.get('q')

    if searchTerm:

        filtered_listing = [listing.serialize() for listing in Listing.query.filter_by(title=searchTerm)]
        return jsonify(listings=filtered_listing)

    listings = [listing.serialize() for listing in Listing.query.all()]

    return jsonify(listings=listings)


@app.get('/listings/<int:id>')
def get_listing(id):

    listing = Listing.query.get_or_404(id)

    if listing and listing.bookings:
        json_listing = listing.serialize()

        if listing and listing.messages:
             json_listing['messages'] = [message.serialize() for message in listing.messages]

        json_listing['bookings'] = [booking.serialize() for booking in listing.bookings]
        return jsonify(listing=json_listing)

    return jsonify(listing=listing.serialize())


@app.delete('/listings/<int:id>')
def delete_listing(id):

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
    {
	"body":"hfsadfello",
	"property_id":"1",
	"from_username":"testuser2"
}
    return a json
        {
	"message": {
		"body": "hfsadfello",
		"id": 2,
		"sent_at_date": "Thu, 08 Jun 2023 10:03:32 GMT"
	}
} """

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

    message = Message.query.get_or_404(id)

    return jsonify(message=message.serialize())

##############################################################################
#  Booking routes:

@app.get('/bookings/<int:id>')
def get_booking(id):

    booking = Booking.query.get_or_404(id)

    if booking:
        return jsonify(booking=booking.serialize())

    return jsonify(error='You cannot look at a booking if your not the host or guest')


@app.get('/bookings')
def get_bookings():

    bookings = [booking.serialize() for booking in Booking.query.all()]

    if bookings:
        return jsonify(booking=bookings)

    return jsonify(error='You cannot look at a booking if your not the host or guest')


@app.post('/bookings')
def create_booking():
    """create a booking by receiving
        {
        "username":"testuser2",
        "property_id":"1",
        "check_in_date": "2008-11-09 15:45:21",
        "check_out_date": "2008-11-11 11:12:01",
        "booking_price_per_night":"5"
    }

    return a json
   {
	"booking": {
		"booking_price_per_night": 5,
		"check_in_date": "Sun, 09 Nov 2008 15:45:21 GMT",
		"check_out_date": "Tue, 11 Nov 2008 11:12:01 GMT",
		"id": 2,
		"property_id": 1,
		"username": "testuser2"
	}
} """

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

    booking = Booking.query.get_or_404(id)

    if current_user.username == booking.username:
        if booking:
            db.session.delete(booking)
            db.session.commit()

            return jsonify(message='Deleted booking successfully')

    return jsonify(message='could not delete booking')

