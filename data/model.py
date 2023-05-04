from dataclasses import dataclass, field

@dataclass
class parcela:
    id: int = field(default=0)
    st_gostov: int = field(default=0)

@dataclass
class drzava:
    kratica: str = field(default="")
    ime: str = field(default="")

@dataclass 
class uporabnik:
    id: int = field(default=0)
    uporabnisko_ime: str = field(default="")
    geslo: str = field(default="")
    ime: str = field(default="")
    priimek: str = field(default="")
    rojstvo: str = field(default="")
    nacionalnost: str = field(default="")

@dataclass
class receptor:
    emso: str = field(default="")
    uporabnisko_ime: str = field(default="")
    geslo: str = field(default="")
    ime: str = field(default="")
    priimek: str = field(default="")

@dataclass
class rezervacije:
    id: int = field(default=0)
    pricetek_bivanja: str = field(default="")
    st_nocitev: int = field(default=0)
    odrasli: int = field(default=0)
    otroci: int = field(default=0)
    rezervirana_parcela: int = field(default=0)
    gost: int = field(default=0)

@dataclass
class racun:
    id: int = field(default=0)
    id_rezervacije: int = field(default=0)
    izdajatelj: str = field(default="")

