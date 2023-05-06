

# rezervacije: bere, ureja, briše, naredi novo r
# registracija gosta 
# registracija receptorja --> vidi vse rezervacije: lahko glede na dan začetka rezervacin 
# in glede na dan zacetek + stevilo nočitev

# uvozimo psycopg2
import psycopg2, psycopg2.extensions, psycopg2.extras
psycopg2.extensions.register_type(psycopg2.extensions.UNICODE) # se znebimo problemov s šumniki

from typing import List, TypeVar, Type, Callable
from data.model import *    #uvozimo classe tabel


#from pandas import DataFrame
#from re import sub


import data.auth as auth  
from datetime import date



class Repo:

    def __init__(self):
        self.conn = psycopg2.connect(database=auth.db, host=auth.host, user=auth.user, password=auth.password, port=5432)
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
              VALUES (%s, %s, %s, %s, %s, %s) RETURNING id; """, (uporabnik.uporabnisko_ime, uporabnik.geslo, uporabnik.ime, uporabnik.priimek, uporabnik.rojstvo, uporabnik.nacionalnost))
        uporabnik.id = self.cur.fetchone()[0]
        self.conn.commit()
        return uporabnik
    

    def tabela_rezervacije(self, prvi_dan) -> List[rezervacije]:
        #funkcija prikaze tabelo rezervacij, ki se zacnejo na 'prvi_dan'
        self.cur.execute("""
            SELECT * FROM rezervacije
            WHERE pricetek_bivanja = %s """, (prvi_dan,))
        return [rezervacije(id, pricetek_bivanja, st_nocitev, odrasli, otroci, rezervirana_parcela, gost) for (id, pricetek_bivanja, st_nocitev, odrasli, otroci, rezervirana_parcela, gost) in self.cur.fetchall()]


    def dodaj_rezervacije(self, rezervacije:rezervacije) -> rezervacije:
        # najprej je treba preveriti če je takšno rezervacijo možno narediti:

        # ali je izbrana parcela primerna za otroci + odrasli <= st_gostov?
        # ali je parcela prosta na izbrane dni? 
        # --  to se lahko naredi tudi v aplikaciji tako, da je možno izbrati za rezervacijo le parcele, ki so primerne in proste

        self.cur.execute("""
            INSERT INTO rezervacije (pricetek_bivanja, st_nocitev, odrasli, otroci, rezervirana_parcela, gost)
              VALUES (%s, %s, %s, %s, %s, %s) RETURNING id; """, (rezervacije.pricetek_bivanja, rezervacije.st_nocitev, rezervacije.odrasli, rezervacije.otroci, rezervacije.rezervirana_parcela, rezervacije.gost))
        rezervacije.id = self.cur.fetchone()[0]
        self.conn.commit()
        return rezervacije
    

    ####

    def tabela_parcela(self, prvi_dan, st_dni, st_gostov) ->List[parcela]:
        # funkcija izpiše seznam vseh parcel, katere bi bile primerne za željeno rezervacijo = st_gostov & izbrane dni

        # zdruziti je treba tabelo rezervacij in tabelo parcel --> dobimo proste parcele
        # nato vzamemo parcele katere so primerne za dano st_gostov



            # IDK?? 
            self.cur.execute("""
            SELECT * FROM parcele
            WHERE NOT EXISTS(
                SELECT 
            )
            WHERE st_gostov = %s """, (prvi_dan, st_dni, st_gostov))


        return [parcela(id, st_gostov) for (id, st_gostov) in self.cur.fetchall()]




        

