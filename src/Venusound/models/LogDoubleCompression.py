# -*- coding: utf-8 -*-

from Venusound import db

class LogDoubleCompression(db.Model):

    event_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    username = db.Column(db.String(80), db.ForeignKey('User.username'))
    create_time = db.Column(db.DateTime, unique=False)
    file_name = db.Column(db.String(250), unique=False)
    bitrate = db.Column(db.Integer, unique=False)
    hash_val = db.Column(db.String(250), unique=False)
    flag = db.Column(db.Integer, primary_key=True, autoincrement=True)
    user = db.relationship('User',
                           primaryjoin='User.username == username',
                           backref=db.backref('User', order_by='User.username'))


    def __init_(self, username, create_time, file_name, bitrate, hash_val, flag):
        
        self.username = username
        self.create_time = create_time
        self.file_name = file_name
        self.bitrate = bitrate
        self.hash_val = hash_val
        self.flag = flag