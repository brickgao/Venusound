# -*- coding: utf-8 -*-

from Venusound import *
from flask import Flask, render_template, request, flash, redirect, abort, session
from models.User import user
from models.LogDoubleCompression import log_double_compression
from models.LogCheckOffset import log_check_offset
import hashlib

@app.route('/', methods=['GET'])
def GetIndex():
    return render_template('index.html')

@app.route('/login', methods=['GET', 'POST'])
def Login():
    if 'username' in session:
        flash(u'你需要登出后在登录', 'error')
        return redirect('/manage')
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
                flash(u'欢迎回来，' + unicode(_username, 'gbk'), 'success')
                return redirect('/')
            else:
                flash(u'密码错误', 'error')
                return redirect('/login')
                
