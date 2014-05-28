# -*- coding: utf-8 -*-

from Venusound import db

class LogCheckOffset(db.Model):

    event_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    username = db.Column(db.String(80), db.ForeignKey('user.username'))
    create_time = db.Column(db.DateTime, unique=False)
    file_name = db.Column(db.String(250), unique=False)
    bitrate = db.Column(db.Integer, unique=False)
    hash_val = db.Column(db.String(250), unique=False)
    flag = db.Column(db.Integer, primary_key=True, autoincrement=True)
    info_dict = db.Column(db.PickleType, unique=False)
    user = db.relationship('user',
                           primaryjoin='User.username == username',
                           backref=db.backref('user', order_by='user.username'))


    def __init_(self, username, create_time, file_name, bitrate, hash_val, flag, info_dict):
        
        self.username = username
        self.create_time = create_time
        self.file_name = file_name
        self.bitrate = bitrate
        self.hash_val = hash_val
        self.flag = flag
        self.info_dict = info_dict
