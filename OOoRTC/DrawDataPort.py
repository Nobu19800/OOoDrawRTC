# -*- coding: utf-8 -*-

##
#
# @file DrawDataPort.py

import optparse
import sys,os,platform
import re


from os.path import expanduser
sv = sys.version_info


if os.name == 'posix':
    sys.path += ['/usr/lib/python2.' + str(sv[1]) + '/dist-packages', '/usr/lib/python2.' + str(sv[1]) + '/dist-packages/rtctree/rtmidl']
elif os.name == 'nt':
    sys.path += ['C:\\Python2' + str(sv[1]) + '\\lib\\site-packages', 'C:\\Python2' + str(sv[1]) + '\\Lib\\site-packages\\OpenRTM_aist\\RTM_IDL', 'C:\\Python2' + str(sv[1]) + '\\lib\\site-packages\\rtctree\\rtmidl']
    
    
    



import time
import random
import commands
import RTC
import OpenRTM_aist


from OpenRTM_aist import CorbaNaming
from OpenRTM_aist import RTObject
from OpenRTM_aist import CorbaConsumer
from omniORB import CORBA
import CosNaming
from rtctree.utils import build_attr_string, dict_to_nvlist, nvlist_to_dict
import threading




##
# @class DrawPortObject
# @brief 追加するポートのクラス
#

class DrawPortObject:
    ##
    # @brief コンストラクタ
    # @param self 
    # @param port データポート
    # @param data データ
    # @param name 名前
    # @param offset 位置、角度のオフセット[X,Y,R]
    # @param scale 位置の拡大率[X,Y]
    # @param pos 図形の初期位置、角度[X,Y,R]
    # @param obj 図形のオブジェクト
    # @param port_a 接続するデータポート
    # @param m_data_Type データ型
    #
    def __init__(self, port, data, name, offset, scale, pos, obj, port_a, m_dataType):
        self._port = port
        self._data = data
        self._name = name
        self._ox = offset[0]
        self._oy = offset[1]
        self._or = offset[2]
        self._sx = scale[0]
        self._sy = scale[1]
        self._x = pos[0]
        self._y = pos[1]
        self._r = pos[1]
        self._obj = obj
        self._port_a = port_a
        self._dataType = m_dataType


##
# @class DataType
# @brief データのタイプ
#

class DataType:

    basic = 0
    extended = 1

    DataTypeList = ["TimedDoubleSeq","TimedLongSeq","TimedFloatSeq","TimedShortSeq","TimedUDoubleSeq","TimedULongSeq",
                    "TimedUFloatSeq","TimedUShortSeq","TimedPoint2D","TimedVector2D","TimedPose2D","TimedGeometry2D"]
    def __init__(self):
        pass


def GetDataSType(data_type):
    basic = DataType.basic
    extended = DataType.extended

    if data_type == 'TimedDoubleSeq':
        dt = RTC.TimedDoubleSeq(RTC.Time(0,0),[])
        return dt, [float, basic]
    elif data_type == 'TimedLongSeq':
        dt = RTC.TimedLongSeq(RTC.Time(0,0),[])
        return dt, [long, basic]
    elif data_type == 'TimedFloatSeq':
        dt = RTC.TimedFloatSeq(RTC.Time(0,0),[])
        return dt, [float, basic]
    elif data_type == 'TimedShortSeq':
        dt = RTC.TimedShortSeq(RTC.Time(0,0),[])
        return dt, [int, basic]
    elif data_type == 'TimedUDoubleSeq':
        dt = RTC.TimedUDoubleSeq(RTC.Time(0,0),[])
        return dt, [float, basic]
    elif data_type == 'TimedULongSeq':
        dt = RTC.TimedULongSeq(RTC.Time(0,0),[])
        return dt, [long, basic]
    elif data_type == 'TimedUFloatSeq':
        dt = RTC.TimedUFloatSeq(RTC.Time(0,0),[])
        return dt, [float, basic]
    elif data_type == 'TimedUShortSeq':
        dt = RTC.TimedUShortSeq(RTC.Time(0,0),[])
        return dt, [int, basic]
    elif data_type == 'TimedPoint2D':
        dt = RTC.TimedPoint2D(RTC.Time(0,0),RTC.Point2D(0,0))
        return dt, [RTC.Point2D, extended, data_type]
    elif data_type == 'TimedVector2D':
        dt = RTC.TimedVector2D(RTC.Time(0,0),RTC.Vector2D(0,0))
        return dt, [RTC.Vector2D, extended, data_type]
    elif data_type == 'TimedPose2D':
        dt = RTC.TimedPose2D(RTC.Time(0,0),RTC.Pose2D(RTC.Point2D(0,0),0))
        return dt, [RTC.Pose2D, extended, data_type]
    elif data_type == 'TimedGeometry2D':
        dt = RTC.TimedGeometry2D(RTC.Time(0,0),RTC.Geometry2D(RTC.Pose2D(RTC.Point2D(0,0),0), RTC.Size2D(0,0)))
        return dt, [RTC.Geometry2D, extended, data_type]

    return None, None

##
# @brief データポートのデータ型を返す関数
# @param m_port データポート
# @return データオブジェクト、[データ型、データのタイプ、データ型の名前]
#

def GetDataType(m_port):
    basic = DataType.basic
    extended = DataType.extended
    
    profile = m_port.get_port_profile()
    props = nvlist_to_dict(profile.properties)
    data_type =  props['dataport.data_type']
    if data_type.startswith('IDL:'):
        data_type = data_type[4:]
    colon = data_type.rfind(':')
    if colon != -1:
        data_type = data_type[:colon]

    data_type = data_type.replace('RTC/','')
    
    
    
    return GetDataSType(data_type)





