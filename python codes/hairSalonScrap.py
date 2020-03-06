FOURSQUARE_CLIENT_ID = 'MBY2IO5RI50UABQEYPGDW20C1HGJFACXJG24WB5JTIYJTILJ'# use your own client id
FOURSQUARE_CLIENT_SECRET = 'RVV0ANL0IJQMYZYZBPDXPOEI1F22FKHFWCIUULBRJA22AL03'# use your own client secret
RADIUS = 10000  #
NO_OF_VENUES = 100
VERSION = '20200105'  # Current date
LATITUDE = '12.9716'
LONGITUDE = '77.5946'


def get_category_type(row):
    try:
        categories_list = row['categories']
    except:
        categories_list = row['venue.categories']

    if len(categories_list) == 0:
        return None
    else:
        return categories_list[0]['name']


import pandas as pd

from pandas.io.json import json_normalize
import requests

pd.set_option('display.max_rows', None)

offset = 0
total_venues = 0
foursquare_venues = pd.DataFrame(columns=['name', 'categories', 'lat', 'lng'])

while True:
    url = ('https://api.foursquare.com/v2/venues/explore?categoryId=4bf58dd8d48988d110951735&client_id={}'
           '&client_secret={}&v={}&ll={},{}&radius={}&limit={}&offset={}').format(FOURSQUARE_CLIENT_ID,
                                                                                  FOURSQUARE_CLIENT_SECRET,
                                                                                  VERSION,
                                                                                  LATITUDE,
                                                                                  LONGITUDE,
                                                                                  RADIUS,
                                                                                  NO_OF_VENUES,
                                                                                  offset)
    print(url)
    result = requests.get(url).json()
    venues_fetched = len(result['response']['groups'][0]['items'])
    total_venues = total_venues + venues_fetched
    print("Total {} venues fetched within a total radius of {} Km".format(venues_fetched, RADIUS / 1000))

    venues = result['response']['groups'][0]['items']
    venues = json_normalize(venues)

    # Filter the columns
    filtered_columns = ['venue.name', 'venue.categories', 'venue.location.lat', 'venue.location.lng']
    venues = venues.loc[:, filtered_columns]

    # Filter the category for each row
    venues['venue.categories'] = venues.apply(get_category_type, axis=1)

    # Clean all column names
    venues.columns = [col.split(".")[-1] for col in venues.columns]
    foursquare_venues = pd.concat([foursquare_venues, venues], axis=0, sort=False)

    if venues_fetched < 100:
        break
    else:
        offset = offset + 100

foursquare_venues = foursquare_venues.reset_index(drop=True)
print("\nTotal {} venues fetched".format(total_venues))
print(foursquare_venues)
