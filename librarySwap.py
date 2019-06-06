import requests
import json
import sys
import shelve
from gmusicapi import Mobileclient
from datetime import datetime
mc = Mobileclient(debug_logging=False)

def main():
    """"""
    #Options: Either run whole, or export songs from spotify or import songs to gplay
def getSongsFromSpotify():
    """Cycles through songs in a spotify library and creates a list of dictionaries where each dictionary represents a single song.
    For example:  
    {
        "title": "If I'm Lyin, I'm Flyin",
        "artists": [
            "Kodak Black"
        ]
        This function will return the list of songs and output a json file containing the same
        """
    print("Request an access token at the following address: https://developer.spotify.com/console/get-current-user-saved-tracks/?market=&limit=&offset=")
    key = input("Enter your Spotify authorization token: ")
    url = 'https://api.spotify.com/v1/me/tracks'
    headers = {'Authorization': 'Bearer '+ key}
    parameters = {'limit':'50', 'offset':'0'}
    nextPage = ""
    songs = []


    while nextPage != None:

        tracks = requests.get(url, headers=headers, params=parameters)
        
        if tracks.status_code == 200:
            tracksDict = json.loads(tracks.text)
                
            for ob in tracksDict['items']:
                artists = []
                title = ob['track']['name']  
                for art in ob['track']['artists']:
                    artist = art['name']
                    artists.append(artist)
                
                songs.append({'title': title, 'artists':artists})
        
            parameters['offset'] = str(tracksDict['offset']+50)
            nextPage = tracksDict['next']

        else:
            print("Oops, something went wrong.  Error: " + str(tracks.status_code))
            nextPage = None     

            
    with open('trackFile.json', 'w') as outfile:
        json.dump(songs, outfile)

    return songs
    
