"""Seed database with sample data from CSV Files."""

from app import app
from models import  db, Listing, User, Message

db.drop_all()
db.create_all()

u1 = User(
    username="testuser",
    first_name="firsttest",
    last_name="lasttest",
    email="email@gmail.com",
    password="password",
    is_host=False
)

# h1 = User(
#     username="hostuser",
#     first_name="firsttest",
#     last_name="lasttest",
#     email="email@gmail.com",
#     password="password",
#     isHost="False"
# )

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

# b1 = Booking(
#     id=1,
#     username="testuser",
#     property_id=1,
#     check_in_date="2008-11-09 15:45:21",
#     check_out_date="2008-11-11 11:12:01",
#     booking_price_per_night=9,
# )

m1 = Message(
    id=1,
    from_username="testuser",
    property_id=1,
    body="body of message",
    sent_at_date = "2008-11-12 11:12:01"
)
db.session.add_all([l1,u1, m1])
db.session.commit()
