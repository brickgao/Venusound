# -*- coding: utf-8 -*-

from Venusound import db

class log_double_compression(db.Model):

    event_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    username = db.Column(db.String(80), db.ForeignKey('user.username'))
    create_time = db.Column(db.DateTime, unique=False)
    file_name = db.Column(db.String(250), unique=False)
    file_path = db.Column(db.String(500), unique=False)
    file_size = db.Column(db.Integer, unique=False)
    play_time = db.Column(db.Float, unique=False)
    bitrate = db.Column(db.Integer, unique=False)
    hash_val = db.Column(db.String(250), unique=False)
    flag = db.Column(db.Integer, unique=False)
    user = db.relationship('user',
                           primaryjoin='log_double_compression.username == user.username',
                           backref=db.backref('log_double_compression', order_by='log_double_compression.username'))


    def __init__(self, username, create_time, file_name, file_path, file_size, bitrate, play_time, hash_val, flag):
        
        self.username = username
        self.create_time = create_time
        self.file_name = file_name
        self.file_path = file_path
        self.file_size = file_size
        self.bitrate = bitrate
        self.play_time = play_time
        self.hash_val = hash_val
        self.flag = flag
