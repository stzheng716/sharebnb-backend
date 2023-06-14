from cities import cities

cityTest = "Daly City"

def geoCoder(city):

    coordinates = [{"latitude": cityInfo["latitude"], 
            "longitude": cityInfo["longitude"]} 
            for cityInfo in cities if cityInfo["city"] == city]
    
    return coordinates[0]