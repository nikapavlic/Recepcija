import random
import string
import names
from datetime import datetime, timedelta
import pandas
import pandas as pd
import numpy as np

tabela = pd.read_csv(r"C:\Users\Holc\Documents\Lea\FMF\3_letnik\Osnove_podatkovnih_baz\Projekt\Recepcija\podatki\drzave.csv", sep='semicolon', header=None)
#print(tabela)

tabel_v_list = tabela.values.tolist()
elementi = [sublist[0].split(';')[0] for sublist in tabel_v_list]
kratice = random.choices(elementi, k=10)

#print(kratice)

# ime = names.get_full_name()
# print(ime)

# Random uporabniska imena
uporabniska_imena = []
for i in range(10):
    uporabnisko_ime = ''.join(random.choices(string.ascii_lowercase, k=8))
    uporabniska_imena.append(uporabnisko_ime)

# Random gesla
gesla = []
for i in range(10):
    geslo = ''.join(random.choices(string.ascii_letters + string.digits, k=10))
    gesla.append(geslo)

# Random imena
imena = []
for i in range(10):
    ime = ''.join(names.get_first_name())
    imena.append(ime)

# Random priimki
priimki = []
for i in range(10):
    priimek = ''.join(names.get_last_name())
    priimki.append(priimek)


# Random datumi
datumi = []
for i in range(10):
    zacetek = datetime(1950, 1, 1)
    konec = datetime(2007, 1, 1)
    random_datum = zacetek + timedelta(days=random.randint(0, (konec - zacetek).days))
    datumi.append(random_datum.strftime("%Y-%m-%d"))

# Pretvarjanje v SQL
sql_stavki = []
for i in range(10):
    sql_stavek = f"INSERT INTO uporabnik (uporabnisko_ime, geslo, ime, priimek, rojstvo, nacionalnost) VALUES ('{uporabniska_imena[i]}', '{gesla[i]}', '{imena[i]}', '{priimki[i]}', '{datumi[i]}', '{kratice[i]}');"
    sql_stavki.append(sql_stavek)

# Print the SQL insert statements
for sql_stavek in sql_stavki:
    print(sql_stavek)
