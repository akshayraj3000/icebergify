from flask import Flask, render_template, send_from_directory, redirect, session, request
from PIL import Image, ImageFont, ImageDraw
import tekore as tk
from werkzeug.middleware.proxy_fix import ProxyFix
from flask_session import Session
from fontTools.ttLib import TTFont
from fontTools.unicode import Unicode

app = Flask(__name__)
app.config['SECRET_KEY'] = ''
app.config['SESSION_TYPE'] = 'filesystem'
Session(app)

app.wsgi_app = ProxyFix(app.wsgi_app)

cid = ""
secret = ""
#redirect_uri = 'http://164.92.148.45:5000/callback'
redirect_uri = 'https://icebergify.com/callback'

cred = tk.Credentials(client_id=cid,client_secret=secret,redirect_uri=redirect_uri,sender=None, asynchronous=None)
sp = tk.Spotify()

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/privacy.html')
def privacy():
    return render_template('privacy.html')

@app.route('/about.html')
def about():
    return render_template('about.html')

@app.route('/berg.html')
def berg():
    ###AUTHENTICATION
    user = session.get('state', None)
    token = session.get('token', None)

    if user is None or token is None:
        session.pop('state', None)#
        return redirect('/login')

    if token.is_expiring:
        token = cred.refresh(token)

    with sp.token_as(token):
        ###CREATE ICEBERG

        name = sp.current_user().display_name
        if  ' ' in name:
            name = name[:name.index(' ')]
        if '.' in name:
            name = name[:name.index('.')]

        artists = {}
        for term in ["long_term", "medium_term", "short_term"]:
            temp_artists = sp.current_user_top_artists(limit=50, offset=0, time_range=term)
            for artist in temp_artists.items:
                artists[artist.name] = artist.popularity

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

        ###FONT WORK
        intro = ImageFont.truetype("Intro Regular Regular.ttf", 55)
        noto = ImageFont.truetype("NotoSans-Regular.ttf", 55)
        korean = ImageFont.truetype("NotoSansKR-Regular.otf", 55)
        japanese = ImageFont.truetype("rounded-mgenplus-1cp-regular.ttf", 55)

        intro_ttf = TTFont('Intro Regular Regular.ttf')
        noto_ttf = TTFont('NotoSans-Regular.ttf')
        korean_ttf = TTFont('NotoSansKR-Regular.otf')
        japanese_ttf = TTFont('rounded-mgenplus-1cp-regular.ttf')

        def has_glyph(font, glyph):
            for table in font['cmap'].tables:
                if ord(glyph) in table.cmap.keys():
                    return True
            return False

        def print_artist(artist):
            count = 0
            for char in artist:
                if has_glyph(intro_ttf, char):
                    count += 1
            if count == len(artist):
                return(intro)
            
            count = 0
            for char in artist:
                if has_glyph(noto_ttf, char):
                    count += 1
            if count == len(artist):
                return(noto)

            count = 0
            for char in artist:
                if has_glyph(korean_ttf, char):
                    count += 1
            if count == len(artist):
                return(korean)

            count = 0
            for char in artist:
                if has_glyph(japanese_ttf, char):
                    count += 1
            if count == len(artist):
                return(japanese)
            
            return(intro)
        
        ###
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
                image2.text(tuple(coordinates[section[1]][count]), artist, (230, 54, 41), print_artist(artist))
                count += 1

        ###TITLE
        intro_font_big = ImageFont.truetype("Intro Regular Regular.ttf", 100)
        image2.text((25, 20), name + "'s Spotify", (19, 81, 143), intro_font_big)
        image2.text((195, 120), "Iceberg", (19, 81, 143), intro_font_big)

        ###SAVING
        sid = sp.current_user().id
        bergname = "result" + str(sid) + ".jpg"
        iceberg_img2.save("data/" + str(bergname))

    return render_template('berg.html', value=bergname)

@app.route('/login', methods=['GET'])
def login():
    if session.get('token', None) is not None:
        return redirect('/berg.html')

    scope = tk.scope.user_top_read
    auth = tk.UserAuth(cred, scope)
    #session['auth'] = auth.__dict__
    return redirect(auth.url)

@app.route('/callback', methods=['GET'])
def callback():
    code = request.args.get('code')
    state = request.args.get('state')

    #check if state matches auth state somehow
    token = cred.request_user_token(code)
    #token = auth.request_token(code, state)
    session['state'] = state
    session['token'] = token
    return redirect('/berg.html')

@app.route('/data/<filename>')
def display_image(filename):
    return send_from_directory('data', filename, as_attachment=True)

if __name__ == "__main__":
    app.run(host='0.0.0.0')
