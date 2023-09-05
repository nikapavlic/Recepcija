#!/usr/bin/python
# -*- encoding: utf-8 -*-

# uvozimo bottle.py
import os
from bottleext import *

from data.model import *
from database import Repo
from functools import wraps
from datetime import datetime as dt
from datetime import date

# uvozimo ustrezne podatke za povezavo
import data.auth as auth

# uvozimo psycopg2
import psycopg2
import psycopg2.extensions
import psycopg2.extras
# se znebimo problemov s šumniki
psycopg2.extensions.register_type(psycopg2.extensions.UNICODE)


# privzete nastavitve
SERVER_PORT = os.environ.get('BOTTLE_PORT', 8080)
RELOADER = os.environ.get('BOTTLE_RELOADER', True)
DB_PORT = os.environ.get('POSTGRES_PORT', 5432)

repo = Repo()

# za debugiranje
# debuger(True)


def password_hash(s):
    """Vrni SHA-512 hash danega UTF-8 niza. Gesla vedno spravimo v bazo
       kodirana s to funkcijo."""
    h = hashlib.sha512()
    h.update(s.encode('utf-8'))
    return h.hexdigest()

@get('/receptorji')
def receptorji():
    cur.execute("""
        SELECT emso, ime, priimek
        FROM receptor
    """)
    return template_user('receptorji.html', receptorji=cur)


def cookie_required(f):
    """
    Dekorator, ki zahteva veljaven piškotek. Če piškotka ni, uporabnika preusmeri na stran za prijavo.
    """
    @wraps(f)
    def decorated(*args, **kwargs):

        cookie = request.get_cookie("uporabnisko_ime")
        if cookie:
            return f(*args, **kwargs)

        return template('zacetna_stran.html', napaka="Potrebna je prijava")

    return decorated


def cookie_required_receptor(f):
    """
    Dekorator, ki zahteva veljaven piškotek receptorja. Če piškotka ni, uporabnika preusmeri na stran za prijavo.
    """
    @wraps(f)
    def decorated(*args, **kwargs):

        cookie = request.get_cookie("rola")
        if cookie == "receptor":
            return f(*args, **kwargs)

        return template("receptor_prijava.html", napaka="Za dostop se je potrebno prijaviti kot receptor")

    return decorated


@get('/')
def index():
    return template('zacetna_stran.html')


@post('/izracun')
def izracun():
    st_nocitev = int(request.forms.st_nocitev)
    odrasli = int(request.forms.odrasli)
    otroci = int(request.forms.otroci)
    cena = (odrasli*12+otroci*7)*st_nocitev
    return template('zacetna_stran.html', cena=cena)


@get('/static/<filename:path>')
def static(filename):
    return static_file(filename, root='static')


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

# PRIJAVA ZA RECEPTORJA
@post('/receptor/prijava')
def prijava_receptor_post():
    uporabnisko_ime = request.forms.get('uporabnisko_ime')
    geslo = password_hash(request.forms.get('geslo'))
    #geslo = request.forms.get('geslo')
    if uporabnisko_ime is None or geslo is None:
        sporocilo = "Vnesi uporabniško ime in geslo"
        return template("receptor_prijava.html", napaka=sporocilo)
    hashBaza = None
    try:
        hashBaza = cur.execute(
            "SELECT geslo FROM receptor WHERE uporabnisko_ime = %s", [uporabnisko_ime])
        hashBaza = cur.fetchone()[0]
        id_receptorja = cur.execute(
            "SELECT emso FROM receptor WHERE uporabnisko_ime = %s", [uporabnisko_ime])
        id_receptorja = cur.fetchall()[0]
    except TypeError:
        hashBaza = None
    if hashBaza is None:
        sporocilo = "Napačno uporabniško ime"
        return template("receptor_prijava.html", napaka=sporocilo)
    if geslo != hashBaza:
        sporocilo = "Napačno geslo"
        return template("receptor_prijava.html", napaka=sporocilo)
    response.set_cookie("uporabnisko_ime", uporabnisko_ime,  path="/")
    response.set_cookie("rola", "receptor",  path="/")
    response.set_cookie("id", str(id_receptorja),  path="/")

    redirect(url('aktivne_rezervacije_get'))

