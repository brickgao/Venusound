# -*- coding: utf-8 -*-

import hashlib, string
from Venusound import db

class user(db.Model):
    
    username = db.Column(db.String(80), primary_key=True)
    passwd = db.Column(db.String(250), unique=False)
    salt = db.Column(db.String(10), unique=False)


    def __init__(self, username, passwd):
        
        _salt = ''.join(random.sample(string.ascii_letters + string.digits, 8))
        _passwd_with_salt = hashlib.sha512(passwd + _salt).hexdigest()
        self.username = username
        self.salt = _salt
        self.passwd = _passwd_with_salt
