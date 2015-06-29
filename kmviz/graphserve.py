#!/usr/bin/env python
import graphgen
from bottle import get, run

@get('/network')
def network():
    graphgen.get_json()

run(host='localhost', port=7070)
