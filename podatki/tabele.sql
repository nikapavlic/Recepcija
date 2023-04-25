-- Active: 1681383332221@@baza.fmf.uni-lj.si@5432@sem2023_nikap@public
CREATE TABLE parcela (
    ID SERIAL PRIMARY KEY,
    st_gostov INTEGER NOT NULL
);

INSERT INTO parcela (st_gostov) VALUES (2);


CREATE TABLE drzava (
    kratica TEXT PRIMARY KEY NOT NULL,
    ime TEXT
);

DROP TABLE uporabnik;

CREATE TABLE uporabnik (
    ID SERIAL NOT NULL PRIMARY KEY,
    uporabnisko_ime TEXT UNIQUE NOT NULL,
    geslo TEXT,
    ime TEXT,
    priimek TEXT,
    rojstvo DATE,
    nacionalnost TEXT REFERENCES drzava(kratica) 
);

CREATE TABLE receptor(
    emso TEXT PRIMARY KEY NOT NULL,
    uporabnisko_ime  TEXT UNIQUE NOT NULL,
    geslo TEXT,
    ime TEXT,
    priimek TEXT
);

CREATE TABLE rezervacije (
    ID SERIAL PRIMARY KEY,
    pricetek_bivanja DATE NOT NULL,
    st_nocitev INTEGER NOT NULL,
    odrasli INTEGER,
    otroci INTEGER,
    rezervirana_parcela INTEGER NOT NULL REFERENCES parcela(ID),
    gost INTEGER NOT NULL REFERENCES uporabnik(ID)
);

CREATE TABLE racun(
    ID SERIAL PRIMARY KEY,
    id_rezervacije INTEGER REFERENCES rezervacije(ID),
    izdajatelj TEXT REFERENCES receptor(emso)
);



