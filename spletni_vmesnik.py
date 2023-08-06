#!/usr/bin/python
# -*- encoding: utf-8 -*-

# uvozimo bottle.py
from bottleext import *
# from bottleext import get, post, run, request, template, redirect, static_file, url, response, template_user

from data.model import *
from database import Repo
from functools import wraps
from datetime import datetime as dt
from datetime import date

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

repo=Repo()

#za debugiranje
#debuger(True)



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

def cookie_required(f):
    """
    Dekorator, ki zahteva veljaven piškotek. Če piškotka ni, uporabnika preusmeri na stran za prijavo.
    """
    @wraps(f)
    def decorated( *args, **kwargs):
        
           
        cookie = request.get_cookie("uporabnisko_ime")
        if cookie:
            return f(*args, **kwargs)
        
        return template("receptor_prijava.html", napaka="dekorator!")

           
    return decorated


@get('/')
def index():
    return template('zacetna_stran.html')
    #return 'Začetna stran'


@get('/static/<filename:path>')
def static(filename):
    return static_file(filename, root='static')



# @get('/')
# @cookie_required
# def index():
#     """
#     Domača stran je stran z cenami izdelkov.
#     """

#     izdelki = repo.cena_izdelkov()
        
#     return template_user('izdelki.html', skip=0, take=10, izdelki=izdelki)
 
    
# @get('/izdelki/<skip:int>/<take:int>/')
# @cookie_required
# def izdelki(skip, take):    
    
#     izdelki = repo.cena_izdelkov(skip=skip, take=take )
#     return template_user('izdelki.html',skip=skip, take=take, izdelki=izdelki)

# @get('/kategorije/<skip:int>/<take:int>/')
# @cookie_required
# def kategorije(skip, take):    
    
#     kategorije = repo.kategorije_izdelkov(skip=skip, take=take )
#     return template_user('kategorije.html' ,skip=skip, take=take, kategorije=kategorije)
    
    
    

# @post('/receptor/prijava')
# def receptor_prijava_post():
#     """
#     Prijavi uporabnika v aplikacijo. Če je prijava uspešna, ustvari piškotke o uporabniku in njegovi roli.
#     Drugače sporoči, da je prijava neuspešna.
#     """
#     username = request.forms.get('uporabnik')
#     password = request.forms.get('geslo')

#     if not auth.obstaja_uporabnik(username):
#         return template("receptor_prijava.html", napaka="Uporabnik s tem imenom ne obstaja")

#     prijava = auth.prijavi_uporabnika(username, password)
#     if prijava:
#         response.set_cookie("uporabnik", username)
#         response.set_cookie("rola", prijava.role)
        
#         redirect(url('index'))
        
#     else:
#         return template("receptor_prijava.html", napaka="Neuspešna prijava. Napačno geslo ali uporabniško ime.")
    
@get('/odjava')
def odjava():
    """
    Odjavi uporabnika iz aplikacije. Pobriše piškotke o uporabniku in njegovi roli.
    """
    
    response.delete_cookie("uporabnisko_ime")
    response.delete_cookie("rola")
    response.delete_cookie("id")
    
    return template('zacetna_stran.html', napaka=None)




@get('/receptor/prijava') 
def prijava_receptor_get():
    return template("receptor_prijava.html")

# kot zaposleni se lahko prijavimo npr. z emšom 1 in geslom 1234
@post('/receptor/prijava')                              #   POMOJE DA VSE KAR JE V TEJ FUNKCIJI ZAKOMENTIRAN SE LAHKO IZBRIŠE
def prijava_receptor_post():
    uporabnisko_ime = request.forms.get('uporabnisko_ime')
    geslo = request.forms.get('geslo')
    if uporabnisko_ime is None or geslo is None:
        redirect(url('prijava_receptor_get'))
    hashBaza = None
    try: 
        cur.execute("SELECT geslo FROM receptor WHERE uporabnisko_ime = %s", [uporabnisko_ime])
        hashBaza = cur.fetchall()[0][0]
        cur.execute("SELECT emso FROM receptor WHERE uporabnisko_ime = %s", [uporabnisko_ime])
        id_receptorja = cur.fetchall()[0][0]
    except:
        hashBaza = None
    if hashBaza is None:
        redirect(url('prijava_receptor_get'))
        return
    if geslo != hashBaza:
      #  nastaviSporocilo('Nekaj je šlo narobe.') 
        redirect(url('prijava_receptor_get'))
        return
    #### NE DELAJO COOKIJI????
    response.set_cookie("uporabnisko_ime", uporabnisko_ime,  path = "/") #secret = "secret_value",, httponly = True)
    response.set_cookie("rola", "receptor",  path = "/")
    response.set_cookie("id", str(id_receptorja),  path = "/")
    

    #redirect(url('izbira_pregleda'))
    redirect(url('rezervacije_get'))#, id_receptorja = id_receptorja, receptor = True)
    #ck = request.get_cookie("uporabnik")
    #rl = request.get_cookie("rola")
    #return #str(ck)

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
        cur.execute("SELECT id FROM uporabnik WHERE uporabnisko_ime = %s", [uporabnisko_ime])
        id_gosta = cur.fetchall()[0][0]
    except:
        hashBaza = None
    if hashBaza is None:
        redirect(url('prijava_gost_get'))
        return
    if geslo != hashBaza:
         #nastaviSporocilo('Nekaj je šlo narobe.') 
         redirect(url('prijava_gost_get'))
         return
    response.set_cookie("uporabnisko_ime", uporabnisko_ime,  path = "/") #secret = "secret_value",, httponly = True)
    response.set_cookie("rola", "gost",  path = "/")
    response.set_cookie("id", str(id_gosta),  path = "/")
    
