#!/usr/bin/env python3

from flask import Flask, request
import flask
from typing import Dict, List
import deezerapi
from werkzeug.middleware.proxy_fix import ProxyFix

app = Flask(__name__)

app.wsgi_app = ProxyFix(
    app.wsgi_app, x_for=1, x_proto=1, x_host=1, x_prefix=1
)

users : List[Dict] = []
DEFAULT_GENRES : List[str] = ['Rock', 'Electro', 'Metal']

@app.route('/')
@app.route('/player')
def player():
    if request.cookies.get('userid') is None:
        resp = flask.make_response(flask.render_template('player.html', userid=str(len(users)), start_track = '70266756'))
        resp.set_cookie('userid', str(len(users)))
        users.append({'lasthr': 60, 'targethr': 60, 'curr_bpm': 124, 'recentplays': []})
        return resp
    return flask.render_template('player.html', userid=request.cookies.get('userid'))

@app.route('/tos')
def tos():
    return flask.render_template('tos.html')

@app.route('/clearcookie')
def clear_cookies():
    resp = flask.redirect('/')
    resp.delete_cookie('userid')
    return resp

@app.route('/channel')
def channel():
    return flask.render_template('channel.html')

@app.route('/hr/<userid>')
def get_hr(userid):
    userid = int(userid)
    #print(str(userid))
    hr = request.args.get('hr')
    if hr != None:
        users[userid]['lasthr'] = int(hr)
        return ''
    else:
        return str(users[userid]['lasthr'])

@app.route('/set_hr_target')
def set_hr():
    userid = request.cookies.get('userid')
    if userid is None:
        return ''
    user = users[int(userid)]
    hr = request.args.get('hr')
    if hr != None:
        user['targethr'] = int(hr)
    return ''
    

@app.route('/get_next')
def get_next_song():
    userid = request.cookies.get('userid')
    if userid is None:
        return ''
    user = users[int(userid)]
    while True:
        if user['lasthr'] > user['targethr']:
            track = deezerapi.get_tracks_by_bpm_genre((user['curr_bpm'] - 10, DEFAULT_GENRES), max = 3)[0]
        elif user['lasthr'] < user['targethr']:
            track = deezerapi.get_tracks_by_bpm_genre((user['curr_bpm'] + 10, DEFAULT_GENRES), max = 3)[0]
        else:
            track = deezerapi.get_tracks_by_bpm_genre((user['curr_bpm'], DEFAULT_GENRES), max = 3)[0]
        if track not in user['recentplays']:
            break
    ti = deezerapi.track_info(str(track))
    user['recentplays'].append(track)
    #print('Old BPM: ' + str(user['curr_bpm']) + ' New BPM: ' + str(ti['bpm']))
    user['curr_bpm'] = ti['bpm']
    return str(track)
