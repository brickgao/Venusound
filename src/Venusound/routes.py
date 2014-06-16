# -*- coding: utf-8 -*-

from Venusound import *
from flask import Flask, render_template, request, flash, redirect, abort, session
from models.User import user
from models.LogDoubleCompression import log_double_compression
from models.LogCheckOffset import log_check_offset
from models.UploadFiles import upload_files
from msic.detect_double_compression import detect_double_compression
from msic.check_offset import check_offset_main
import hashlib, os, datetime, eyed3, msic, multiprocessing, wave

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
            _username = session['username']
            _file_info_list = log_double_compression.query.filter_by(username=_username)
            _template_file_info_list = []
            _cnt = 1
            for _file_info in _file_info_list:
                _dict = {}
                _dict['id'] = str(_cnt)
                _dict['create_time'] = _file_info.create_time.strftime("%Y-%m-%d %H:%M:%S")
                _dict['file_name'] = _file_info.file_name
                _dict['bitrate'] = _file_info.bitrate
                _dict['md5'] = _file_info.hash_val
                _dict['flag'] = _file_info.flag
                _dict['make_check_offset_url'] = '/make_check_offset/' + \
                                                 _file_info.file_path.split('\\')[2].split('.')[0]
                _template_file_info_list.append(_dict)
                _cnt += 1
            return render_template('double_compression_list.html', info_list=_template_file_info_list)
        else:
            _username = session['username']
            _file = request.files['file']
            _file_name = _file.filename
            _folder_path = '.\upload'
            if not os.path.exists(_folder_path):
                os.makedirs(_folder_path)
            _datetime_now = datetime.datetime.now()
            _s_file_name = hashlib.md5(str(_datetime_now) + session['username']).hexdigest() + '.mp3'
            _file_path = os.path.join(_folder_path, _s_file_name)
            _file.save(_file_path)
            # Decode MP3
            _encoder = os.path.abspath(u'./Venusound/msic/lame_encode/lame_detect_double_compression.exe')
            _wav_file_path = unicode(_file_path[:-3] + 'wav', 'gbk')
            _wav_file_name = _file_name[:-3] + 'wav'
            _recv = os.popen((_encoder + u' --decode \"' + _file_path + u'\" \"' + _wav_file_path + '\"').encode('gbk')).read()
            _wav_upload_files_info = upload_files(_username, _wav_file_name, _wav_file_path)
            _md5 = ''
            with open(_file_path, 'rb') as _file_obj:
                _md5_obj = hashlib.md5()
                _md5_obj.update(_file_obj.read())
                _md5 = _md5_obj.hexdigest()
            _audio = eyed3.load(_file_path)
            _bitrate = _audio.info.bit_rate[1]
            _file_in = wave.open(_wav_file_path, 'rb')
            _play_time = _file_in.getparams()[3] / 22050.
            _file_size = os.path.getsize(_file_path)
            _log_double_compression_info = log_double_compression(_username, _datetime_now, _file_name, 
                                                                  _file_path, _file_size, _bitrate,
                                                                  _play_time, _md5, 0)
            _upload_files_info = upload_files(_username, _file_name, _file_path)
            db.session.add(_wav_upload_files_info)
            db.session.add(_log_double_compression_info)
            db.session.add(_upload_files_info)
            db.session.commit()
            _p = multiprocessing.Process(target=detect_double_compression, args=(_file_path,))
            _p.start()
            flash(u'上传成功', 'success')
            return u'文件上传成功'

@app.route('/upload/<_file_name>', methods=['GET'])
def getUploadFiles(_file_name):
    if not 'username' in session:
        flash(u'请先登录', 'error')
        return redirect('/')
    else:
        _username = session['username']
        _file_path = os.path.join('.\upload', _file_name)
        _upload_files_info = upload_files.query.filter_by(username=_username, file_path=_file_path).first()
        if _upload_files_info is None:
            return abort(404)
        else:
            _file_path = _upload_files_info.file_path
            with open(_file_path, 'rb') as _file_ret:
                return _file_ret.read()
            return abort(500)
        
