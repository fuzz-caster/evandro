from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from flask import g
from flask.cli import with_appcontext
from werkzeug.local import LocalProxy
from werkzeug.security import generate_password_hash
from sqlalchemy import Column
from sqlalchemy import Date
from sqlalchemy import Integer
from sqlalchemy import String
from sqlalchemy.ext.declarative import declarative_base
import click
import pandas as pd
from datetime import datetime
from evandro.config import  DATABASE_URI

Base = declarative_base()

_engine = create_engine(DATABASE_URI)
_DbSession = sessionmaker(autoflush=True)

class Transaksi(Base):
    __tablename__ = "transaksi"
    id = Column(Integer, primary_key=True)
    tanggal = Column(Date, nullable=False)
    produksi = Column(Integer, nullable=False)
    persediaan = Column(Integer, nullable=False)
    penjualan = Column(Integer, nullable=False)
    permintaan = Column(Integer, nullable=False)

    @classmethod
    def fromdict(cls, d):
        allowed = ('tanggal', 'produksi', "penjualan", "persediaan", "permintaan")
        df = {k: v for k, v in d.items() if k in allowed}
        return cls(**df)

    def update(self, **kwargs):
        allowed = ('tanggal', 'produksi', "penjualan", "persediaan", "permintaan")
        items = filter(lambda pair: pair[0] in allowed, kwargs.items())
        for k, v in items:
            setattr(self, k, v)

    def to_dict(self):
        return {
            "id": self.id,
            "tanggal": self.tanggal.isoformat(),
            "produksi": self.produksi,
            "persediaan": self.persediaan,
            "penjualan": self.penjualan,
            "permintaan": self.permintaan
        }

class Rule(Base):
    __tablename__ = "rule"
    id = Column(Integer, primary_key=True)
    produksi = Column(Integer, nullable=False)
    penjualan = Column(Integer, nullable=False)
    persediaan = Column(Integer, nullable=False)
    permintaan = Column(Integer, nullable=False)

    def to_list(self):
        return [self.produksi, self.penjualan, self.persediaan]

    def to_tuple(self):
        return (self.produksi, self.penjualan, self.persediaan)

    def to_dict(self):
        return {
            "id": self.id,
            "produksi": self.produksi,
            "penjualan": self.penjualan,
            "persediaan": self.persediaan,
            "permintaan": self.permintaan
        }

    @classmethod
    def fromdict(cls, d):
        allowed = ('produksi', "penjualan", "persediaan", "permintaan")
        df = {k: v for k, v in d.items() if k in allowed}
        return cls(**df)


class User(Base):
    __tablename__ = 'user'
    id = Column(Integer, primary_key=True)
    username = Column(String(250), nullable=False)
    nama = Column(String(250), nullable=False)
    password = Column(String(250), nullable=False)
    role = Column(String(250), nullable=False)
    email = Column(String(250), nullable=True)

    def to_dict(self):
        return {
            'id': self.id,
            'username': self.username,
            'nama': self.nama
        }


def _create_session():
    db_session = _DbSession(bind=_engine)
    return db_session

@click.command('init-db')
@with_appcontext
def _init_db():
    Base.metadata.create_all(_engine)
    dbsession = _create_session()

    Xs = pd.read_csv("data_2.csv")
    records = Xs.to_records()
    for r in records:
        tran = Transaksi()
        tran.tanggal = datetime.strptime(r[1], '%m/%d/%Y')
        tran.produksi = int(r[2])
        tran.penjualan = int(r[3])
        tran.persediaan = int(r[4])
        tran.permintaan = int(r[5])
        dbsession.add(tran)

    pd_rules = pd.read_csv("rules.csv")
    records = pd_rules.to_records()
    for r in records:
        rule = Rule()
        rule.produksi = int(r[1])
        rule.penjualan = int(r[2])
        rule.persediaan = int(r[3])
        rule.permintaan = int(r[4])
        dbsession.add(rule)

    nama = "Super Admin"
    username = "super-admin"
    password = "super-admin"
    role = "admin"

    phash = generate_password_hash(password)
    admin = User(
        nama=nama,
        username=username,
        role=role,
        password=phash
    )

    dbsession.add(admin)
    dbsession.commit()

def _get_db_session():
    if 'db_session' not in g:
        g.db_session = _create_session()
    return g.db_session

def _teardown_db_session(e=None):
    db_session = g.pop('db_session', None)
    if db_session is not None:
        db_session.close()


# Register session lifecycle hook to instance.
# Using function since we use factory.
def init_app(app=None):
    if app is None: raise Exception('App is none!')
    app.teardown_appcontext(_teardown_db_session)
    app.cli.add_command(_init_db)

db_session = LocalProxy(_get_db_session)

def rule_is_unique(tup):
    rules = db_session.query(Rule).all()
    var_tuple = lambda r: (r.produksi, r.penjualan, r.persediaan)
    rules_as_tuples = map(lambda r: var_tuple, rules)
    for r_tuple in rules_as_tuples:
        if r_tuple == tup:
            return False
    return True