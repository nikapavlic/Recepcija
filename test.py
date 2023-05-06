from data.model import *
from database import Repo

import os

import data.auth as auth

# uvozimo psycopg2
import psycopg2, psycopg2.extensions, psycopg2.extras
psycopg2.extensions.register_type(psycopg2.extensions.UNICODE) # se znebimo problemov s šumniki

import os

# priklopimo se na bazo
conn = psycopg2.connect(database=auth.db, host=auth.host, user=auth.user, password=auth.password, port=5432)
conn.set_isolation_level(psycopg2.extensions.ISOLATION_LEVEL_AUTOCOMMIT) # onemogočimo transakcije
cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)

repo = Repo()

a =repo.tabela_uporabnik()
print(a)

uporabnik = uporabnik(0, 'ana', 'ana123', 'ana', 'banana', '1999-05-31', 'BRA')


repo.dodaj_uporabnik(uporabnik)

a = repo.tabela_rezervacije('2023-05-31')
print(a)


rezervacija = rezervacije(0, '2023-05-31', 10, 2, 2, 1, 14)

# repo.dodaj_rezervacije(rezervacija) #zakomentiran da ne dodja vsakic novo rezervacijo

a = repo.tabela_rezervacije('2023-05-31')
print(a)