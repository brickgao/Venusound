# -*- coding: utf-8 -*-

from Venusound import *
import os, wave_op, eyed3, sys, tempfile, shutil, multiprocessing, math
from collections import Counter
from libsvm.svmutil import *
from Venusound.models.LogCheckOffset import log_check_offset

def mp3_pre_handle(_file_path, _db_l, _encoder):
    if not os.path.exists(u'.\wave_sample'):
        os.makedirs(u'.\wave_sample')
    else:
        os.rmdir(u'.\wave_sample')
        os.makedirs(u'.\wave_sample')
    _recv = os.popen((_encoder + u' --decode \"' + _file_path + u'\" tmp_origin.wav').encode('gbk')).read()
    _db_l = wave_op.get_decibel(u'tmp_origin.wav')
    for i in range(576):
        wave_op.del_frames(u'tmp_origin.wav', i)
        _new_path = os.path.join(u'.\wave_sample', unicode(str(i), 'gbk'))
        os.mkdir(_new_path)
        shutil.move(u'.\\tmp_processed.wav', os.path.join(_new_path, 'tmp_processed.wav'))

def deal_with_wave(_offset, _bitrate, _base_path, _encoder):
    _arg_dif_l = []
    os.chdir(os.path.join(_base_path, u'wave_sample', unicode(str(_offset), 'gbk')))
    _recv = os.popen((_encoder + u' tmp_processed.wav tmp.mp3 -b ' + unicode(_bitrate, 'gbk')).encode('gbk')).read()
    _tmp_l = []
    with open('data.tmp', 'r') as _file_in:
        for _i in range(2):  _line = _file_in.readline()
        while True:
            _line = _file_in.readline()
            if _line == '':     break
            if _line == '\n':   continue
            _mdct_arr = map(float, _line.split(' ')[:-1])
            _cnt = 0
            if _offset == 0:
                _avg = sum(_mdct_arr) / len(_mdct_arr)
                _dif = _avg - min(_mdct_arr)
                _arg_dif_l.append(_dif)
            for _i in range(576):
                _tmp = 10 * math.log(max((_mdct_arr[_i] ** 2) * (10 ** 10), 1.0), 10)
                if _tmp != 0.0:     _cnt += 1
            _tmp_l.append(_cnt)
    _len_mdct = len(_tmp_l)
    _after_sliding_win_l = []
    for _i in range(_len_mdct - 3):
        _after_sliding_win_l.append(min(_tmp_l[_i], _tmp_l[_i + 1], _tmp_l[_i + 2]))
    _after_sliding_win_l.append(min(_tmp_l[_len_mdct - 2], _tmp_l[_len_mdct - 1]))
    _after_sliding_win_l.append(_tmp_l[_len_mdct - 1])
    return (_offset, _after_sliding_win_l, _arg_dif_l)

def deal_with_wave_mf_wrap(args):
    return deal_with_wave(*args)

def check_offset_speed_up(_bitrate, _mdct_ret_d, _arg_dif_l, _db_l, _base_path, _encoder):
    _pool_size = multiprocessing.cpu_count()
    _pool = multiprocessing.Pool(processes=_pool_size)
    _inputs = []
    for _i in range(576):
        _inputs.append((_i, str(_bitrate) , _base_path, _encoder,))
    _pool_outputs = _pool.map(deal_with_wave_mf_wrap, _inputs)
    _pool.close()
    _pool.join()
    for _e in _pool_outputs:
        if not _e[0]:
            _arg_dif_l = _e[2]
        _mdct_ret_d[_e[0]] = _e[1]
    _min_num, _offset = [], []
    for _i in range(576):
        _len = len(_mdct_ret_d[_i])
        if not _i:
            for _j in range(_len):
                _min_num.append(_mdct_ret_d[_i][_j])
                _offset.append(0)
        else:
            for _j in range(_len):
                if _j < len(_min_num) and _mdct_ret_d[_i][_j] < _min_num[_j]:
                    _min_num[_j], _offset[_j] = _mdct_ret_d[_i][_j], _i
    _from_begin, _fix_num = 0, 0
    for _i in range(len(_offset)):
        if (_i < len(_arg_dif_l) and _arg_dif_l[_i] < 0.01) or (_i < len(_db_l) and _db_l[_i] >= 400):
            continue
        else:
            _from_begin, _fix_num = _i, _offset[_i]
            break
    if _from_begin != 0:
        for _i in range(_from_begin):
            _offset[_i] = _fix_num
    for _i in range(_from_begin + 1, len(_offset)):
        if (_i < len(_arg_dif_l) and _arg_dif_l[_i] < 0.01) or (_i < len(_db_l) and _db_l[_i] >= 400):
            _offset[_i] = _offset[_i - 1]
    return _offset

def check_offset_main(_file_path):
    # Encoder path
    _encoder = os.path.abspath(u'./Venusound/msic/lame_encode/lame_check_offset.exe')
    _mdct_ret_d = {}
    _arg_dif_l = []
    _db_l = []
    _abs_file_path = os.path.abspath(_file_path)
    _audio = eyed3.load(_abs_file_path)
    _audio_bitrate = _audio.info.bit_rate[1]
    _folder_name = _file_path.split('\\')[2].split('.')[0]
    _log_check_offset_info = log_check_offset.query.filter_by(file_path=_file_path).first()
    _temp_path = os.path.join(tempfile.gettempdir(), _folder_name)
    if not os.path.exists(_temp_path):
        os.makedirs(_temp_path)
    else:
        shutil.rmtree(_temp_path)
        os.makedirs(_temp_path)
    os.chdir(_temp_path)
    mp3_pre_handle(_abs_file_path, _db_l, _encoder)
    _base_path = _temp_path
    _offset = check_offset_speed_up(_audio_bitrate, _mdct_ret_d, _arg_dif_l, _db_l, _base_path, _encoder)
    _offset_len = len(_offset)
    _flag = 1
    for _i in range(_offset_len - 1):
        if _offset[_i] != _offset[_i + 1]:
            _flag = -1
            break
    _log_check_offset_info.flag = _flag
    _log_check_offset_info.offset_list = _offset
    db.session.add(_log_check_offset_info)
    db.session.commit()
    shutil.rmtree(u'./wave_sample')
