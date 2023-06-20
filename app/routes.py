from flask import Flask, render_template_string, request, url_for, session, redirect, render_template
import spotipy
from spotipy import SpotifyOAuth
import time
from spotipy.oauth2 import SpotifyClientCredentials
from app import app
import openai
import string
from bardapi import Bard
import os
import re

from config.config import *


os.environ['_BARD_API_KEY'] = BARD_API_KEY

# OpenAI API Key and base URL
openai.api_key = openai_api_key
openai.api_base = openai_api_base


app.config['SESSION_COOKIE_NAME']='Spotify Cookie'
app.secret_key=app_secret_key

TOKEN_INFO='token_info'


@app.route('/')
def index():
    return render_template('home.html')

@app.route('/login')
def login():
    session.clear()
    if 'access_token' in session:
        # User is already authenticated, redirect them to another page
        return redirect(url_for('search_page'))
    else:
        auth_url = create_spotify_oauth().auth_manager.get_authorize_url()
        return redirect(auth_url)
    # # Set up Spotify OAuth flow
    # sp_oauth = SpotifyOAuth(
    #     client_id='YOUR_CLIENT_ID',
    #     client_secret='YOUR_CLIENT_SECRET',
    #     redirect_uri='YOUR_REDIRECT_URI',
    #     scope='YOUR_SCOPES'
    # )

    # # Generate authorization URL
    # auth_url = sp_oauth.get_authorize_url()

    # # Redirect the user to the authorization URL
    # return redirect(auth_url)

# @app.route('/login')
# def index():
#     return "Hello, World 123!"

@app.route('/redirect')
def redirect_page():
    session.clear()
    # session.pop(TOKEN_INFO, None)
    code = request.args.get('code')
    token_info = create_spotify_oauth().auth_manager.get_access_token(code)
    
    session[TOKEN_INFO] = token_info
    # print(token_info)
    return redirect(url_for('search_page'))
# route to save the Discover Weekly songs to a playlist
# @app.route('/saveDiscoverWeekly')
# def save_discover_weekly():
#     try: 
#         # get the token info from the session
#         token_info = get_token()
#     except:
#         # if the token info is not found, redirect the user to the login route
#         print('User not logged in')
#         return redirect("/")
#     return("OAUTH SUCCESSFULL")

@app.route('/search', methods=['GET', 'POST'])
def search_page():
    # Check if the user is authenticated
    try: 
        # get the token info from the session
        token_info = get_token()
        # print(token_info)
        # print(type(token_info))
    except:
        # if the token info is not found, redirect the user to the login route
        print('User not logged in')
        return redirect("/")
    
    if isinstance(token_info, dict) and 'access_token' in token_info:
    # Create a Spotipy instance with the access token
        sp = spotipy.Spotify(auth=token_info['access_token'])
    else:

        # Handle the error condition appropriately (e.g., show an error message)
        print('Error: Invalid token_info')
        return redirect(url_for('login'))
    # if 'TOKEN_INFO' not in session:
    #     return redirect(url_for('login'))
    

    if request.method == 'POST':
        # Retrieve the form data
        search_query = request.form.get('search_query')
        print(search_query)
        session['playlist_creation_in_progress'] = True

        # Perform necessary processing or actions with the form data
        playlist_name = get_playlist_name(search_query)  # Set the desired name for your playlist
        user_id = sp.current_user()["id"]  # Get the current user's Spotify user ID
        playlist = sp.user_playlist_create(user_id, playlist_name, public=True)
        playlist_id = playlist["id"]  # Get the ID of the created playlist
        print(playlist_id)
        session['playlist_id'] = playlist_id
        print(session.get('playlist_id', None))


        make_playlist_complete(sp,search_query,playlist_id=playlist_id)

        # Redirect the user to the show playlist page
        return redirect(url_for('final_page'))

    # Render the search page template
    return render_template('search_page.html')

@app.route('/finalpage')
def final_page():
    return render_template('final_page.html')

@app.route('/homepage')
def home_page():
    if not session.get(TOKEN_INFO):
        return redirect(url_for('login'))
    
    return ('OAUTH SUCCESSFUL')