@app.route('/check_offset', methods=['GET', 'POST'])
def GetCheckOffsetList():
    if not 'username' in session:
        flash(u'请先登录', 'error')
        return redirect('/')
    else:
        if request.method == 'GET':
            _username = session['username']
            _log_check_offset_info_list = log_check_offset.query.filter_by(username=_username)
            _template_file_info_list = []
            _cnt = 1
            for _file_info in _log_check_offset_info_list:
                _dict = {}
                _dict['id'] = str(_cnt)
                _dict['create_time'] = _file_info.create_time.strftime("%Y-%m-%d %H:%M:%S")
                _dict['file_name'] = _file_info.file_name
                _dict['bitrate'] = _file_info.bitrate
                _dict['md5'] = _file_info.hash_val
                _dict['flag'] = _file_info.flag
                _dict['log_url'] = '/check_offset/' + _file_info.file_path.split('\\')[2].split('.')[0]
                _template_file_info_list.append(_dict)
                _cnt += 1
            return render_template('check_offset_list.html', info_list=_template_file_info_list)
        else:
            _username = session['username']
            _file = request.files['file']
            _file_name = _file.filename
            _folder_path = '.\upload'
            if not os.path.exists(_folder_path):
                os.makedirs(_folder_path)
            _datetime_now = datetime.datetime.now()
            _s_file_name = hashlib.md5(str(_datetime_now) + session['username']).hexdigest() + '.mp3'
            _file_path = os.path.join(_folder_path, _s_file_name)
            _file.save(_file_path)
            # Decode MP3
            _encoder = os.path.abspath(u'./Venusound/msic/lame_encode/lame_detect_double_compression.exe')
            _wav_file_path = unicode(_file_path[:-3] + 'wav', 'gbk')
            _wav_file_name = _file_name[:-3] + 'wav'
            _recv = os.popen((_encoder + u' --decode \"' + _file_path + u'\" \"' + _wav_file_path + '\"').encode('gbk')).read()
            _wav_upload_files_info = upload_files(_username, _wav_file_name, _wav_file_path)
            _md5 = ''
            with open(_file_path, 'rb') as _file_obj:
                _md5_obj = hashlib.md5()
                _md5_obj.update(_file_obj.read())
                _md5 = _md5_obj.hexdigest()
            _audio = eyed3.load(_file_path)
            _bitrate = _audio.info.bit_rate[1]
            _file_in = wave.open(_wav_file_path, 'rb')
            _play_time = _file_in.getparams()[3] / 22050.
            _file_size = os.path.getsize(_file_path)
            _log_check_offset_info = log_check_offset(_username, _datetime_now, _file_name, _file_path, 
                                                      _file_size, _bitrate, _play_time, _md5, 0, [])
            _upload_files_info = upload_files(_username, _file_name, _file_path)
            db.session.add(_wav_upload_files_info)
            db.session.add(_log_check_offset_info)
            db.session.add(_upload_files_info)
            db.session.commit()
            _p = multiprocessing.Process(target=check_offset_main, args=(_file_path,))
            _p.start()
            flash(u'上传成功', 'success')
            return u'文件上传成功'
        
@app.route('/check_offset/<event_id>', methods=['GET'])
def GetCheckOffsetLog(event_id):
    if not 'username' in session:
        flash(u'请先登录', 'error')
        return redirect('/')
    else:
        _username = session['username']
        _file_path = os.path.join('.\upload', event_id + '.mp3')
        _log_check_offset_info = log_check_offset.query.filter_by(username=_username, file_path=_file_path).first()
        if _log_check_offset_info is None:
            flash(u'权限不足或者该检测不存在', 'error')
            return redirect('/check_offset')
        elif _log_check_offset_info.flag == 0:
            flash(u'检测尚未完成', 'error')
            return redirect('/check_offset')
        else:
            _dict = {}
            _dict['create_time'] = _log_check_offset_info.create_time.strftime("%Y-%m-%d %H:%M:%S")
            _dict['file_name'] = _log_check_offset_info.file_name
            _dict['bitrate'] = _log_check_offset_info.bitrate
            _dict['md5'] = _log_check_offset_info.hash_val
            _dict['flag'] = _log_check_offset_info.flag
            _dict['offset_list'] = _log_check_offset_info.offset_list
            _dict['file_size'] = _log_check_offset_info.file_size
            _dict['play_time'] = _log_check_offset_info.play_time
            _dict['event_id'] = event_id
            _dict['x-axis'] = [_i for _i in range(1, len(_dict['offset_list']) + 1)]
            _dict['distort-point'] = []
            _dict['conclusion'] = ['']
            _dict['mark_width'] = 1100. / len(_dict['offset_list'])
            _each_frame_time = _log_check_offset_info.play_time / len(_dict['offset_list'])
            _cnt = 0
            for _i in range(len(_dict['offset_list'])- 1):
                if _dict['offset_list'][_i] != _dict['offset_list'][_i + 1]:
                    _cnt += 1
                    _dict['conclusion'].append(u'%d. 篡改发生在第 %d 帧和第 %d 帧之间' % (_cnt, _i, _i + 1))
                    _dict['distort-point'].append(_each_frame_time * _i)
            _dict['conclusion'][0] = u'共有 %d 个篡改点：' % _cnt
            return render_template('check_offset_log.html', info=_dict)

@app.route('/make_check_offset/<event_id>', methods=['GET'])
def MakeCheckOffset(event_id):
    if not 'username' in session:
        flash(u'请先登录', 'error')
        return redirect('/')
    else:
        _username = session['username']
        _file_path = os.path.join('.\upload', event_id + '.mp3')
        _log_double_compression_info = log_double_compression.query.filter_by(username=_username, file_path=_file_path).first()
        if _log_double_compression_info is None:
            flash(u'该检测不存在', 'error')
            return redirect('/double_compression')
        elif _log_double_compression_info.flag <= 1:
            flash(u'检测尚未完成或者未经过重压缩', 'error')
            return redirect('/double_compression')
        else:
            _datetime_now = datetime.datetime.now()
            _file_name = _log_double_compression_info.file_name
            _file_path = _log_double_compression_info.file_path
            _file_size = _log_double_compression_info.file_size
            _bitrate = _log_double_compression_info.bitrate
            _play_time = _log_double_compression_info.play_time
            _md5 = _log_double_compression_info.hash_val
            _log_check_offset_info = log_check_offset(_username, _datetime_now, _file_name, _file_path, 
                                                      _file_size, _bitrate, _play_time, _md5, 0, [])
            db.session.add(_log_check_offset_info)
            db.session.commit()
            _p = multiprocessing.Process(target=check_offset_main, args=(_file_path,))
            _p.start()
            flash(u'新建篡改定位检测成功', 'success')
            return redirect('/check_offset')
