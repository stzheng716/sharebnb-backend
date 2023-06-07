from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt

db = SQLAlchemy()

DEFAULT_IMAGE_URL = (
    "https://www.keywestnavalhousing.com/media/com_posthousing/images/nophoto.png" +
    "default-user-icon-28.jpg")


class User(db.Model):
    """User in the shareBnb."""

    __tablename__ = 'users'

    username = db.Column(
        db.String(30),
        primary_key=True
    )

    first_name = db.Column(
        db.String(25),
        nullable=False
    )

    last_name = db.Column(
        db.String(25),
        nullable=False
    )

    email = db.Column(
        db.String(50),
        nullable=False,
        unique=True,
    )

    password = db.Column(
        db.String(100),
        nullable=False,
    )

    isHost = db.Column(
        db.boolean,
        nullable=False,
        default="False",
    )


    listing = db.relationship('Listing', backref="host")


    @classmethod
    def signup(cls, username, first_name, last_name, email, password, isHost):
        """Sign up user.

        Hashes password and adds user to session.
        """

        hashed_pwd = bcrypt.generate_password_hash(password).decode('UTF-8')

        user = User(
            username=username,
            first_name=first_name,
            last_name=last_name,
            email=email,
            password=hashed_pwd,
            isHost=isHost,
        )

        db.session.add(user)
        return user

    @classmethod
    def authenticate(cls, username, password):
        """Find user with `username` and `password`.

        This is a class method (call it on the class, not an individual user.)
        It searches for a user whose password hash matches this password
        and, if it finds such a user, returns that user object.

        If this can't find matching user (or if password is wrong), returns
        False.
        """

        user = cls.query.filter_by(username=username).one_or_none()

        if user:
            is_auth = bcrypt.check_password_hash(user.password, password)
            if is_auth:
                return user

        return False

class Listing(db.Model):
    
    __tablename__= 'listings'

    id = db.Column(
        db.Integer,
        primary_key=True
    )

    title = db.Column(
        db.String(40),
        nullable=False
    )

    details = db.Column(
        db.Text,
        nullable=False
    )

    street = db.Column(
        db.String(50),
        nullable=False
    )

    city = db.Column(
        db.String(30),
        nullable=False
    )

    state = db.Column(
        db.String(2),
        nullable=False
    )

    zip = db.Column(
        db.Integer,
        nullable=False
    )

    country = db.Column(
        db.String(3),
        nullable=False
    )

    price_per_night = db.Column(
        db.Integer,
        nullable=False
    )

    image_url = db.Column(
        db.String(255),
        nullable=False,
        default=DEFAULT_IMAGE_URL,
    )

    username = db.Column(
        db.String(30),
        db.ForeignKey('users.username'),
        nullable=False,
    )

class Booking(db.Model):
    
    __tablename__= 'bookings'

    id = db.Column(
        db.Integer,
        primary_key=True
    )

    username = db.Column(
        db.String(30),
        db.ForeignKey('users.username'),
        nullable=False,
    )

    property_id = db.Column(
        db.Integer,
        db.ForeignKey('listings.id'),
        nullable=False,
    )

    check_in_date = db.Column(
        db.DateTime,
        nullable=False
    )

    check_out_date = db.Column(
        db.DateTime,
        nullable=False
    )

    booking_price_per_night = db.Column(
        db.Integer,
        nullable=False
    )

class Message(db.Model):
    
    __tablename__= 'messages'

    id = db.Column(
        db.Integer,
        primary_key=True
    )

    from_username = db.Column(
        db.String(30),
        db.ForeignKey('users.username'),
        nullable=False,
    )

    property_id = db.Column(
        db.Integer,
        db.ForeignKey('listings.id'),
        nullable=False,
    )

    body = db.Column(
        db.Text,
        nullable=False
    )

    sent_at_date = db.Column(
        db.DateTime,
        nullable=False
    )



# class File(db.Model):

#     __tablename__= 'files'

#     id = db.Column(db.Integer, primary_key=True)
#     original_filename = db.Column(db.String(100))
#     filename = db.Column(db.String(100))
#     bucket = db.Column(db.String(100))
#     region = db.Column(db.String(100))

# def connect_db(app):
#     """Connect this database to provided Flask app.
#     You should call this in your Flask app.
#     """

#     app.app_context().push()
#     db.app = app
#     db.init_app(app)
