"""
 The purpose of this code is to show how to work with plant.id API.
 You'll find API documentation at https://plantid.docs.apiary.io and https://plant.id/api
"""

import base64
from json import JSONDecodeError
from os import walk
from geopy.geocoders import Nominatim
import requests


secret_access_key = 'lKl8qiY80fYB9UHbJb1Gap6yC0uYF5tzattg8k3SkxIeYHAfW5'

def encode_file(file_name):
    with open(f"images/{file_name}", "rb") as file:
        return base64.b64encode(file.read()).decode("ascii")

def send_for_identificattion(file_names):
    # calling the Nominatim tool
    loc = Nominatim(user_agent="GetLoc")
    location = input("Introduce la localización: ")
    getLoc = loc.geocode(location)
    latitude = getLoc.latitude
    longitude = getLoc.longitude
    
    print(f"{location} latitude is {latitude} and longitude is {longitude}")
    
    # files_encoded = []
    # for file_name in file_names:
    #     with open(f"images/{file_name}", 'rb') as file:
    #         files_encoded.append(base64.b64encode(file.read()).decode('ascii'))

    params = {
        'latitude': latitude,
        'longitude': longitude,
        'images': [encode_file(img) for img in file_names],
        'Api-Key': secret_access_key,
        'modifiers': ["crops_fast", "similar_images"]
    }
    # see the docs for more optinal atrributes; for example 'custom_id' allows you to work
    # with your own identifiers
    headers = {
        'Content-Type': 'application/json',
        'Api-Key': secret_access_key,
    }

    response = requests.post(
        'https://api.plant.id/v2/enqueue_identification', json=params, headers=headers)

    if response.status_code != 200:
        print(response.text)

    print(response.json().get('id'))

    return response.json().get('id')


def get_suggestions(request_ids):
    params = {
        "ids": [request_ids]
    }
    headers = {
        'Content-Type': 'application/json',
        'Api-Key': secret_access_key,
    }

    # To keep it simple, we are pooling the API waiting for the server to finish the identification.
    # The better way would be to utilise "callback_url" parameter in /identify call to tell the our server
    # to call your's server enpoint once the identificatin is done.
    while True:
        print("Waiting for suggestions...")
        # sleep(5)
        try:
            resp = requests.post(
                f'https://api.plant.id/v2/get_identification_result/multiple', json=params, headers=headers).json()

        except JSONDecodeError:
            print(resp.text)

        if resp[0]["suggestions"]:
            return resp[0]["suggestions"]

mypath = r"images"
filenames = next(walk(mypath), (None, None, []))[2]  # [] if no file -> List
# more photos of the same plant increases the accuracy
request_id = send_for_identificattion(file_names=filenames) # -> List

result = get_suggestions(request_id)

similar_images = []
for res in result[0].get('similar_images'):
    similar_images.append((round(res.get('similarity') * 100, 2) ,res.get('url')))

# just listing the suggested plant names here (without the certainty values)
for r, suggestion in enumerate(result):
    plant_id = suggestion.get("id")
    plant_sugg_name = suggestion.get("plant_name")
    common_names = suggestion.get("plant_details").get("common_names")
    match_accuracy = round(suggestion.get("probability") * 100, 2)
    confirmed = suggestion.get("confirmed")
    try:
        wiki_image = suggestion.get("plant_details").get("wiki_image").get("value")
    except AttributeError:
        wiki_image = None
        
    # similar_images = suggestion.get('similar_images')[0].get('url')

    print(f"\nSuggestion {r} info with id {plant_id}:")
    print(f"    - Name: {plant_sugg_name}")
    print(f"    - Common names: {common_names}")
    print(f"    - Accuracy: {match_accuracy}%")
    print(f"    - Confirmed?: {confirmed}")
    print(f"    - Wiki image: {wiki_image}")
    print(f"    - Similar images: {similar_images}")
