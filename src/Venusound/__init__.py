# -*- coding: utf-8 -*-

from flask import Flask
from flask.ext.sqlalchemy import SQLAlchemy
from Venusound import *

app = Flask(__name__)

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///db.sqlite'
app.config['SECRET_KEY'] = 'quaerendoinvenietis'

db = SQLAlchemy(app)

from models.User import user
from models.LogDoubleCompression import log_double_compression
from models.LogCheckOffset import log_check_offset
from models.UploadFiles import upload_files

db.create_all()
