#  🏡🛖🏘️ shareBnB 🏠🏚️🖼️

#### AirBnB inspired clone

## Technologies:

* Language: Python
* Web framework: Flask
* ORM: SQLAlchemy
* Additional: Brypt, JWT, Unittests, AWS S3 bucket

## Features:

* Users registration and login with JWT
* Users CRUD listings of a property
* Users can send messages about a listing to the host
* Users can edit their own profile
* Search for listings

## Set Up:

1. Clone or fork this repository and python is installed on computer

2. Setup a Python virtual environment 
 
 * ```$ python3 -m venv venv```
 * ```$ source venv/bin/activate```
 * ```(venv) $ pip3 install -r requirements.txt```

3. Set up data and seed your database(this application uses psql)
* ```(venv) $ psql```
* ```=# CREATE DATABASE sharebnb;```
* ```*ctrl d*```
* ```(venv) python3 seed.py*```

4. Create .env in the project directory with the two variable below

* ```JWT_SECRET_KEY="this-is-a-secret-shhhh"```
* ```DATABASE_URL=postgresql:///sharebnb```

5. Start the server by running

* ```$ flask run```
    * Mac users, port 5000 might be taken by another application to run on another port use the command below
    * ```$ flask run -p 5001```

6. View application by going to http://localhost:5000 or http://localhost:5001 on your browser

7. Available Routes:

POST: /auth/login

POST: /auth/signup

GET/PATCH/DELETE: /users

GET: /messages/:id

POST: /messages

GET/POST/PATCH/DELETE: /listings

GET/POST/DELETE: /bookings