@app.route('/tracks')
def tracks_disp():
    client_credentials_manager = SpotifyClientCredentials(client_id="f23942b66b7c414285a7c4c0977ecf19", client_secret="f43c9ebb93bb4cf2b6635e37a7528e2c")
    sp = spotipy.Spotify(client_credentials_manager=client_credentials_manager)
    track_ids = ['3QFInJAm9eyaho5vBzxInN', '3QFInJAm9eyaho5vBzxInN']  # Replace with your track IDs
    tracks = sp.tracks(track_ids)['tracks']
    html_code = ''
    for track in tracks:
        # Extract track details
        track_name = track['name']
        album_name = track['album']['name']
        album_art_url = track['album']['images'][0]['url']
        spotify_url = track['external_urls']['spotify']
        
        # Generate HTML code for the track
        html_code += f"""
        <div class="song-line">
            <a href="{spotify_url}" target="_blank" class="play-button">
                <img src="play-button.png" alt="Play Button">
            </a>
            <div class="song-details">
                <h3>{track_name}</h3>
                <p>Album: {album_name}</p>
            </div>
            <a href="{spotify_url}" target="_blank" class="album-art">
                <img src="{album_art_url}" alt="{album_name} Album Art">
            </a>
        </div>
        """

    # Render the HTML code
    return render_template_string(html_code)



# @app.route('/callback')
# def callback():
#     # Process the callback after the user authorizes the app
#     sp_oauth = SpotifyOAuth(
#         client_id='YOUR_CLIENT_ID',
#         client_secret='YOUR_CLIENT_SECRET',
#         redirect_uri='YOUR_REDIRECT_URI',
#         scope='YOUR_SCOPES'
#     )

#     # Exchange the authorization code for an access token
#     code = request.args.get('code')
#     token_info = sp_oauth.get_access_token(code)

#     # Save the access token and other relevant information in the session
#     session['token_info'] = token_info

#     # Redirect the user to the playlist creation page or perform other actions

# @app.route('/create_playlist')
# def create_playlist():
#     # Retrieve the access token from the session
#     token_info = session.get('token_info')

#     # Check if the user is authenticated
#     if not token_info or not sp_oauth.is_token_expired(token_info):
#         # Redirect the user to the login page
#         return redirect(url_for('login'))

#     # Create the playlist using the Spotify API
#     # Use the access token to make authenticated requests to the API

#     return "Playlist created successfully"

# Other routes and functions for playlist management can be defined here

def get_token():
    token_info = session.get(TOKEN_INFO, None)
    if not token_info:
        return redirect(url_for('login', _external=False))  # Return the redirect response
    print(token_info)
    # now = int(time.time())
    # ¸print(type(token_info))
    # is_expired = token_info['expires_at'] - now < 60
    # if is_expired:
    #     spotifyoauth = create_spotify_oauth()
    #     token_info = spotifyoauth.refresh_access_token(token_info['refresh_token'])

    return token_info

    
    


def create_spotify_oauth():
    return spotipy.Spotify(auth_manager=SpotifyOAuth(scope='playlist-modify-public', client_id=spotify_client_id, client_secret=spotify_client_secret, redirect_uri=spotify_redirect_uri, cache_path=False))

    

def get_playlist_name(user_input):
    response = openai.Completion.create(
    model="text-davinci-003",
    prompt="I want you to give me a catchy name for a playlist based on songs similar to '" + user_input + "'. Just reply with the playlist name and nothing else",
    temperature=0.7,
    max_tokens=256,
    top_p=1,
    frequency_penalty=0,
    presence_penalty=0,
    stop=["Human: ", "AI: "]
    )
    name=response.choices[0].text
    title=re.sub(r'[\n"\.]', '', name)
    
    return(title.strip())

def create_chatgpt_playlist(gpt_prompt):
    response = openai.Completion.create(
    model="text-davinci-003",
    prompt=gpt_prompt,
    temperature=0.7,
    max_tokens=256,
    top_p=1,
    frequency_penalty=0,
    presence_penalty=0,
    stop=["Human: ", "AI: "]
    )
    a=response.choices[0].text
    
    q=a.split('\n')
        
    q = [item for item in q if item and item.strip(string.whitespace)]

    # print(q)
    songs = []
    for line in q[1:]:
        parts = line.split(' - ')  # Split by " - " to separate song name and artists
        artist = parts[1]  # Extract the song name
        if ('.' in parts[0]):
            song_name = parts[0].split('. ')[1]
        else:
            song_name = parts[0]
        
          # Extract the artist
        songs.append([song_name, artist])
    return songs