# PRIJAVA ZA GOSTE
@get('/gost/prijava')
def prijava_gost_get():
    return template("gost_prijava.html")


@post('/gost/prijava')
def prijava_gost_post():
    uporabnisko_ime = request.forms.get('uporabnisko_ime')
    geslo = password_hash(request.forms.get('geslo'))
    if uporabnisko_ime is None or geslo is None:
        sporocilo = "Vnesi uporabniško ime in geslo"
        return template("gost_prijava.html", napaka=sporocilo)
    hashBaza = None
    try:
        cur.execute("SELECT geslo FROM uporabnik WHERE uporabnisko_ime = %s", [
                    uporabnisko_ime])
        hashBaza = cur.fetchall()[0][0]
        cur.execute("SELECT id FROM uporabnik WHERE uporabnisko_ime = %s", [
                    uporabnisko_ime])
        id_gosta = cur.fetchall()[0][0]
    except TypeError:
        hashBaza = None
    if hashBaza is None:
        sporocilo = "Napačno uporabniško ime"
        return template("gost_prijava.html", napaka=sporocilo)
    if geslo != hashBaza:
        sporocilo = "Napačno geslo"
        return template("gost_prijava.html", napaka=sporocilo)
    response.set_cookie("uporabnisko_ime", uporabnisko_ime,  path="/")
    response.set_cookie("rola", "gost",  path="/")
    response.set_cookie("id", str(id_gosta),  path="/")

    redirect(url('pregled_rezervacij_gosta')) 

             
@get('/gost/pregled/')
@cookie_required
def pregled_rezervacij_gosta():
    id_gosta = int(request.cookies.get("id"))
    
    cur.execute("""
         SELECT pricetek_bivanja, st_nocitev, odrasli, otroci, uporabnisko_ime, rezervacije.id FROM rezervacije
         INNER JOIN uporabnik ON rezervacije.gost = uporabnik.id
         WHERE uporabnik.id = %s
         ORDER BY pricetek_bivanja
     """,
                [id_gosta])
    return template_user('gost_pregled.html', rezervacija=cur)


@get('/gost/racuni/')
@cookie_required
def gost_racuni():
    uporabnik = str(request.cookies.get("uporabnisko_ime"))
    cur.execute("""
        SELECT racun.id AS id_racuna, racun.id_rezervacije AS id_rezervacije, uporabnik.ime AS ime_uporabnika , uporabnik.priimek AS priimek_uporabnika, rezervacije.odrasli AS odrasli, rezervacije.otroci AS otroci, rezervacije.st_nocitev AS st_nocitev FROM racun 
                INNER JOIN rezervacije ON id_rezervacije = rezervacije.id
                INNER JOIN receptor ON racun.izdajatelj = receptor.emso
                INNER JOIN uporabnik ON uporabnik.id = rezervacije.gost
                WHERE uporabnik.uporabnisko_ime =%s
                ORDER BY racun.id """, [uporabnik])
    return template_user('gost_racuni.html', racuni=cur)


# REZERVACIJA
@get('/gost/rezervacija/')
@cookie_required
def gost_rezervacija_get():
    return template("nova_rezervacija.html")


