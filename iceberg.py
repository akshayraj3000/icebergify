import requests
from PIL import Image, ImageFont, ImageDraw
import os
import spotipy
from spotipy.oauth2 import SpotifyClientCredentials
import spotipy.util as util

###AUTHENTICATION

cid = "807e4b747d9c4264b87542e38019d4c9" 
secret = "c752248925b0473a90ed87a9b180ea67"

os.environ['SPOTIPY_CLIENT_ID'] = cid
os.environ['SPOTIPY_CLIENT_SECRET'] = secret
os.environ['SPOTIPY_REDIRECT_URI'] = 'http://example.com/callback/'

username = ""
client_credentials_manager = SpotifyClientCredentials(client_id = cid, client_secret = secret) 
sp = spotipy.Spotify(client_credentials_manager = client_credentials_manager)
scope = 'user-top-read'
access_token = util.prompt_for_user_token(username, scope)

###CREATE ICEBERG

def get_artists():
    terms = ["long_term", "medium_term", "short_term"]
    data = []
    for term in terms:
        user_url = 'https://api.spotify.com/v1/me/top/artists?time_range=' + str(term) + '&limit=50&offset=0'
        response = requests.get(user_url, headers = {"Authorization": f"Bearer {access_token}"})
        json_resp = response.json()
        data.append(json_resp)

    return data

# long_term - several years
# medium_term - six months
# short_term - weeks to a month

data = get_artists()

#print(data[0]['items'][0]['name'])

artists = {}

for i in range(3):
    for j in range(len(data[i]['items'])):
        artists[data[i]['items'][j]['name']] = data[i]['items'][j]['popularity']


sections = [(16,'first'),(28,'second'),(40,'third'),(52,'fourth'),(64,'fifth'),(76,'sixth'),(88,'seventh'),(100,'eighth')]
iceberg = {'first':[], 'second':[], 'third':[], 'fourth':[], 'fifth':[], 'sixth':[], 'seventh':[], 'eighth':[]}
min_pop = 0
for max_pop in sections:
    for artist, pop in artists.items():
        if (pop <= max_pop[0]) and (pop > min_pop) and len(iceberg[max_pop[1]]) < 5:
            iceberg[max_pop[1]].append(artist)
    min_pop = max_pop[0]

print(iceberg)

iceberg_img = Image.open("iceberg_blank.jpg")
image = ImageDraw.Draw(iceberg_img)
arial = ImageFont.truetype("arial.ttf", 55)

coordinates = {}
coordinates['eighth'] = [(30,30), (150,160), (350, 95), (640, 170), (730,20)]
coordinates['seventh'] = [(30,30 + 256), (150,160 + 256), (350, 95 + 256), (640, 170 + 256), (730,20 + 256)]
coordinates['sixth'] = [(30,30 + 527), (150,160 + 527), (350, 95 + 527), (640, 170 + 527), (730,20 + 527)]
coordinates['fifth'] = [(30,30 + 783), (150,160 + 783), (350, 95 + 783), (640, 170 + 783), (730,20 + 783)]
coordinates['fourth'] = [(30,30 + 1039), (150,160 + 1039), (350, 95 + 1039), (640, 170 + 1039), (730,20 + 1039)]
coordinates['third'] = [(30,30 + 1295), (150,160 + 1295), (350, 95 + 1295), (640, 170 + 1295), (730,20 + 1295)]
coordinates['second'] = [(30,30 + 1541), (150,160 + 1541), (350, 95 + 1541), (640, 170 + 1541), (730,20 + 1541)]
coordinates['first'] = [(30,30 + 1807), (150,160 + 1807), (350, 95 + 1807), (640, 170 + 1807), (730,20 + 1807)]

for section in sections:
    count = 0
    for artist in iceberg[section[1]]:
        image.text(coordinates[section[1]][count], artist, (230, 54, 41), arial)
        count += 1


iceberg_img.save("result.jpg")



