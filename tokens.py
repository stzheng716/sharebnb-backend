# import jwt
# from jwt.exceptions import InvalidTokenError
# import os

# def createToken(user):
#     """return signed JWT {username, isAdmin} from user data"""

#     payload ={
#     "username": user.username,
#     "isHost": user.isHost
#     }

#     return jwt.encode(payload, os.environ['SECRET_KEY'], algorithm="HS256")

# def authenitcateJWT(token):
    
#     if(token):
#         try:
#             decoded_token = jwt.decode(token, os.environ['SECRET_KEY'], algorithm=["HS256"])
#         except InvalidTokenError:
#             return False
    
#     return decoded_token.payload.username
    