@post('/gost/rezervacija/')
@cookie_required  
def gost_rezervacija_post():
    zacetek_nocitve = request.forms.zacetek_nocitve
    stevilo_dni = str(request.forms.stevilo_dni)
    stevilo_odraslih = str(request.forms.stevilo_odraslih)
    stevilo_otrok = str(request.forms.stevilo_otrok)

    id_gosta = int(request.cookies.get("id"))

    # ni možna rezervacija za nazaj:
    datum= datetime.strptime(zacetek_nocitve, "%Y-%m-%d")
    danes = datetime.now()
    if datum.date() < danes.date():
        return template_user("nova_rezervacija.html",  napaka="Ni mogoče potovati v preteklost <3")
    

    if stevilo_dni.isdigit() and stevilo_odraslih.isdigit() and stevilo_otrok.isdigit():
        stevilo_dni = int(request.forms.stevilo_dni)
        stevilo_odraslih = int(request.forms.stevilo_odraslih)
        stevilo_otrok = int(request.forms.stevilo_otrok)
    else:
        return template_user("nova_rezervacija.html",  napaka="Prosimo, da še enkrat vnesete podatki. Pazite, da so vnešeni pravilno.")
    

    if stevilo_odraslih + stevilo_otrok > 12:
        return template_user("nova_rezervacija.html",  napaka="Rezervacijo lahko naredite za največ 12 oseb na eni parceli. Če želite rezervirati za več oseb, se prosimo obrnite na recepciijo kampa.")


    seznam_prostih_parcel = repo.dobi_proste_parcele(
        datum_nove=zacetek_nocitve, st_dni_nove=stevilo_dni, st_odraslih=stevilo_odraslih, st_otrok=stevilo_otrok)
    
    if seznam_prostih_parcel is None:
        return template_user("nova_rezervacija.html",  napaka="Za izbrane parametre ni prostih parcel")


    prosta_parcela = seznam_prostih_parcel[0]

    rezervacija = rezervacije(pricetek_bivanja=zacetek_nocitve, st_nocitev=stevilo_dni,
                              odrasli=stevilo_odraslih, otroci=stevilo_otrok, rezervirana_parcela=prosta_parcela, gost=id_gosta)

    repo.dodaj_rezervacije(rezervacija)
    redirect(url('pregled_rezervacij_gosta'))


# DODAJANJE NOVIH RECEPTORJEV
@get('/dodaj_receptorja')
@cookie_required
@cookie_required_receptor
def dodaj_receptorja_get():
    return template_user('nov_receptor.html')


@post('/dodaj_receptorja')
@cookie_required
@cookie_required_receptor
def dodaj_receptorja_post():
    emso = request.forms.emso
    uporabnisko_ime = request.forms.uporabnisko_ime
    geslo = password_hash(request.forms.geslo)
    ime = request.forms.ime
    priimek = request.forms.priimek

    cur.execute("""
        SELECT emso 
        FROM receptor
    """)
    sz = cur.fetchall()
    seznam_emso = [value[0] for value in sz]

    if str(emso) in seznam_emso:
        sporocilo = "Uporabnik s to številko EMŠO že obstaja"
        return template_user('nov_receptor.html', napaka=sporocilo)

    else:
        receptor1 = receptor(emso=emso, uporabnisko_ime=uporabnisko_ime,
                         geslo=geslo, ime=ime, priimek=priimek)
        repo.dodaj_receptor(receptor1)
        redirect(url('receptorji'))


# REGISTRACIJA ZA NOVE UPORABNIKE
@get('/registracija')
def registracija_get():
    cur.execute("""
        SELECT kratica, ime
        FROM drzava
    """)
    return template('registracija.html', drzava=cur)


@post('/registracija')
def registracija_post():
    uporabnisko_ime = request.forms.uporabnisko_ime
    geslo = password_hash(request.forms.geslo)
    ime = request.forms.ime
    priimek = request.forms.priimek
    rojstvo = request.forms.rojstvo
    nacionalnost = request.forms.nacionalnost
    cur.execute("SELECT uporabnisko_ime FROM uporabnik")
    sz = cur.fetchall()
    seznam_uporabniskih_imen = [value[0] for value in sz]
    if uporabnisko_ime in seznam_uporabniskih_imen:
        sporocilo = "Izberi drugo uporabniško ime"
        cur1.execute("""
            SELECT kratica, ime
            FROM drzava
        """)
        return template("registracija.html", napaka=sporocilo, drzava=cur1)
    else:
        uporabnik1 = uporabnik(uporabnisko_ime=uporabnisko_ime, geslo=geslo,
                           ime=ime, priimek=priimek, rojstvo=rojstvo, nacionalnost=nacionalnost)
        repo.dodaj_uporabnik(uporabnik1)
        if request.cookies.get('rola') == 'receptor':
            redirect(url('pregled_uporabnikov_get'))
        else:
            redirect(url('prijava_gost_get'))


@get('/rezervacije')
@cookie_required
@cookie_required_receptor
def rezervacije_get():
    cur.execute("""
        SELECT rezervacije.id,  pricetek_bivanja, st_nocitev,odrasli,otroci, rezervirana_parcela, gost, ime, priimek,pricetek_bivanja+st_nocitev AS odhod, pricetek_bivanja+st_nocitev  < DATE('now') AS pretecena,pricetek_bivanja+st_nocitev = DATE('now') AS gre  FROM rezervacije
        LEFT JOIN uporabnik ON uporabnik.id = rezervacije.gost
        ORDER BY pricetek_bivanja;
    """)
    cur1.execute("""SELECT id_rezervacije FROM racun""")
    sz = cur1.fetchall()
    seznam = [value[0] for value in sz]

    return template_user('rezervacije.html', rezervacija=cur, poravnani=seznam)


