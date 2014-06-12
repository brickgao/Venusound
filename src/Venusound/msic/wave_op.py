# -*- coding: utf-8 -*-

import wave, array, math

def del_frames(_file_name, offset):
    _file_in = wave.open(_file_name, 'rb')
    _tmp = _file_in.getparams()
    _data = _file_in.readframes(_tmp[3])
    _data = _data[_tmp[1] * offset:]
    _params = (_tmp[0], _tmp[1], _tmp[2], _tmp[3] - offset, _tmp[4], _tmp[5])
    _file_out = wave.open(u'tmp_processed.wav', 'wb')
    _file_out.setparams(_params)
    _file_out.writeframes(_data)
    _file_out.close()
    _file_in.close()

def func_decibel_4(_input):
    if _input == 0:
        return 0
    else:
        return 20 * math.log(abs(_input) / 32768., 10)

def func_decibel_2(_input):
    if _input == 0:
        return 0
    else:
        return 20 * math.log(abs(_input) / 128., 10)

def get_decibel(_file_name):
    _file_in = wave.open(_file_name, 'rb')
    _tmp = _file_in.getparams()
    _data = _file_in.readframes(_tmp[3])
    if _tmp[1] == 2:
        _decibel = array.array('h')
    else:
        _decibel = array.array('i')
    _decibel.fromstring(_data)
    _decibel_len = len(_decibel)
    _ret = []
    for _i in range(_decibel_len / 576):
        _cnt = 0
        for _e in _decibel[_i * 576 : _i * 576 + 1152]:
            if _tmp[1] == 2:
                if func_decibel_2(_e) < 10.0:
                    _cnt += 1
            else:
                if func_decibel_4(_e) < 10.0:
                    _cnt += 1
        _ret.append(_cnt)
    return _ret
