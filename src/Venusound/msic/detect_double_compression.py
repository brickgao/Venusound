# -*- coding: utf-8 -*-

from Venusound import *
import os, wave_op, eyed3, sys, tempfile, shutil
from collections import Counter
from libsvm.svmutil import *
from Venusound.models.LogDoubleCompression import log_double_compression
from Venusound.models.User import user

# Decoder path
_decoder = os.path.abspath(u'./Venusound/msic/mpg123_decode/mpg123_to_wav.exe')

# Encoder path
_encoder = os.path.abspath(u'./Venusound/msic/lame_encode/lame_detect_double_compression.exe')

# LibSVM models
_libsvm_model_list = {32 : os.path.abspath(u'./Venusound/msic/libsvm_model/32.model'),
                      64 : os.path.abspath(u'./Venusound/msic/libsvm_model/64.model'),
                      96 : os.path.abspath(u'./Venusound/msic/libsvm_model/96.model'),
                      128 : os.path.abspath(u'./Venusound/msic/libsvm_model/128.model')}

def get_avg():
    _list, _total = [], []
    for _i in range(10):
        _total.append([])
        _list.append(0.0)
    with open(u'data.tmp', 'r') as _origin_output:
        while True:
            _line = _origin_output.readline()
            if _line == '':     break
            if _line == '\n':   continue
            _q_mdct_arr = _line.split(' ')[:-1]
            _q_mdct_arr = map(int, _q_mdct_arr)
            _q_mdct_dict = dict(Counter(_q_mdct_arr))
            for _i in range(10):
                if _i in _q_mdct_dict:
                    _total[_i].append(_q_mdct_dict[_i])
                else:
                    _total[_i].append(0)
        for _i in range(10):
            _list[_i] = float(sum(_total[_i])) / len(_total[_i])
    os.remove(u'data.tmp')
    return _list

def get_feature(_file_path):
    _audio = eyed3.load(_file_path)
    _audio_bitrate = str(_audio.info.bit_rate[1])
    _origin_avg, _double_avg = [], []
    _recv = os.popen((_decoder + u' \"' + _file_path + u'\" tmp.wav').encode('gbk')).read()
    _origin_avg = get_avg()
    os.remove(u'tmp.wav')
    _recv = os.popen((_encoder + u' --decode \"' + _file_path + u'\" tmp.wav').encode('gbk')).read()
    wave_op.del_frames(u'tmp.wav', 200)
    _recv = os.popen((_encoder + u' tmp_processed.wav tmp.mp3 -b ' + _audio_bitrate).encode('gbk')).read()
    os.remove(u'tmp.wav')
    os.remove(u'tmp_processed.wav')
    _recv = os.popen((_decoder + u' tmp.mp3 tmp.wav').encode('gbk')).read()
    _double_avg = get_avg()
    os.remove(u'tmp.wav')
    _feature = {}
    for _i in range(10):
        _feature[_i + 1] = _origin_avg[_i] - _double_avg[_i]
    return _feature

def detect_double_compression_main(_file_path):
    _abs_file_path = os.path.abspath(_file_path)
    _audio = eyed3.load(_abs_file_path)
    _audio_bitrate = _audio.info.bit_rate[1]
    _log_double_compression_info = log_double_compression.query.filter_by(file_path=_file_path).first()
    _user_info = user.query.filter_by(username=_log_double_compression_info.username).first()
    _m = None
    if _audio_bitrate in _libsvm_model_list:
        _m = svm_load_model(_libsvm_model_list[_audio_bitrate])
    else:
        _log_double_compression_info.flag = -1
        db.session.add(_log_double_compression_info)
        db.session.commit()
        return None
    _folder_name = _file_path.split('\\')[2].split('.')[0]
    _temp_path = os.path.join(tempfile.gettempdir(), _folder_name)
    if not os.path.exists(_temp_path):
        os.makedirs(_temp_path)
    else:
        shutil.rmtree(_temp_path)
        os.makedirs(_temp_path)
    os.chdir(_temp_path)
    _x, _y = [], [0]
    _x.append(get_feature(_abs_file_path))
    p_labels, p_acc, p_vals = svm_predict(_y, _x, _m)
    _log_double_compression_info.flag = p_labels[0]
    _user_info.need_refresh_double_compression = 1
    db.session.add(_log_double_compression_info)
    db.session.add(_user_info)
    db.session.commit()
    return None