#    redirect(url('pregled_rezervacij_gosta'))
    redirect(url('pregled_rezervacij_gosta'))#, id_gosta=id_gosta))

# @get('/gost/pregled')
# def pregled_rezervacij_gosta():
#     return template('gost_pregled.html')

@get('/gost/pregled/')#<uporab>')                   #   POMOJE DA VSE KAR JE V TEJ FUNKCIJI ZAKOMENTIRAN SE LAHKO IZBRIŠE
@cookie_required
def pregled_rezervacij_gosta(): 
    #uporab = str(request.cookies.get('uporabnik'))     
    #uporab = 'petja'
    id_gosta = int(request.cookies.get("id"))
    #cur.execute("SELECT id FROM uporabnik WHERE uporabnisko_ime = %s", [uporab])
    #id_gosta = int(cur.fetchall()[0][0])
    cur.execute("""
         SELECT pricetek_bivanja, st_nocitev, odrasli, otroci, uporabnisko_ime FROM rezervacije
         INNER JOIN uporabnik ON rezervacije.gost = uporabnik.id
         WHERE uporabnik.id = %s
     """,
      [id_gosta])
    return template_user('gost_pregled.html', rezervacija = cur)#,id_gosta=id_gosta)
    #return str(id_gosta)

# REZERVACIJA
# treba še popraviti

@get('/gost/rezervacija/')
def gost_rezervacija_get():
    #cur.execute("""SELECT id FROM uporabnik WHERE id = %s""", (id, ))
    # id_gosta = cur.fetchone()
    return template("nova_rezervacija.html")

@post('/gost/rezervacija/')                     #   POMOJE DA VSE KAR JE V TEJ FUNKCIJI ZAKOMENTIRAN SE LAHKO IZBRIŠE
def gost_rezervacija_post():
    zacetek_nocitve = request.forms.zacetek_nocitve
    stevilo_dni = int(request.forms.stevilo_dni)
    stevilo_odraslih = int(request.forms.stevilo_odraslih)
    stevilo_otrok = int(request.forms.stevilo_otrok)

    id_gosta = int(request.cookies.get("id"))
    #zacetek_nocitve = str(zacetek_nocitve)
    #zacetek_nocitve = '2023-09-01'
    #zacetek_nocitve = zacetek_nocitve.strftime("%Y-%m-%d")
    seznam_prostih_parcel = repo.dobi_proste_parcele(datum_nove = zacetek_nocitve, st_dni_nove=stevilo_dni, st_odraslih=stevilo_odraslih, st_otrok=stevilo_otrok)

    rezervacija = rezervacije(pricetek_bivanja=zacetek_nocitve, st_nocitev=stevilo_dni, odrasli=stevilo_odraslih, otroci=stevilo_otrok, rezervirana_parcela=seznam_prostih_parcel, gost=id_gosta)

    repo.dodaj_rezervacije(rezervacija)
   # return zacetek_nocitve
    return "Uspešno dodano"

   # v gost=manjka id gosta, ki dela rezervacijo, to bi lahko dodale v samo metodo zgoraj, ker je rezervacija itak vezana na uporabnika, zaenkrat meče samo Petja kar na vse rezervacije ne glede na id


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
    repo.dodaj_uporabnik(uporabnik1)
    redirect(url('prijava_gost_get'))


@get('/rezervacije')
@cookie_required #Če to odkomentiraš kr naenkrat pri prijavi ne dela, ker se cookiji očitno ne prenesejo naprej in potem ta funkcija ne dela
def rezervacije_get():#,id_receptorja receptor):
    #receptor = request.get_cookie("uporabnisko_ime")
    #if receptor == None:
    #    template_user('receptor_prijava.html')
    #else:
    cur.execute("""
        SELECT rezervacije.id,  pricetek_bivanja, st_nocitev,odrasli,otroci, rezervirana_parcela, gost, ime, priimek FROM rezervacije
        LEFT JOIN uporabnik ON uporabnik.id = rezervacije.gost
    """)
    return template_user('rezervacije.html', rezervacija = cur)

@post('/zbrisi-rezervacijo')
def zbrisi_rezervacijo():
    id_rezervacije = request.forms.id_rezervacije
    repo.zbrisi_rezervacijo(id_rezervacije)
    redirect(url('rezervacije_get'))

#tole moras preuredit +  manjkajo cookiji za rezervacijo id, ker mora biti tista, ki jo kliknem
@get('/rezervacija/predracun/')
def ustvari_predracun_get():
    #kaj rabim na predracunu:
    # st_rezervacije
    # st_dni
    # ime gosta
    # st. otrok in st. odraslih
    # st_parcele
    id_zacasni = 23
    cur.execute("SELECT * FROM rezervacije WHERE id = %s", [id_zacasni])
    return template('racun.html', rezervacija=cur)


conn = psycopg2.connect(database=auth.db, host=auth.host, user=auth.user, password=auth.password, port=DB_PORT)
cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor) 

run(host='localhost', port=SERVER_PORT, reloader=RELOADER)

