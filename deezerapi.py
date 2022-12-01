#!/usr/bin/env python3

# Code to access the Deezer API

from typing import List, Dict, Tuple
import requests, random

API_URL = 'https://api.deezer.com/'

def search_tracks(q : str, next = None) -> List[Dict]:
    '''Performs a search on the Deezer API for songs matching the passed query'''
    #print('Searching for: ' + q)
    nextstr = ''
    if next != None and next != 0:
        nextstr = '&index=' + str(next)
    req = requests.get(API_URL + 'search/?q=' + q + nextstr)
    return req.json()['data']

def get_track_bpm_genre(track_id : str) -> List[str]:
    '''Returns the genre name(s) for the passed track ID'''
    req = requests.get(API_URL + 'track/' + track_id)
    track_info = req.json()
    album_id = str(track_info['album']['id'])
    req = requests.get(API_URL + 'album/' + album_id)
    genres = req.json()['genres']['data']
    gs = []
    for g in genres:
        gs.append(g['name'])
    return (track_info['bpm'], gs)

def track_info(track_id : str) -> Dict:
    ti = {'id': int(track_id)}
    (bpm, genres) = get_track_bpm_genre(track_id)
    ti['bpm'] = round(bpm)
    ti['genres'] = genres
    req = requests.get(API_URL + '/track/' + track_id)
    ti['duration'] = req.json()['duration']
    return ti

def get_tracks_by_bpm_genre(q : Tuple[float, List[str]], bpm_bounds : int = 5, max : int = 5) -> List[int]:
    '''Returns a list of up to max tracks of correct genres that are within +- bpm_bounds of the target bpm'''
    bpm_target = round(q[0])
    max_bpm = bpm_target + bpm_bounds
    min_bpm = bpm_target - bpm_bounds
    gs = set(q[1])
    out_tracks = []
    tracks = search_tracks('bpm_min:"' + str(min_bpm) + '" bpm_max:"' + str(max_bpm) + '"', random.randint(0, 4) * 25)
    for t in tracks:
        genres = set(get_track_bpm_genre(str(t['id']))[1])
        if len(gs.intersection(genres)) > 0:
            out_tracks.append(t['id'])
            if len(out_tracks) == max:
                random.shuffle(out_tracks)
                return out_tracks
    random.shuffle(out_tracks)
    return out_tracks

