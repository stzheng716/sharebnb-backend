from geopy.geocoders import Nominatim

#TODO: need error handling
def getGeoCode(address):
    geolocator = Nominatim(user_agent="sharebnb")
    location = geolocator.geocode(address)

    return {"latitude": location.latitude, "longitude": location.longitude}