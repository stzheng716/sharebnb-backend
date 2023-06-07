import jwt
import os

def createToken(user):
    """return signed JWT {username, isAdmin} from user data"""

    payload ={
    "username": user.username,
    "isHost": user.isHost
    }

    return jwt.encode(payload, os.environ['SECRET_KEY'])