@post('/zbrisi-rezervacijo')
@cookie_required
def zbrisi_rezervacijo():
    id_rezervacije = request.forms.id_rezervacije
    repo.zbrisi_rezervacijo(id_rezervacije)
    rola = str(request.cookies.get("rola"))
    if rola == 'receptor':
        redirect(url('rezervacije_get'))
    else:
        redirect(url('pregled_rezervacij_gosta'))


@get('/aktivne-rezervacije')
@cookie_required
@cookie_required_receptor
def aktivne_rezervacije_get():
    cur.execute("""
        SELECT rezervacije.id,  pricetek_bivanja, st_nocitev,odrasli,otroci, rezervirana_parcela, gost, ime, priimek, pricetek_bivanja+st_nocitev AS odhod, pricetek_bivanja+st_nocitev  <= DATE('now') AS pretecena FROM rezervacije
        LEFT JOIN uporabnik ON uporabnik.id = rezervacije.gost
        WHERE pricetek_bivanja <= DATE('now') AND DATE('now') <= pricetek_bivanja + st_nocitev
        ORDER BY pricetek_bivanja
    """)
    cur1.execute("""SELECT id_rezervacije FROM racun""")
    sz = cur1.fetchall()
    seznam = [value[0] for value in sz]
    # return template_user('rezervacije.html', rezervacija = cur, emso=emso)
    return template_user('aktivne_rezervacije.html', rezervacija=cur, poravnani=seznam)


@post('/rezervacija/predracun/')
@cookie_required
@cookie_required_receptor
def ustvari_predracun_post():
    id_rez = request.forms.id_rez
    redirect(url('ustvari_predracun_get', id=id_rez))


@get('/rezervacija/predracun/<id>')
@cookie_required
@cookie_required_receptor
def ustvari_predracun_get(id):
    receptor = request.cookies.get("uporabnisko_ime")
    cur.execute(
        "SELECT ime, priimek FROM receptor WHERE uporabnisko_ime = %s", (receptor,))
    podatki = cur.fetchone()
    ime = podatki[0]
    priimek = podatki[1]
    id_rez = id
    cur.execute("""SELECT rezervacije.id AS id_rezervacije, pricetek_bivanja, st_nocitev, odrasli, otroci, ime AS ime_gosta, priimek AS priimek_gosta FROM rezervacije 
                INNER JOIN uporabnik ON uporabnik.id = rezervacije.gost
                WHERE rezervacije.id = %s""", (id_rez,))

    return template('predracun.html', rezervacija=cur, receptor=receptor, ime=ime, priimek=priimek)


@get('/rezervacija/racun/<id>')
@cookie_required
@cookie_required_receptor
def ustvari_racun_get(id):
    receptor = request.cookies.get("uporabnisko_ime")
    cur.execute(
        "SELECT ime, priimek FROM receptor WHERE uporabnisko_ime = %s", (receptor,))
    podatki = cur.fetchone()
    ime = podatki[0]
    priimek = podatki[1]
    id_rez = id
    cur.execute("""SELECT rezervacije.id AS id_rezervacije, pricetek_bivanja, st_nocitev, odrasli, otroci, ime AS ime_gosta, priimek AS priimek_gosta FROM rezervacije 
                INNER JOIN uporabnik ON uporabnik.id = rezervacije.gost
                WHERE rezervacije.id = %s""", (id_rez,))
    return template('racun.html', rezervacija=cur, receptor=receptor, ime=ime, priimek=priimek)


@post('/rezervacija/racun/')
@cookie_required
@cookie_required_receptor
def ustvari_racun_post():
    id_rez = request.forms.id_rez
    redirect(url('ustvari_racun_get', id=id_rez))