def run_function_until_correct_output_gpt(gpt_prompt):
    tries=0
    output=['']
    while (tries<10):
        try:
            output = create_chatgpt_playlist(gpt_prompt=gpt_prompt)
            if len(output)>=10:
                # Process the correct output
                return output
                break  # Exit the loop if the output is correct
        except Exception as e:
            # Handle the exception (optional)
            print("Exception occurred:", str(e))
            tries = tries+1
            # Continue to the next iteration of the loop
    return output

def create_bard_playlist(bard_prompt):
    ans=(Bard().get_answer(bard_prompt)['content'])
    pattern = r'[^a-zA-Z0-9\s\[\].-]'
    cleaned_string = re.sub(pattern, '', ans)
    lines = cleaned_string.split('\n')
    lines=[item for item in lines if item != '']
    # print(lines)
    title=lines[1]
    if ('name'  in  title.lower()):
        name=title.split(' ')[1]
        playlist_name=title.split(name)
        title=playlist_name[1]
    # title=lines[1]
    songs_and_artists=[]
    for line in lines:
        line=line.strip()
        if '-' in line and (('[' or ']') not in line ):
            # line=line.strip('[')
            # line= line.strip(']')
            line=line.split('-')
            song= (line[0].split('.'))[1].strip()
            artist=(line[1]).strip()
            songs_and_artists.extend([[song,artist]])
        # songs.append(line[0])
        # artists.append(line[1])
    return songs_and_artists


def run_function_until_correct_output_bard(prompt):
    count=0
    output=['']
    while (count<10):
        try:
            output = create_bard_playlist(prompt)
            if len(output)>=10 :
                # Process the correct output
                return(output)
                break  # Exit the loop if the output is correct
        except Exception as e:
            # Handle the exception (optional)
            print("Exception occurred:", str(e))
            count = count+1
            # Continue to the next iteration of the loop
    return output

def prep_list_for_spotify(song_and_artist_list)  : 
    final_list=[]
    for i in song_and_artist_list:
        final_list.append({'name': i[0],'artist':i[1]})
    return final_list



def make_playlist(sp,song_list, playlist_id):
    track_uris = []

    # Iterate over the songs and search for each one
    for song in song_list:
        query = f"track:{song['name']} artist:{song['artist']}"
        results = sp.search(q=query, type='track', limit=1)

        if results['tracks']['items']:
            track = results['tracks']['items'][0]
            track_uris.append(track['uri'])
        else:
            # Retry search using just the name of the song
            query = f"track:{song['name']}"
            results = sp.search(q=query, type='track', limit=1)

            if results['tracks']['items']:
                track = results['tracks']['items'][0]
                track_uris.append(track['uri'])

    # Add the tracks to the playlist
    sp.playlist_add_items(playlist_id, track_uris)
    print("Playlist Created Successfully")


def make_playlist_complete(sp_instance,user_prompt, playlist_id):
    songs=[]
    gpt_prompt_1="Human: I want you to act as a song recommender expert. I will provide you with a song and you will create a playlist of 10 songs that are similar to the given song. And you will provide a playlist name. You should not choose songs that have the same artist or the same name. Do not write any explanations or other words, just reply with the playlist name and the list of songs and their artists in the format [song name - artist]. My first song is ' "
    gpt_prompt_2=" ' \n AI: "
    final_gpt_prompt= gpt_prompt_1+user_prompt+gpt_prompt_2
    bard_prompt_1="I want you to act as a song recommender expert.Do not write any explanations, just reply with the name of the playlist and a numbered list containing the name of song and the artist in this specific format ' Song name - Artist ' and nothing else. I will provide you with a song and you will create a playlist of 10 songs that are similar to the given song and artist. You should not choose songs that are same artist or the same name. My first song is ' "
    bard_prompt_2= " ' "
    final_bard_prompt= bard_prompt_1+user_prompt+bard_prompt_2
    print(final_gpt_prompt)
    songs=(run_function_until_correct_output_gpt(gpt_prompt=final_gpt_prompt))
    print(final_bard_prompt)
    songs.extend(run_function_until_correct_output_bard(final_bard_prompt))

    song_list=prep_list_for_spotify(songs)

    make_playlist(sp=sp_instance,song_list=song_list,playlist_id=playlist_id)