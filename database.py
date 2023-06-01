

# rezervacije: bere, ureja, briše, naredi novo r
# registracija gosta 
# registracija receptorja --> vidi vse rezervacije: lahko glede na dan začetka rezervacin 
# in glede na dan zacetek + stevilo nočitev
from datetime import datetime as dt, timedelta
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
              VALUES (%s, %s, %s, %s, %s, %s); """, (uporabnik.uporabnisko_ime, uporabnik.geslo, uporabnik.ime, uporabnik.priimek, uporabnik.rojstvo, uporabnik.nacionalnost))
        self.conn.commit()
        return uporabnik
    

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
    
    # def dobi_proste_parcele(self, datum_nove, st_dni_nove, st_odraslih, st_otrok):
    #     datum_zacetka_nove = dt.strptime(datum_nove, '%Y-%m-%d').date() 
    #     #datum_zacetka_nove = datum_nove
    #     self.cur.execute("""
    #     SELECT DISTINCT parcela.id FROM parcela  
    #     LEFT JOIN rezervacije ON rezervacije.rezervirana_parcela = parcela.id
    #     WHERE st_gostov >= %s""", (st_odraslih + st_otrok,))
    #     parcele_seznam = self.cur.fetchall()
    #     parcele_na_voljo = [parcela for seznam in parcele_seznam for parcela in seznam]
    #     self.cur.execute("""
    #     SELECT * FROM parcela  
    #     LEFT JOIN rezervacije ON rezervacije.rezervirana_parcela = parcela.id
    #     WHERE st_gostov >= %s""", (st_odraslih + st_otrok,))
    #     for stara_rezervacija in self.cur.fetchall():
    #         if stara_rezervacija[3] == None:
    #             continue
    #         elif stara_rezervacija[3] <= datum_zacetka_nove and stara_rezervacija[3] + timedelta(days=stara_rezervacija[4]) > datum_zacetka_nove:
    #             parcele_na_voljo.remove(stara_rezervacija[0])
    #         elif stara_rezervacija[3] >= datum_zacetka_nove and datum_zacetka_nove + timedelta(days=st_dni_nove) > stara_rezervacija[3]:
    #             parcele_na_voljo.remove(stara_rezervacija[0])
    #         else:
    #             continue
    #     #return parcele_na_voljo
    #     return datum_zacetka_nove

    def dobi_proste_parcele(self, datum_nove, st_dni_nove, st_odraslih, st_otrok):
        self.cur.execute(
            """SELECT parcela.id FROM parcela
            LEFT JOIN rezervacije ON rezervacije.rezervirana_parcela = parcela.id
            WHERE st_gostov >= %s AND parcela.id NOT IN 
                (SELECT parcela.id FROM parcela
                LEFT JOIN rezervacije ON rezervacije.rezervirana_parcela = parcela.id WHERE
                pricetek_bivanja + st_nocitev  > TO_DATE(%s, 'YYYY-MM-DD') AND
                pricetek_bivanja < TO_DATE(%s, 'YYYY-MM-DD') + %s)""",(st_odraslih+st_otrok, datum_nove, datum_nove, int(st_dni_nove)))
        prosta_parcela = self.cur.fetchone()
        return prosta_parcela





    def zbrisi_rezervacijo(self, id_rezervacije):
        self.cur.execute("""DELETE FROM rezervacije WHERE id = %s""", (id_rezervacije,))
        self.conn.commit()
        return 
#         

    

    ####

    #def tabela_parcela(self, prvi_dan, st_dni, st_gostov) ->List[parcela]:
        # funkcija izpiše seznam vseh parcel, katere bi bile primerne za željeno rezervacijo = st_gostov & izbrane dni

        # zdruziti je treba tabelo rezervacij in tabelo parcel --> dobimo proste parcele
        # nato vzamemo parcele katere so primerne za dano st_gostov



            # IDK?? 
        #     self.cur.execute("""
        #     SELECT * FROM parcele
        #     WHERE NOT EXISTS(
        #         SELECT 
        #     )
        #     WHERE st_gostov = %s """, (prvi_dan, st_dni, st_gostov))


        # return [parcela(id, st_gostov) for (id, st_gostov) in self.cur.fetchall()]

        
        # datum_zacetka_stare, st_dni_stare, datum_zacetka_nove, st_dni_nove

        # if datum_zacetka_stare <= datum_zacetka_nove and datum_zacetka_stare + st_dni_stare > datum_zacetka_nove
        #   parcela je zasedena
        # elseif datum_zacetka_stare >= datum_zacetka_nove and datum_zacetka_nove + st_dni_nove > datum_zacetka_stare
        #   parcela je zasedena
        # else
        #   parcela prosta