@get('/rezervacija/izdaj_racun/<id>')
@cookie_required
@cookie_required_receptor
def izdaj_racun_get(id):
    #receptor = request.cookies.get("uporabnisko_ime")
    id_rez = id
    cur.execute(
        "SELECT id, pricetek_bivanja, st_nocitev, odrasli, otroci FROM rezervacije WHERE id = %s", (id_rez,))
    redirect(url('pregled_racunov_get'))


@post('/rezervacija/izdaj_racun/')
@cookie_required
@cookie_required_receptor
def izdaj_racun_post():
    id_rez = request.forms.id_rez
    emso = request.cookies.get("id")
    emso = str(emso[2:-2])
    repo.ustvari_racun(id_rez, emso)
    redirect(url('izdaj_racun_get', id=id_rez))

# PREGLED RAČUNOV-RECEPTOR
@get('/racuni')
@cookie_required
#@cookie_required_receptor
def pregled_racunov_get():
    cur.execute("""
        SELECT racun.id AS id_racuna, racun.id_rezervacije AS id_rezervacije, receptor.ime AS ime_receptorja, receptor.priimek AS priimek_receptorja, uporabnik.ime AS ime_uporabnika , uporabnik.priimek AS priimek_uporabnika, rezervacije.odrasli AS odrasli, rezervacije.otroci AS otroci, rezervacije.st_nocitev AS st_nocitev FROM racun 
                INNER JOIN rezervacije ON id_rezervacije = rezervacije.id
                INNER JOIN receptor ON racun.izdajatelj = receptor.emso
                INNER JOIN uporabnik ON uporabnik.id = rezervacije.gost
                ORDER BY id_racuna
    """)
    if request.cookies.get('rola') == 'receptor':
        return template_user('racuni.html', racuni=cur)
    else:
        redirect(url('gost_racuni'))
    

@get('/rezervacija/pregled_racuna/<id>')
@cookie_required
#@cookie_required_receptor
def preglej_racun_get(id):
    id_racuna = id
    cur.execute("""SELECT rezervacije.id AS id_rezervacije, pricetek_bivanja, st_nocitev, odrasli, otroci, uporabnik.ime AS ime_gosta, uporabnik.priimek AS priimek_gosta, receptor.ime AS ime_receptorja, receptor.priimek AS priimek_receptorja FROM racun 
                INNER JOIN rezervacije ON racun.id_rezervacije = rezervacije.id
                INNER JOIN uporabnik ON uporabnik.id = rezervacije.gost
                INNER JOIN receptor ON racun.izdajatelj = receptor.emso
                WHERE racun.id = %s""", (id_racuna,))
    return template('pregled_racuna.html', rezervacija=cur)


@post('/rezervacija/pregled_racuna/')
@cookie_required
#@cookie_required_receptor
def preglej_racun_post():
    id_racuna = request.forms.id_racuna
    redirect(url('preglej_racun_get', id=id_racuna))


# PREGLED UPORABNIKOV

@get('/uporabniki')
@cookie_required
@cookie_required_receptor
def pregled_uporabnikov_get():
    cur.execute("""
        SELECT id, uporabnisko_ime, ime, priimek, rojstvo, nacionalnost FROM uporabnik
                """)
    return template_user('uporabniki.html', uporabniki=cur)

@post('/receptor_rezervira')
@cookie_required
@cookie_required_receptor
def pregled_uporabnikov_post():
    id_gosta = int(request.forms.id)
    redirect(url('receptor_rezervira_get', id =id_gosta))

@get('/receptor_rezervira/<id>')
@cookie_required
def receptor_rezervira_get(id):
    id_gosta = id
    return template_user("receptor_rezervira.html",id=id_gosta)


