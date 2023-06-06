from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

class File(db.Model):

    __tablename__= 'files'

    id = db.Column(db.Integer, primary_key=True)
    original_filename = db.Column(db.String(100))
    filename = db.Column(db.String(100))
    bucket = db.Column(db.String(100))
    region = db.Column(db.String(100))

# def connect_db(app):
#     """Connect this database to provided Flask app.
#     You should call this in your Flask app.
#     """

#     app.app_context().push()
#     db.app = app
#     db.init_app(app)