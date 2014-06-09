# -*- coding: utf-8 -*-

from Venusound import *
from flask import Flask, render_template, request, flash, redirect, abort, session
from models.User import user
from models.LogDoubleCompression import log_double_compression
from models.LogCheckOffset import log_check_offset
from werkzeug import secure_filename
import hashlib, os

@app.route('/', methods=['GET'])
def GetIndex():
    return render_template('index.html')

@app.route('/login', methods=['GET', 'POST'])
def Login():
    if 'username' in session:
        flash(u'你需要登出后再登录', 'error')
        return redirect('/')
    if request.method == 'GET':
        return render_template('login.html')
    else:
        _username = request.form['username']
        _passwd = request.form['passwd']
        if _username == '':
            flash(u'请填写用户名', 'error')
            return redirect('/login')
        if _passwd == '':
            flash(u'请填写密码', 'error')
            return redirect('/login')
        _user_info = user.query.filter_by(username=_username).first()
        if not _user_info:
            flash(u'用户名不存在', 'error')
            return redirect('/login')
        else:
            _passwd_with_salt = hashlib.sha512(_passwd + _user_info.salt).hexdigest()
            if _passwd_with_salt == _user_info.passwd:
                session['username'] = _username
                flash(u'欢迎回来，' + _username, 'success')
                return redirect('/')
            else:
                flash(u'密码错误', 'error')
                return redirect('/login')

@app.route('/signup', methods=['GET', 'POST'])
def SignUp():
    if 'username' in session:
        flash(u'你需要登出后再注册', 'error')
        return redirect('/')
    if request.method == 'GET':
        return render_template('signup.html')
    else:
        _username = request.form['username']
        _passwd = request.form['passwd']
        if _username == '':
            flash(u'请填写用户名', 'error')
            return redirect('/signup')
        if _passwd == '':
            flash(u'请填写密码', 'error')
            return redirect('/signup')
        _user_info = user.query.filter_by(username=_username).first()
        if not _user_info:
            _user_info = user(_username, _passwd)
            db.session.add(_user_info)
            db.session.commit()
            flash(u'注册成功，请登录', 'success')
            return redirect('/login')
        else:
            flash(u'用户名已经存在', 'error')
            return redirect('/signup')

@app.route('/logout', methods=['GET'])
def Logout():
    session.pop('username', None)
    flash(u'登出成功', 'success')
    return redirect('/')

@app.route('/double_compression', methods=['GET', 'POST'])
def GetDoubleCompressionList():
    if not 'username' in session:
        flash(u'请先登录', 'error')
        return redirect('/')
    else:
        if request.method == 'GET':
            return render_template('double_compression_list.html')
        else:
            _username = session['username']
            _file = request.files['file']
            _file_name = _file.filename
            _s_file_name = secure_filename(_file.filename)
            _file_path = './upload'
            if not os.path.exists(_file_path):
                os.makedirs(_file_path)
            _file.save(os.path.join(_file_path, _s_file_name))
            flash(u'上传成功', 'success')
            return u'文件上传成功'
        
