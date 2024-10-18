import googlemaps
import os
import json
import time
import haversine

gmaps = googlemaps.Client(key= os.environ['GOOGLE_API_KEY'])

def getBusinessesForCity(city, business_type):
    geocode_result = gmaps.geocode(city)
    print(json.dumps(geocode_result))
    if len(geocode_result) == 1:

        northeast = geocode_result[0]['geometry']['bounds']['northeast']
        southwest = geocode_result[0]['geometry']['bounds']['southwest']
        grid_cell_width = (northeast.get('lng') - southwest.get('lng'))/10
        grid_cell_height = (northeast.get('lat') - southwest.get('lat'))/10
        businesses = []
        #divide the city into a grid of 10x10
        for x in range(0, 1):
            for y in range(0, 1):
                businesses = []
                f = open("%s-%d-%d.json" % (city, x,y), "w")
                #find places in the grid
                businesses = businesses + find_businesses_in_bounds( business_type,
                    {
                        "lat": float(northeast.get('lat') - grid_cell_height * (y)),
                        "lng": float(northeast.get('lng') - grid_cell_width * (x))
                    },
                    {
                        "lat": float(northeast.get('lat') - grid_cell_height * (y+1)),
                        "lng": float(northeast.get('lng') - grid_cell_width * (x+1))
                    })
                f.write(json.dumps(businesses, indent=2))
                f.close()
        
        
        
        

def find_businesses_in_bounds(business_type, northeast:dict, southwest:dict) :
    businesses = []
    #start from the center of the bounds
    center = {
        'lat': ((float(northeast.get('lat') - southwest.get('lat'))) / 2 ) + float(southwest.get('lat')),
        'lng': ((float(northeast.get('lng') - southwest.get('lng'))) / 2 ) + float(southwest.get('lng')),
    }
    #set the radius to the distance between the northeast and southwest corners
    radius = (haversine.haversine((northeast['lat'], northeast.get('lng')), (center['lat'], center.get('lng'))))*1000
    print ("Searching for businesses in the bounds (%s %s) with radius %f" % (center['lat'], center['lng'], radius))
    places = gmaps.places( 
            business_type,
            location=(center['lat'], center['lng']),
            radius=radius
        )
    businesses = businesses + find_details_in_radius(places['results'], center, northeast, southwest);
    while(places.get('next_page_token')):
        time.sleep(2)
        places = gmaps.places(
            business_type,
            location=(center['lat'], center['lng']),
            radius=radius,
            page_token=places['next_page_token']
        )
        businesses = businesses + find_details_in_radius(places['results'], center, northeast, southwest);
    print("Found %d businesses in the bounds" % len(businesses))
    return businesses;

def find_details_in_radius(results, center, northeast:dict, southwest:dict):
    businesses = []
    for place in results:
        details = find_dentist_details(place, center, northeast, southwest)
        if(details != None):
            businesses.append(details)
    return businesses

def find_dentist_details(dentist, center, northeast:dict, southwest:dict):
    #distance_from_center = haversine.haversine((dentist['geometry']['location']['lat'], dentist['geometry']['location']['lng']), (center['lat'], center['lng']))
    lat = dentist['geometry']['location']['lat']
    lng = dentist['geometry']['location']['lng']
    
    if(lat <= northeast['lat'] and lat >= southwest['lat'] and 
       lng <= northeast['lng'] and lng >= southwest['lng']):
        details = dentist
        place_details = gmaps.place(dentist['place_id'], fields=['name', 'formatted_address', 'formatted_phone_number', 'website', 'reviews'])
        dentist['details'] = place_details['result']
        return details
    return None