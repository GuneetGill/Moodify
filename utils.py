
'''
takes in a playlist and gives back a mood 
'''
def show_tracks(sp, playlist_id):
    tracks = sp.playlist_items(playlist_id, fields="items(track(id,name,artists(name),album(name,images))),next")
    tracks_info = []
    cover_art_urls = []
    
    mood_counts = {
        "Melancholic": 0,
        "Sad": 0,
        "Calm": 0,
        "Peaceful": 0,
        "On Top of the World": 0,
        "Electric": 0,
        "Euphoric": 0,
        "Happy": 0,
        "Angry": 0,
        "Joyful": 0,
        "Relaxed": 0,
        "Intense": 0,
        "Neutral": 0
    }
    
    processed_items = 0
    max_items = 25 # Maximum number of items to process

    while processed_items < max_items:
        for item in tracks['items']:
            if processed_items >= max_items:
                break
            track = item['track']
            if track and 'id' in track and 'name' in track and 'artists' in track:
                track_id = track['id']
                track_name = track['name']
                artist_name = ', '.join(artist['name'] for artist in track['artists'])
                album_name = track['album']['name']
                
                images = track['album']['images']
                cover_art_urls.append(images[0])
                

                tracks_info.append(f"track name: {track_name}  artist: {artist_name}  album: {album_name}")
                mood = analyze_song(sp, track_id)
                mood_counts[mood] += 1 
                
                processed_items += 1
                
        if tracks['next'] and processed_items < max_items:
            tracks = sp.next(tracks)
        else:
            break
    
    # Check if all counts are 0
    if all(count == 0 for count in mood_counts.values()):
        final_mood = "Neutral"
    else:
        final_mood = max(mood_counts, key = mood_counts.get)
    
    return final_mood, tracks_info , cover_art_urls
    


'''
takes in recently played songs and gives final mood 
'''
def recent_tracks(sp):
    tracks = sp.current_user_recently_played(limit=20)
    num_tracks_fetched = len(tracks.get('items', []))

    mood_counts = {
        "Melancholic": 0,
        "Sad": 0,
        "Calm": 0,
        "Peaceful": 0,
        "On Top of the World": 0,
        "Electric": 0,
        "Euphoric": 0,
        "Happy": 0,
        "Angry": 0,
        "Joyful": 0,
        "Relaxed": 0,
        "Intense": 0,
        "Neutral": 0
    }
    
    limit = min(6, num_tracks_fetched)
    cover_art_urls = []
    song_info = []

    for item in tracks['items']:
        track = item['track']
        if track and 'id' in track:
            track_id = track['id']
            track_name = track['name']
            mood = analyze_song(sp, track_id)
            print("analyze_song is being called")

            if len(cover_art_urls) < limit:
                album = track['album']
                if 'images' in album and len(album['images']) > 0:
                    cover_art_urls.append(album['images'][0]['url'])

                artist = track['artists'][0]['name']
                song_info.append((track_name, artist))
            
            print(f"Track ID: {track_id}, Track Name: {track_name}, Mood: {mood}")
            mood_counts[mood] += 1 

        if tracks['next']:
            tracks = sp.next(tracks)
        else:
            break

    if all(count == 0 for count in mood_counts.values()):
        final_mood = "Neutral"
    else:
        final_mood = max(mood_counts, key=mood_counts.get)
    
    print(f"Final Mood: {final_mood}")
    print(f"Cover Art URLs: {cover_art_urls}")
    print(f"Song Info: {song_info}")

    return final_mood, cover_art_urls, song_info


'''
intakes spotify api returns cover art url
'''
def cover_art(sp):
    tracks = sp.current_user_recently_played()['items']
    cover_art_urls = []

    for item in tracks:
        track = item['track']
        
        if track and 'id' in track:
            album = track['album']
            if 'images' in album and len(album['images']) > 0:
                cover_art_urls.append(album['images'][0]['url'])

    return cover_art_urls

'''gives songs along with artist name as a list '''
def song_info(sp):
    tracks = sp.current_user_recently_played()['items']
    song_info = []

    for item in tracks:
        track = item['track']
        
        #get artist name and track name 
        if track and 'artists' in track:
            artist = track['artists'][0]['name']  # Get the first artist's name
            song = track['name']
            song_info.append((song, artist))  # Append as a tuple

    return song_info

'''
takes in song track_id and extracts elements from spotify audio features to determine the mood of a song 
'''      
def analyze_song(sp, track_id):
    features = sp.audio_features(track_id)
    if not features:
        return "Unknown audio feature"

    extracted_features_list = [
        {
            'acousticness': round(feature['acousticness'], 3),
            'danceability': round(feature['danceability'], 3),
            'energy': round(feature['energy'], 3),
            'loudness': round(normalize_loudness(feature['loudness']), 3),
            'valence': round(feature['valence'], 3)
        }
        for feature in features
    ]

    song_datas = extracted_features_list[0]
    acousticness = song_datas["acousticness"]
    danceability = song_datas["danceability"]
    energy = song_datas["energy"]
    loudness = song_datas["loudness"]
    valence = song_datas["valence"]

    if (acousticness >= 0.50 and valence <= 0.3):
        if (energy <= 0.35):
            mood = "Melancholic"
        else:
            mood = "Sad"
    elif (acousticness >= 0.5 and valence <= 0.45):
        if (energy <= 0.45):
            mood = "Calm"
        else:
            mood = "Peaceful"
    elif (acousticness <= 0.2 and danceability >= 0.6):
        if (energy >= 0.8):
            if (loudness >= 0.93):
                mood = "On Top of the World"
            else:
                mood = "Electric"
        else:
            if (energy >= 0.60 and loudness >= 0.8):
                mood = "Euphoric"
            else:
                mood = "Happy"
    elif (acousticness <= 0.1 and danceability <= 0.6 and energy >= 0.8 and loudness >= 0.9):
        mood = "Angry"
    elif (danceability > 0.7 or energy > 0.7 or valence > 0.7):
        mood = "Joyful" 
    elif (acousticness > 0.3 and energy < 0.5 or valence > 0.5):
        mood = "Relaxed"
    elif (energy > 0.8 and valence < 0.2):
        mood = "Intense"
    else:
        mood = "Neutral"
        
    return mood


def normalize_loudness(loudness, min_loudness=-60, max_loudness=0):
    return (loudness - min_loudness) / (max_loudness - min_loudness)