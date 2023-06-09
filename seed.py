"""Seed database with sample data"""

from app import app
from models import  db, Listing, User, Message, Booking

db.drop_all()
db.create_all()

u1 = User(
    username="testuser1",
    first_name="firsttest",
    last_name="lasttest",
    email="email@gmail.com",
    password="password",
    is_host=False
)

h1 = User(
    username="hostuser",
    first_name="firsttest",
    last_name="lasttest",
    email="email1234@gmail.com",
    password="password",
    is_host=True
)

l1 = Listing(
    title="title",
    details="details",
    street="streetname",
    city="cityname",
    state="Ca",
    zip=12345,
    country="USA",
    price_per_night=10,
    image_url="https://www.keywestnavalhousing.com/media/com_posthousing/images/nophoto.png",
    username="hostuser"
)

b1 = Booking(
    id=1,
    username="testuser",
    property_id=1,
    check_in_date="2008-11-09 15:45:21",
    check_out_date="2008-11-11 11:12:01",
    booking_price_per_night=9,
)

m1 = Message(
    id=1,
    from_username="testuser1",
    property_id=1,
    body="body of message",
    sent_at_date = "2008-11-12 11:12:01"
)

<<<<<<< HEAD
#TODO: how to seed data in specific order?

=======
>>>>>>> 8a36595c5ad651848e3691b029a81af9b2eac94e
db.session.add_all([u1,h1])
db.session.commit()
db.session.add_all([l1])
db.session.commit()
db.session.add_all([m1])
db.session.commit()

