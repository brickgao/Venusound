# -*- coding: utf-8 -*-

from flask import Flask
from flask.ext.sqlalchemy import SQLAlchemy
from Venusound import *

app = Flask(__name__)

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///bot_data.db'
app.config['SECRET_KEY'] = 'quaerendoinvenietis'

db = SQLAlchemy(app)

db.create_all()
