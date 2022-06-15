from flask import Flask, render_template, send_from_directory
from PIL import Image, ImageFont, ImageDraw
import spotipy
from spotipy.oauth2 import SpotifyOAuth

app = Flask(__name__)

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/privacy.html')
def privacy():
    return render_template('privacy.html')

@app.route('/berg.html')
def berg():
    ###AUTHENTICATION

    cid = "807e4b747d9c4264b87542e38019d4c9" 
    secret = "c752248925b0473a90ed87a9b180ea67"
    redirect = 'http://localhost:8888/callback'
    scope = 'user-top-read'

    sp = spotipy.Spotify(auth_manager=SpotifyOAuth(client_id=cid, client_secret=secret, redirect_uri=redirect, scope=scope))

    ###CREATE ICEBERG

    name = sp.current_user()['display_name']
    if  ' ' in name:
        name = name[:name.index(' ')]
    if '.' in name:
        name = name[:name.index('.')]

    data = []
    for term in ["long_term", "medium_term", "short_term"]:
        data.append(sp.current_user_top_artists(limit=50, offset=0, time_range=term))

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

    ###DRAW ICEBERG
    for section, artists in iceberg.items():
        artists_sorted = (sorted(artists, key=len))
        artists_sorted.reverse()
        iceberg[section] = artists_sorted

    iceberg_img = Image.open("iceberg_blank.jpg")
    image = ImageDraw.Draw(iceberg_img)
    intro_font = ImageFont.truetype("Intro Regular Regular.ttf", 55)

    iceberg_img2 = Image.open("iceberg_blank2.jpg")
    image2 = ImageDraw.Draw(iceberg_img2)

    coordinates = {}
    coordinates['eighth'] = [[350, 335], [30,270], [640, 425], [150,415], [800,260]]
    for i in range(6,-1,-1):
        if sections[i][1] != 'sixth':
            coordinates[sections[i][1]] = []
            for j in range(5):
                coordinates[sections[i][1]].append([coordinates[sections[i+1][1]][j][0], coordinates[sections[i+1][1]][j][1] + 256])
        elif sections[i][1] == 'sixth':
            coordinates[sections[i][1]] = []
            for j in range(5):
                coordinates[sections[i][1]].append([coordinates[sections[i+1][1]][j][0], coordinates[sections[i+1][1]][j][1] + 271])

    for section in sections:
        count = 0
        for artist in iceberg[section[1]]:
            image2.text(tuple(coordinates[section[1]][count]), artist, (230, 54, 41), intro_font)
            count += 1

    ###TITLE
    intro_font_big = ImageFont.truetype("Intro Regular Regular.ttf", 100)
    image2.text((25, 20), name + "'s Spotify", (19, 81, 143), intro_font_big)
    image2.text((195, 120), "Iceberg", (19, 81, 143), intro_font_big)

    ###SAVING
    sid = sp.current_user()['id']
    bergname = "result" + str(sid) + ".jpg"
    iceberg_img2.save("data/" + str(bergname))

    return render_template('berg.html', value=bergname)

@app.route('/data/<filename>')
def display_image(filename):
    return send_from_directory('data', filename, as_attachment=True)

app.run(host='localhost', port=5000)