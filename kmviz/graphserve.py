#!/usr/bin/env python
import graphgen
from bottle import get, run

@get('/network/<size>/<wifisize>/<seed>')
def network(size, wifisize, seed):
    return graphgen.get_json(int(size), int(wifisize), int(seed))

@get('/network')
def network_fixed():
    return network(15, 5, 0)

@get('/room')
def room():
    return {
        'polygon': [{'x': p[0], 'y': p[1]}
                    for p in graphgen.create_room()],
    }

@get('/d3.min.js')
def d3():
    with open('d3.min.js') as f:
        return f.read()

@get('/jquery.min.js')
def d3():
    with open('jquery.min.js') as f:
        return f.read()

@get('/')
def index():
    with open('index.html') as f:
        return f.read()

run(host='localhost', port=7070, reloader=True)
