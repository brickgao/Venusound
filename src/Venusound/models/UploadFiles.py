# -*- coding: utf-8 -*-

from Venusound import db

class upload_files(db.Model):

    file_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    username = db.Column(db.String(80), db.ForeignKey('user.username'))
    file_name = db.Column(db.String(80), unique=False)
    file_path = db.Column(db.String(400), unique=False)
    user = db.relationship('user',
                           primaryjoin='upload_files.username == user.username',
                           backref=db.backref('upload_files', order_by='upload_files.username'))


    def __init__(self, username, file_name, file_path):
        
        self.username = username
        self.file_name = file_name
        self.file_path = file_path
