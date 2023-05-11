#!/usr/bin/python
# -*- encoding: utf-8 -*-

# uvozimo bottle.py
from bottleext import *
from data.model import *
from database import Repo

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

Repo=Repo()

#za debugiranje
#debuger(True)

@get('/')
def index():
    return template('zacetna_stran.html')
    #return 'Začetna stran'

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

# Način prijave:
# @get('/izbira_uporabnika')
# def izbira_uporabnika():
#     return template('izbira_uporabnika.html', izbira_uporabnika=izbira_uporabnika)

@get('/receptor/prijava') 
def prijava_receptor_get():
    return template("receptor_prijava.html")

# kot zaposleni se lahko prijavimo npr. z emšom 1 in geslom 1234
@post('/receptor/prijava') 
def prijava_receptor_post():
    uporabnisko_ime = request.forms.get('uporabnisko_ime')
    geslo = request.forms.get('geslo')
    if uporabnisko_ime is None or geslo is None:
        redirect(url('prijava_receptor_get'))
    hashBaza = None
    try: 
        cur.execute("SELECT geslo FROM receptor WHERE uporabnisko_ime = %s", [uporabnisko_ime])
        hashBaza = cur.fetchall()[0][0]
    except:
        hashBaza = None
    if hashBaza is None:
        redirect(url('prijava_receptor_get'))
        return
    if geslo != hashBaza:
      #  nastaviSporocilo('Nekaj je šlo narobe.') 
        redirect(url('prijava_receptor_get'))
        return
    #redirect(url('izbira_pregleda'))
    redirect(url('rezervacije_get'))
    return #'Uspešna prijava'

@get('/gost/prijava') 
def prijava_gost_get():
    return template("gost_prijava.html")


@post('/gost/prijava') 
def prijava_gost_post():
    uporabnisko_ime = request.forms.get('uporabnisko_ime')
    geslo = request.forms.get('geslo')
    if uporabnisko_ime is None or geslo is None:
        redirect(url('prijava_gost_get'))
    hashBaza = None
    try: 
        cur.execute("SELECT geslo FROM uporabnik WHERE uporabnisko_ime = %s", [uporabnisko_ime])
        hashBaza = cur.fetchall()[0][0]
    except:
        hashBaza = None
    if hashBaza is None:
        redirect(url('prijava_gost_get'))
        return
    if geslo != hashBaza:
         #nastaviSporocilo('Nekaj je šlo narobe.') 
         redirect(url('prijava_gost_get'))
         return
    #redirect(url('izbira_pregleda'))
    return 'Uspešna gost prijava'

# treba še popraviti

# @get('/gost/rezervacija/<id>')
# def gost_rezervacija_get(id):
#     cur.execute("SELECT id FROM uporabnik WHERE id = %s", (id, ))
#     # id_gosta = cur.fetchone()
#     return template("nova_rezervacija.html")

# @post('/gost/rezervacija/<id>')
# def gost_rezervacija_post(id):
#     zacetek_nocitve = request.forms.zacetek_nocitve
#     stevilo_dni = request.forms.stevilo_dni
#     stevilo_odraslih = request.forms.stevilo_odraslih
#     stevilo_otrok = request.forms.stevilo_otrok
#     seznam_prostih_parcel = Repo.dobi_proste_parcele(zacetek_nocitve, stevilo_dni, stevilo_odraslih, stevilo_otrok)

#     rezervacija = rezervacije(pricetek_bivanja=zacetek_nocitve, st_nocitev=stevilo_dni, odrasli=stevilo_odraslih, otroci=stevilo_otrok, rezervirana_parcela=seznam_prostih_parcel[0], gost=id)

#     Repo.dodaj_rezervacije(rezervacija)
#     return 'Uspešno dodana rezervacija'
    #v gost=manjka id gosta, ki dela rezervacijo, to bi lahko dodale v samo metodo zgoraj, ker je rezervacija itak vezana na uporabnika


@get('/registracija')
def registracija_get():
    cur.execute("""
        SELECT kratica, ime
        FROM drzava
    """)
    return template('registracija.html', drzava = cur)

@post('/registracija')
def registracija_post():
    uporabnisko_ime = request.forms.uporabnisko_ime
    geslo = request.forms.geslo
    ime = request.forms.ime
    priimek = request.forms.priimek
    rojstvo = request.forms.rojstvo
    nacionalnost = request.forms.nacionalnost

    uporabnik1=uporabnik(uporabnisko_ime=uporabnisko_ime, geslo=geslo, ime=ime, priimek=priimek, rojstvo=rojstvo, nacionalnost=nacionalnost)
    Repo.dodaj_uporabnik(uporabnik1)
    return 'Uspešna registracija'


@get('/rezervacije')
def rezervacije_get():
    cur.execute("""
        SELECT rezervacije.id,  pricetek_bivanja, st_nocitev,odrasli,otroci, rezervirana_parcela, gost, ime, priimek FROM rezervacije
        LEFT JOIN uporabnik ON uporabnik.id = rezervacije.gost
    """)
    return template('rezervacije.html', rezervacija = cur)



conn = psycopg2.connect(database=auth.db, host=auth.host, user=auth.user, password=auth.password, port=DB_PORT)
cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor) 

run(host='localhost', port=SERVER_PORT, reloader=RELOADER)

