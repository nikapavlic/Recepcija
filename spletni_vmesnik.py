#!/usr/bin/python
# -*- encoding: utf-8 -*-

# uvozimo bottle.py
from bottleext import *

# uvozimo ustrezne podatke za povezavo
import data.auth as auth

# uvozimo psycopg2
import psycopg2, psycopg2.extensions, psycopg2.extras
psycopg2.extensions.register_type(psycopg2.extensions.UNICODE) # se znebimo problemov s šumniki

import os

# privzete nastavitve
SERVER_PORT = os.environ.get('BOTTLE_PORT', 8080)
RELOADER = os.environ.get('BOTTLE_RELOADER', True)
DB_PORT = os.environ.get('POSTGRES_PORT', 5432)

#za debugiranje
#debuger(True)

@get('/')
def index():
    return 'Začetna stran'

# @get('/')
# def index():
#     redirect(url('izbira_uporabnika'))

@get('/receptorji')
def receptorji():
    cur.execute("""
        SELECT emso, ime, priimek
        FROM receptor
    """)
    return template('receptorji.html', receptorji=cur)

# # Način prijave:
# @get('/izbira_uporabnika')
# def izbira_uporabnika():
#     return template('izbira_uporabnika.html', izbira_uporabnika=izbira_uporabnika, napaka=napaka)

conn = psycopg2.connect(database=auth.db, host=auth.host, user=auth.user, password=auth.password, port=DB_PORT)
cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor) 

run(host='localhost', port=SERVER_PORT, reloader=RELOADER)

