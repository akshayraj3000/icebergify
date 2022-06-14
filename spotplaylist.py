import requests


SPOTIFY_CREATE_PLAYLIST_URL = 'https://api.spotify.com/v1/users/3si8wjd0feh3dnofgcqj2kyj0/playlists'
ACCESS_TOKEN = ''

def make_playlist(name, public):
    response = requests.post(SPOTIFY_CREATE_PLAYLIST_URL, headers = {"Authorization": f"Bearer {ACCESS_TOKEN}"}, json = {"name":name, "public":public})
    json_resp = response.json()
    return json_resp

playlist = make_playlist('test playlist', False)
new_id = playlist['id']

playlist_url = 'https://api.spotify.com/v1/playlists/' + str(new_id) +'/tracks'

song_list = ['spotify:track:4IO2X2YoXoUMv0M2rwomLC']

def add_song(songs):
    response = requests.post(playlist_url, headers = {"Authorization": f"Bearer {ACCESS_TOKEN}"}, json = {"uris":songs})
    json_resp = response.json()
    return json_resp

add_song(song_list)

# def get_playlist_data(playlist):
#     response = requests.get(playlist_url, headers = {"Authorization": f"Bearer {ACCESS_TOKEN}"}, json = {})