def importToGPlay(input = None):
"""Searches Google Play Music using the song data previously generated."""   
    deviceID = ''
    if deviceID == '':
        dIDs = mc.get_registered_devices()
        dIDsdict = []
        for ids in dIDs:
            dIDsdict.append({'Device name' = ids['friendlyName']})
            diDsdict.append({'Device ID' = ids['id']})
        print('Please input your 16 digit Android device ID or “ios:<uuid>” for iOS from the list below or enter your own.")
        print(dIDsdict)
        deviceID = input('Enter device ID: ')

    # Authenticates devide using device id.  
    # Device ID os a string of 16 hex digits for Android or “ios:<uuid>” for iOS.
    if mc.oauth_login(deviceID) is False:
        mc.perform_oauth()
        
    else:
        print("You have logged in")

    #gets spotify library data from file
    with open("trackFile.json", "r") as songFile:
        songs = json.load(songFile)
    #gets track info and searches google servers then compares to initial query. if it doesn't match the track is added to a fails file
    query = ""
    songIDs = []
    fails = []
    counter = 0
    total = 0
    for track in songs:
        title = track['title'].lower()
        artists = [artie.lower() for artie in track['artists']]
        query = title + " " + " ".join(artists)
        queRES = mc.search(query, max_results=5)
        
        
    #checks to make sure there were matches then compares matches to search
        if len(queRES['song_hits']) > 0:
            reArtist = queRES['song_hits'][0]['track']['artist'].lower()
            reTittes = queRES['song_hits'][0]['track']['title'].lower()

            if reArtist in artists and (reTittes in title or title in reTittes):
                songIDs.append(queRES['song_hits'][0]['track']['storeId'])
            else:
                fails.append({'query': track, 'resp': queRES['song_hits']})
                    
        else:
            fails.append({'query': track, 'resp': queRES['song_hits']})

        if counter < 50:
            counter += 1
        else:
            total += 50
            counter = 0
            print(total)
            print(str(len(songIDs)) + ' ' + str(len(fails)) + '\n')
            with shelve.open('outcomeFile') as outcome:
                outcome['good'] = songIDs
                outcome['bad'] = fails
    
    mc.add_store_tracks(songIDs)       
    
    addLoose = input("Would you like to add possible matches to playlists for later review (Y/N)?")
    if addLoose == 'Y':
        #get the store IDs of fails
        failIds = []
        for query in fails:
            if query["resp"] != []:
                songID = query["resp"][0]["track"]["storeId"]
                failIds.append(songID)
        with shelve.open("failIds") as failed:
            failed["fails"] = failIds
        #create playlists to put the songs in
        playCount = 0
        playlistList = []
        for playCount in range(math.ceil(len(failIds)/500)):
            #create the right number of playlists
            playlist = "Maybes_"+str(playCount)
            playlistList.append(playlist)
            mc.create_playlist(playlist)
            playCount +=1

        #get the playlist IDs of the playlists just created. thanx google for being so easy to work with    
        allPlaylists = mc.get_all_playlists()
        offset = 0
        #add songs to the playlists created
        for plist in allPlaylists:
            if "Maybes" not in plist['name']:
                continue
            playlist = plist['id']
            low = offset*501
            high = low + 501
            sublist = failIds[low:high]
            mc.add_songs_to_playlist(playlist, sublist)
            offset +=1
    elif addLoose == 'N':
        continue
    else:
        print("Is it really that hard to enter Y or N?")

    

    # test = ['Tagrdsjvhn5njasvchcrlnhzx6y', 'Tl46ftluata3xgecexjpdxqpxva', 'T3xpfno3xrj5mxveuozeebzuaiq', 'Thjebjnyitc2oigfbv5ljelstvq', 'Tojowhwp3q5orw7bhmgqlzwzgma', 'T7o5j6lhzrz5y4yzq7uv3ch4psi', 'Tcgl5oure3pprjje5dyhie42fmm', 'Tsmdmnzkinvjqc4yymrlhxrxzny', 'Tnxszfyeajgoefaeml2ye44qk5m', 'Tg7daojc7ahuhbxfhusjzpmdlqu', 'Tje26qvz3wfnmoorpaucsblco4y', 'Tlav5j4tuxvi45q4hos4j5gvwii', 'Tyg6hoe3lstmlu4zdm7gl4hqyni', 'Tygfvtuwsbwfnajyad7lvpln3sq', 'Thpjsdqkhn67wbgt7wqkcxaa5be', 'Tdc3zg55sabyd2wp6t5vckoll3m', 'Tum7lsimn2jd37enim77wzenqsa', 'Tqdwwyibd2rgx4f7gsse2rqs24i', 'Tj6mhocdb5xlexa3xgpxd6wqgse', 'Thawjnnegidasxzfg5jhtvlfmka', 'Tuz77zzjclsu6qyo3t3nn6ctpnm', 'T26aktvztvursmbw5rcduf6pb3e', 'Tvwtkhzxkc3ibnyxmra7hmet3pe', 'Tjiovfdaqcktkweej2j2vtntnw4', 'Tslbornnieprppu2hptf5sxulty', 'Tnubdym3x44xukjfsjhd7f4crdy', 'Tvaqb7zzrh6qwpzgvbo6qtup4au', 'Tvifh2gqfezi7a7qgavkb2cwjwa', 'Txuxja2jos7n2k6l3527qri2y7q', 'Teuaui6zgbin2dhmuf2rfru42yi', 'Tddels6wnksctnuf5mmz2ro2wnm', 'T4uvj37ftqafv56d752mltl2iqm', 'Teamhpks2b2jbfe62tz62vz4dnm', 'Tm3ligtwkczzaxp75wehzinxsau', 'Tftqmvubieoscuvjspjrimykh6m', 'Tergzlxddllc2eehpkabzb5uzmq', 'T4cxvsbllhkn2s7rdeax2be7dmm']

    #print found and missed tracks to file
    # if input("Would you like to save  (Y/N):") == 'Y':
    #     today = str(datetime.now()).replace('-', '').replace(' ','').replace(':','').replace('.','')  # cause i'm too lazy for regex
    #     with open('missedTracks' + today + '.json','w') as responseFile:
    #         json.dump(fails, responseFile)
    #     with open('trackHits' + today + '.json','w') as reFile:
    #         json.dump(songIDs, reFile)


