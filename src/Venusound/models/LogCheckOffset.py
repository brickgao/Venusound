# -*- coding: utf-8 -*-

from Venusound import db

class log_check_offset(db.Model):

    event_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    username = db.Column(db.String(80), db.ForeignKey('user.username'))
    create_time = db.Column(db.DateTime, unique=False)
    file_name = db.Column(db.String(250), unique=False)
    file_path = db.Column(db.String(500), unique=False)
    bitrate = db.Column(db.Integer, unique=False)
    hash_val = db.Column(db.String(250), unique=False)
    flag = db.Column(db.Integer, unique=False)
    info_dict = db.Column(db.PickleType, unique=False)
    user = db.relationship('user',
                           primaryjoin='log_check_offset.username == user.username',
                           backref=db.backref('log_check_offset', order_by='log_check_offset.username'))


    def __init__(self, username, create_time, file_name, file_path, bitrate, hash_val, flag, info_dict):
        
        self.username = username
        self.create_time = create_time
        self.file_name = file_name
        self.file_path = file_path
        self.bitrate = bitrate
        self.hash_val = hash_val
        self.flag = flag
        self.info_dict = info_dict
