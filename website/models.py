from xmlrpc.client import DateTime
from . import db
from flask_login import UserMixin
from sqlalchemy.sql import func
from datetime import datetime


class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(150))
    password = db.Column(db.String(150))
    date_created = db.Column(db.DateTime(timezone=True), default=datetime.now)


class customer(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    id_card = db.Column(db.String)
    firstname = db.Column(db.String(150))
    lastname = db.Column(db.String(150))
    bydliste = db.Column(db.String(150))
    phone = db.Column(db.String)
    email = db.Column(db.String)
    gdpr = db.Column(db.Boolean)
    contract = db.Column(db.Boolean)
    date_created = db.Column(db.DateTime(timezone=True), default=datetime.now)
    pujceno = db.relationship(
        'pujceno', backref="customer", passive_deletes=True)


class trailer(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(150))
    spz = db.Column(db.String(150))
    stk = db.Column(db.DateTime(timezone=True))
    status = db.Column(db.Boolean, default=False)
    zelkarta = db.Column(db.DateTime(timezone=True))
    price = db.Column(db.Integer)
    pujceno = db.relationship(
        'pujceno', backref="trailer", passive_deletes=True)
    back = db.relationship(
        'back', backref="trailer", passive_deletes=True)
    img = db.Column(db.String)
    type = db.Column(db.String)
    serialNumber = db.Column(db.String)
    note = db.Column(db.String)
    # category = db.relationship(
    #     'category', backref="trailer", passive_deletes=True)


class pujceno(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    customer_id = db.Column(db.Integer, db.ForeignKey(
        'customer.id', ondelete="CASCADE"), nullable=False)
    trailer_id = db.Column(db.Integer, db.ForeignKey(
        'trailer.id', ondelete="CASCADE"), nullable=False)
    back = db.relationship(
        'back', backref="pujceno", passive_deletes=True)
    date_created = db.Column(db.DateTime(timezone=True))
    date_back = db.Column(db.DateTime(timezone=True))
    when_back = db.Column(db.DateTime(timezone=True))
    note = db.Column(db.String)
    TotalPrice = db.Column(db.Integer)


class back(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    note = db.Column(db.String)
    pujceno_id = db.Column(db.Integer, db.ForeignKey(
        'pujceno.id', ondelete="CASCADE"), nullable=False)
    trailer_id = db.Column(db.Integer, db.ForeignKey(
        'trailer.id', ondelete="CASCADE"), nullable=False)


# Kategorie

# class category(db.Model):
#    id = db.Column(db.Integer, primary_key=True)
#    name = db.Column(db.String)
#    trailer_id = db.Column(db.Integer, db.ForeignKey(
#       'trailer.id', ondelete="CASCADE"), nullable=False)
