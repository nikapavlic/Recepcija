from data.model import *
from database import Repo
from datetime import datetime as dt
from datetime import date

import os

import data.auth as auth

# uvozimo psycopg2
import psycopg2, psycopg2.extensions, psycopg2.extras
psycopg2.extensions.register_type(psycopg2.extensions.UNICODE) # se znebimo problemov s šumniki

import os

# priklopimo se na bazo
conn = psycopg2.connect(database=auth.db, host=auth.host, user=auth.user, password=auth.password, port=5432)
#conn.set_isolation_level(psycopg2.extensions.ISOLATION_LEVEL_AUTOCOMMIT) # onemogočimo transakcije
cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)

repo = Repo()

a =repo.tabela_uporabnik()
print(a)

#uporabnik = uporabnik(0, 'ana', 'ana123', 'ana', 'banana', '1999-05-31', 'BRA')
uporabnik = uporabnik(uporabnisko_ime = 'lara123123' , geslo = 'la1223', ime='Lara', priimek='Ninič', rojstvo='2002-06-29', nacionalnost='SVN') 

## uporabnik = uporabnik('aba', 'ina123', 'Lina', 'Nana', '1990-05-31', 'SVN') ta ne dela

repo.dodaj_uporabnik(uporabnik)

a = repo.tabela_rezervacije('2023-05-31')
print(a)


rezervacija1 = rezervacije(pricetek_bivanja='2023-04-30', st_nocitev=10, odrasli=2, otroci=2, rezervirana_parcela=1, gost=14)

#repo.dodaj_rezervacije(rezervacija1) #zakomentiran da ne dodja vsakic novo rezervacijo

b = repo.tabela_rezervacije('2023-05-31')
print(b)

test = repo.dobi_proste_parcele('2023-05-31',5,2,2)
print(test)

cur.execute("SELECT id FROM uporabnik")
id_gosta = cur.fetchall()[1][0]
print(id_gosta)

seznam_prostih_parcel = repo.dobi_proste_parcele('2023-08-11', 3, 2, 2)
print(seznam_prostih_parcel)

parcele = repo.dobi_proste_parcele_brez_moje_rezervacije(50,'2023-08-11', 3, 2, 2 )
id_parcele = 24
seznam = [value[0] for value in parcele]
if seznam == []:
    print('prazen') #tukaj bi bilo fajn da se izpiše žal ni prostih parcel
elif int(id_parcele) in seznam:
    print(id_parcele)
else:
    print(seznam[0])
print(seznam)


# datum_zacetka_nove = dt.strptime('2024-04-30', '%Y-%m-%d').date()
# seznam_prostih_parcel1 = repo.dobi_proste_parcele(datum_zacetka_nove, 3, 2, 1)
# print(seznam_prostih_parcel1)