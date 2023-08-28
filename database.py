from datetime import datetime as dt, timedelta
# uvozimo psycopg2
import psycopg2, psycopg2.extensions, psycopg2.extras
psycopg2.extensions.register_type(psycopg2.extensions.UNICODE) # se znebimo problemov s šumniki

from typing import List, TypeVar, Type, Callable
from data.model import *    #uvozimo classe tabel
import os

#from pandas import DataFrame
#from re import sub

import data.auth as auth  
from datetime import date

DB_PORT = os.environ.get('POSTGRES_PORT', 5432)

class Repo:

    def __init__(self):
        self.conn = psycopg2.connect(database=auth.db, host=auth.host, user=auth.user, password=auth.password, port=DB_PORT)
        self.cur = self.conn.cursor(cursor_factory=psycopg2.extras.DictCursor)

    
    def tabela_uporabnik(self) -> List[uporabnik]:
        self.cur.execute("""
            SELECT * FROM uporabnik
        """)
        return [uporabnik(id, uporabnisko_ime, geslo, ime, priimek, rojstvo, nacionalnost) for (id, uporabnisko_ime, geslo, ime, priimek, rojstvo, nacionalnost) in self.cur.fetchall()]


    def dodaj_uporabnik(self, uporabnik: uporabnik) -> uporabnik:
        # ali je že v tabeli?
        self.cur.execute("""
            SELECT * from uporabnik
            WHERE uporabnisko_ime = %s
          """, (uporabnik.uporabnisko_ime,))

        row = self.cur.fetchone()
        if row:
            uporabnik.id = row[0]
            return uporabnik
        
        #nov uporabnik
        self.cur.execute("""
            INSERT INTO uporabnik (uporabnisko_ime, geslo, ime, priimek, rojstvo, nacionalnost)
              VALUES (%s, %s, %s, %s, %s, %s); """, (uporabnik.uporabnisko_ime, uporabnik.geslo, uporabnik.ime, uporabnik.priimek, uporabnik.rojstvo, uporabnik.nacionalnost))
        self.conn.commit()
        return uporabnik
    
    def dodaj_receptor(self, receptor: receptor) -> receptor:
        # ali je že v tabeli?
        self.cur.execute("""
            SELECT * from receptor
            WHERE uporabnisko_ime = %s
          """, (receptor.uporabnisko_ime,))

        row = self.cur.fetchone()
        if row:
            receptor.id = row[0]
            return receptor
        
        #nov uporabnik
        self.cur.execute("""
            INSERT INTO receptor (emso,uporabnisko_ime, geslo, ime, priimek)
              VALUES (%s, %s, %s, %s, %s); """, (receptor.emso, receptor.uporabnisko_ime, receptor.geslo, receptor.ime, receptor.priimek))
        self.conn.commit()
        return receptor

    def tabela_rezervacije(self, prvi_dan) -> List[rezervacije]:
        #funkcija prikaze tabelo rezervacij, ki se zacnejo na 'prvi_dan'
        self.cur.execute("""
            SELECT * FROM rezervacije
            WHERE pricetek_bivanja = %s """, (prvi_dan,))
        return [rezervacije(id, pricetek_bivanja, st_nocitev, odrasli, otroci, rezervirana_parcela, gost) for (id, pricetek_bivanja, st_nocitev, odrasli, otroci, rezervirana_parcela, gost) in self.cur.fetchall()]


    def dodaj_rezervacije(self, rezervacije:rezervacije) -> rezervacije:
        self.cur.execute("""
            INSERT INTO rezervacije (pricetek_bivanja, st_nocitev, odrasli, otroci, rezervirana_parcela, gost)
              VALUES (%s, %s, %s, %s, %s, %s)
              returning id """, (rezervacije.pricetek_bivanja, rezervacije.st_nocitev, rezervacije.odrasli, rezervacije.otroci, rezervacije.rezervirana_parcela, rezervacije.gost))
        id,=self.cur.fetchone()
        self.conn.commit()
        return rezervacije
    

    def dobi_proste_parcele(self, datum_nove, st_dni_nove, st_odraslih, st_otrok):
        self.cur.execute(
            """SELECT parcela.id FROM parcela
            LEFT JOIN rezervacije ON rezervacije.rezervirana_parcela = parcela.id
            WHERE st_gostov >= %s AND parcela.id NOT IN 
                (SELECT parcela.id FROM parcela
                LEFT JOIN rezervacije ON rezervacije.rezervirana_parcela = parcela.id WHERE
                pricetek_bivanja + st_nocitev  > TO_DATE(%s, 'YYYY-MM-DD') AND
                pricetek_bivanja < TO_DATE(%s, 'YYYY-MM-DD') + %s)""",(int(st_odraslih)+int(st_otrok), datum_nove, datum_nove, int(st_dni_nove)))
        prosta_parcela = self.cur.fetchone()
        return prosta_parcela
    
    def dobi_proste_parcele_brez_moje_rezervacije(self, id_rezervacije, datum_nove, st_dni_nove, st_odraslih, st_otrok):
        self.cur.execute(
            """SELECT parcela.id FROM parcela
            LEFT JOIN rezervacije ON rezervacije.rezervirana_parcela = parcela.id
            WHERE st_gostov >= %s AND parcela.id NOT IN 
                (SELECT parcela.id FROM parcela
                LEFT JOIN rezervacije ON rezervacije.rezervirana_parcela = parcela.id 
                WHERE NOT rezervacije.id = %s AND
                pricetek_bivanja + st_nocitev  > TO_DATE(%s, 'YYYY-MM-DD') AND
                pricetek_bivanja < TO_DATE(%s, 'YYYY-MM-DD') + %s)""",(int(st_odraslih)+int(st_otrok), id_rezervacije, datum_nove, datum_nove, int(st_dni_nove)))
        prosta_parcela = self.cur.fetchall()
        return prosta_parcela

    def zbrisi_rezervacijo(self, id_rezervacije):
        self.cur.execute("""DELETE FROM rezervacije WHERE id = %s""", (id_rezervacije,))
        self.conn.commit()
        return 
#         
    def ustvari_racun(self, id_rez, emso):
        self.cur.execute("""INSERT INTO racun (id_rezervacije, izdajatelj) VALUES (%s, %s); """, (id_rez, emso))
        self.conn.commit()
        return
    
    def posodobi_rezervacijo(self, id_rezervacije, pricetek_bivanja, st_nocitev, odrasli, otroci, nova_parcela):
        self.cur.execute(
            """
            UPDATE rezervacije
            SET pricetek_bivanja = %s,
                st_nocitev = %s,
                odrasli = %s,
                otroci = %s,
                rezervirana_parcela = %s
            WHERE rezervacije.id = %s""", (pricetek_bivanja, int(st_nocitev), int(odrasli), int(otroci), int(nova_parcela), int(id_rezervacije)))
        self.conn.commit()
        return