@post('/rezerviraj')
@cookie_required  
def rezerviraj_post():
    zacetek_nocitve = request.forms.zacetek_nocitve
    stevilo_dni = str(request.forms.stevilo_dni)
    stevilo_odraslih = str(request.forms.stevilo_odraslih)
    stevilo_otrok = str(request.forms.stevilo_otrok)
 
    id_gosta = request.forms.id_gosta

    # ni možna rezervacija za nazaj:
    datum= datetime.strptime(zacetek_nocitve, "%Y-%m-%d")
    danes = datetime.now()
    if datum.date() < danes.date():
         return template_user("nova_rezervacija.html",  napaka="Ni mogoče potovati v preteklost <3")
    

    if stevilo_dni.isdigit() and stevilo_odraslih.isdigit() and stevilo_otrok.isdigit():
        stevilo_dni = int(request.forms.stevilo_dni)
        stevilo_odraslih = int(request.forms.stevilo_odraslih)
        stevilo_otrok = int(request.forms.stevilo_otrok)
    else:
        return template_user("nova_rezervacija.html",  napaka="Prosimo, da še enkrat vnesete podatki. Pazite, da so vnešeni pravilno.")
    

    if stevilo_odraslih + stevilo_otrok > 8:
        return template_user("nova_rezervacija.html",  napaka="Preveč oseb!")


    seznam_prostih_parcel = repo.dobi_proste_parcele(
        datum_nove=zacetek_nocitve, st_dni_nove=stevilo_dni, st_odraslih=stevilo_odraslih, st_otrok=stevilo_otrok)
    
    if seznam_prostih_parcel is None:
        return template_user("nova_rezervacija.html",  napaka="Za izbrane parametre ni prostih parcel")


    prosta_parcela = seznam_prostih_parcel[0]
    rezervacija = rezervacije(pricetek_bivanja=zacetek_nocitve, st_nocitev=stevilo_dni,
                              odrasli=stevilo_odraslih, otroci=stevilo_otrok, rezervirana_parcela=prosta_parcela, gost=id_gosta)

    repo.dodaj_rezervacije(rezervacija)
    redirect(url('pregled_uporabnikov_get'))


# PREGLED PARCEL
@get('/parcele')
@cookie_required
@cookie_required_receptor
def pregled_parcel():
    dan = request.forms.get('dan', date.today())
    cur.execute("""
                SELECT parcela.id, uporabnik.ime, uporabnik.priimek, rezervacije.id FROM parcela
                LEFT JOIN rezervacije ON parcela.id = rezervacije.rezervirana_parcela
                LEFT JOIN uporabnik ON gost = uporabnik.id
                WHERE pricetek_bivanja <= %s AND %s <= pricetek_bivanja + st_nocitev;
                """,[dan,dan,])
    zasedene = cur
    cur1.execute("""SELECT id, st_gostov FROM parcela
                ORDER BY id""")
    sz = cur.fetchall()
    seznam = [value[0] for value in sz]
    return template_user('parcele.html', zasedene=zasedene, parcele=cur1, seznam=seznam, dan = dan)


@post('/datum')
def datum():
    dan = str(request.forms.dan)
    redirect(url('pregled_parcel_dan', dan=dan))

@get('/parcele/<dan>')
@cookie_required
@cookie_required_receptor
def pregled_parcel_dan(dan):
    cur.execute("""
                SELECT parcela.id, uporabnik.ime, uporabnik.priimek, rezervacije.id FROM parcela
                LEFT JOIN rezervacije ON parcela.id = rezervacije.rezervirana_parcela
                LEFT JOIN uporabnik ON gost = uporabnik.id
                WHERE pricetek_bivanja <= %s AND %s <= pricetek_bivanja + st_nocitev;
                """,[dan,dan,])
    zasedene = cur
    cur1.execute("""SELECT id, st_gostov FROM parcela
                ORDER BY id""")
    sz = cur.fetchall()
    seznam = [value[0] for value in sz]
    return template_user('parcele.html', zasedene=zasedene, parcele=cur1, seznam=seznam, dan=dan)


static_dir = "./img"


@route("/img/<filename:path>")
def static(filename):
    return static_file(filename, root=static_dir)


# UREJANJE REZERVACIJ
@get('/urejanje/<id>')
@cookie_required
@cookie_required_receptor
def urejanje_rezervacije_get(id):
    #receptor = request.cookies.get("uporabnisko_ime")
    id_rez = id
    cur.execute("""
                SELECT rezervacije.id AS id_rezervacije, pricetek_bivanja, st_nocitev, odrasli, otroci, rezervirana_parcela, rezervacije.gost AS id_gosta, uporabnik.ime AS ime_gosta, uporabnik.priimek AS priimek_gosta FROM rezervacije
                LEFT JOIN uporabnik ON gost = uporabnik.id
                WHERE rezervacije.id = %s""", (id_rez,))
    return template_user('urejanje_rezervacije.html', rezervacija=cur)


