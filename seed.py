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
    password="$2b$12$LURcsX0Icw4/37Job1WjNO/rIkP.Do3vfCtIaA7gytqrn5B5y.Dua",
    is_host=False
)

h1 = User(
    username="hostuser",
    first_name="firsttest",
    last_name="lasttest",
    email="email1234@gmail.com",
    password="$2b$12$LURcsX0Icw4/37Job1WjNO/rIkP.Do3vfCtIaA7gytqrn5B5y.Dua",
    is_host=True
)

l1 = Listing(
    title="A Frame Cabin the woods",
    details="Nestled amidst a picturesque forest setting, the A-frame cabin stands as a rustic retreat, blending harmoniously with nature's embrace. Surrounded by towering trees and the symphony of chirping birds, this charming abode exudes a sense of tranquility and offers a serene escape from the bustling world.",
    street="123 Main",
    city="Daly City",
    state="CA",
    zip=12345,
    country="USA",
    price_per_night=10,
    image_url="https://images.unsplash.com/photo-1590725140246-20acdee442be?ixlib=rb-4.0.3&ixid=M3wxMjA3fDB8MHxwaG90by1wYWdlfHx8fGVufDB8fHx8fA%3D%3D&auto=format&fit=crop&w=774&q=80",
    username="hostuser",
    latitude= 37.6879241,
    longitude= -122.4702079,
)

l2 = Listing(
    title="Designer home in the LA hills",
    details="Perched high in the stunning hills of Los Angeles, this designer home exudes contemporary elegance and offers a luxurious lifestyle amidst breathtaking panoramic views. Set against the backdrop of the sprawling cityscape and the majestic mountains, this architectural masterpiece combines sleek modernity with the natural beauty of its surroundings.",
    street="123 Main",
    city="Los Angeles",
    state="CA",
    zip=12345,
    country="USA",
    price_per_night=10,
    image_url="https://images.unsplash.com/photo-1502005229762-cf1b2da7c5d6?ixlib=rb-4.0.3&ixid=M3wxMjA3fDB8MHxwaG90by1wYWdlfHx8fGVufDB8fHx8fA%3D%3D&auto=format&fit=crop&w=1587&q=80",
    username="hostuser",
    latitude= 34.0522342,
    longitude= -118.2436849,
)

l3 = Listing(
    title="Rustic Cabin in South Tahoe",
    details="Nestled amidst the serene beauty of South Tahoe, this rustic cabin embodies the charm and tranquility of a mountain retreat. Surrounded by towering pine trees and framed by the majestic Sierra Nevada Mountains, this cozy hideaway offers a true escape from the hustle and bustle of everyday life.",
    street="123 Main",
    city="South Lake Tahoe",
    state="NV",
    zip=12345,
    country="USA",
    price_per_night=10,
    image_url="https://images.unsplash.com/photo-1510798831971-661eb04b3739?ixlib=rb-4.0.3&ixid=M3wxMjA3fDB8MHxwaG90by1wYWdlfHx8fGVufDB8fHx8fA%3D%3D&auto=format&fit=crop&w=1587&q=80",
    username="hostuser",
    latitude=38.936604,
    longitude=-119.986649,
)

l4 = Listing(
    title="Weekend Relaxing get away",
    details="Escape the stresses of everyday life and embark on a weekend getaway designed for pure relaxation. This idyllic retreat offers a tranquil haven where you can rejuvenate your mind, body, and soul. From serene landscapes to luxurious amenities, every element has been carefully curated to provide the ultimate relaxation experience.",
    street="123 Main",
    city="Napa",
    state="CA",
    zip=12345,
    country="USA",
    price_per_night=10,
    image_url="https://images.unsplash.com/photo-1525113990976-399835c43838?ixlib=rb-4.0.3&ixid=M3wxMjA3fDB8MHxwaG90by1wYWdlfHx8fGVufDB8fHx8fA%3D%3D&auto=format&fit=crop&w=1664&q=80",
    username="hostuser",
    latitude= 38.2975381,
    longitude= -122.286865,
)
 

b1 = Booking(
    id=1,
    username="testuser1",
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

db.session.add_all([u1,h1])
db.session.commit()
db.session.add_all([l1,l2,l3,l4])
db.session.commit()
db.session.add_all([m1])
db.session.commit()