@post('/urejanje/')
@cookie_required
@cookie_required_receptor
def urejanje_rezervacije_post():
    id_rez = request.forms.id_rez
    redirect(url('urejanje_rezervacije_get', id=id_rez))


@post('/urejanje_rezervacije/')
@cookie_required
@cookie_required_receptor
def uredi_rezervacijo():
    id_rez = request.forms.id_rezervacije
    zacetek_nocitve = request.forms.zacetek_nocitve
    stevilo_dni = str(request.forms.stevilo_dni)
    stevilo_odraslih = str(request.forms.stevilo_odraslih)
    stevilo_otrok = str(request.forms.stevilo_otrok)

    cur.execute(
        "SELECT rezervirana_parcela FROM rezervacije WHERE id = %s", (id_rez,))
    id_parcele = cur.fetchone()
    id_parcele = id_parcele[0]


    if stevilo_dni.isdigit() and stevilo_odraslih.isdigit() and stevilo_otrok.isdigit():
        stevilo_dni = int(request.forms.stevilo_dni)
        stevilo_odraslih = int(request.forms.stevilo_odraslih)
        stevilo_otrok = int(request.forms.stevilo_otrok)
    else:
        sporocilo = "Bodite pozorni pri vnašanju podatkov."
        cur.execute("""
                SELECT rezervacije.id AS id_rezervacije, pricetek_bivanja, st_nocitev, odrasli, otroci, rezervirana_parcela, rezervacije.gost AS id_gosta, uporabnik.ime AS ime_gosta, uporabnik.priimek AS priimek_gosta FROM rezervacije
                LEFT JOIN uporabnik ON gost = uporabnik.id
                WHERE rezervacije.id = %s""", (id_rez,))
        return template_user('urejanje_rezervacije.html', rezervacija=cur, napaka=sporocilo)
        

    if stevilo_odraslih + stevilo_otrok > 8:
        sporocilo = "Presegli ste število dovoljenih oseb."
        cur.execute("""
                SELECT rezervacije.id AS id_rezervacije, pricetek_bivanja, st_nocitev, odrasli, otroci, rezervirana_parcela, rezervacije.gost AS id_gosta, uporabnik.ime AS ime_gosta, uporabnik.priimek AS priimek_gosta FROM rezervacije
                LEFT JOIN uporabnik ON gost = uporabnik.id
                WHERE rezervacije.id = %s""", (id_rez,))
        return template_user('urejanje_rezervacije.html', rezervacija=cur, napaka=sporocilo)
        

    seznam_prostih_parcel = repo.dobi_proste_parcele_brez_moje_rezervacije(
        id_rezervacije=id_rez, datum_nove=zacetek_nocitve, st_dni_nove=stevilo_dni, st_odraslih=stevilo_odraslih, st_otrok=stevilo_otrok)
    seznam = [value[0] for value in seznam_prostih_parcel]

    if seznam_prostih_parcel == []:
        sporocilo = "Za izbrane parametre ni prostih parcel"
        cur.execute("""
                SELECT rezervacije.id AS id_rezervacije, pricetek_bivanja, st_nocitev, odrasli, otroci, rezervirana_parcela, rezervacije.gost AS id_gosta, uporabnik.ime AS ime_gosta, uporabnik.priimek AS priimek_gosta FROM rezervacije
                LEFT JOIN uporabnik ON gost = uporabnik.id
                WHERE rezervacije.id = %s""", (id_rez,))
        return template_user('urejanje_rezervacije.html', rezervacija=cur, napaka=sporocilo)

    elif int(id_parcele) in seznam:
        prosta_parcela = id_parcele
        repo.posodobi_rezervacijo(
            id_rez, zacetek_nocitve, stevilo_dni, stevilo_odraslih, stevilo_otrok, prosta_parcela)
    else:
        prosta_parcela = seznam[0]
        repo.posodobi_rezervacijo(
            id_rez, zacetek_nocitve, stevilo_dni, stevilo_odraslih, stevilo_otrok, prosta_parcela)

    redirect(url('rezervacije_get'))


conn = psycopg2.connect(database=auth.db, host=auth.host,
                        user=auth.user, password=auth.password, port=DB_PORT)
cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
cur1 = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)

run(host='localhost', port=SERVER_PORT, reloader=RELOADER)
