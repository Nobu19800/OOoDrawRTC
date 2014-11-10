# -*- coding: utf-8 -*-

##
#
# @file OOoRTC.py

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




mgr = None
calc_comp = None
draw_comp = None
writer_comp = None
impress_comp = None
base_comp = None





##
# @brief 入力文字列をWriterのドキュメント上で文字化けしない文字コードで文字列を返す
# @param m_str 変換前の文字列
# @param m_code 変換前の文字コード
# @return 変換後の文字列
#
def SetCoding(m_str, m_code):
    if os.name == 'posix':
        if m_code == "utf-8":
            return m_str
        else:
            try:
                return m_str.decode(m_code).encode("utf-8")
            except:
                return ""
    elif os.name == 'nt':
        try:
            return m_str.decode(m_code).encode('cp932')
        except:
            return ""

##
# @brief 文字、背景色の色をRGB形式から変換して返すクラス
# @param red
# @param green
# @param blue
# @return 変換後の色の値
#

def RGB (red, green, blue):
    
    if red > 0xff:
      red = 0xff
    elif red < 0:
      red = 0
    if green > 0xff:
      green = 0xff
    elif green < 0:
      green = 0
    if blue > 0xff:
      blue = 0xff
    elif blue < 0:
      blue = 0
    return red * 0x010000 + green * 0x000100 + blue * 0x000001



##
# @brief ポートを接続する関数
# @param obj1 接続するデータポート
# @param obj2 接続するデータポート
# @param c_name コネクタ名
#

def ConnectPort(obj1, obj2, c_name):

    subs_type = "Flush"

    obj1.disconnect_all()
    
    obj2.disconnect_all()

    # connect ports
    conprof = RTC.ConnectorProfile(c_name, "", [obj1,obj2], [])
    OpenRTM_aist.CORBA_SeqUtil.push_back(conprof.properties,
                                    OpenRTM_aist.NVUtil.newNV("dataport.interface_type",
                                                         "corba_cdr"))

    OpenRTM_aist.CORBA_SeqUtil.push_back(conprof.properties,
                                    OpenRTM_aist.NVUtil.newNV("dataport.dataflow_type",
                                                         "push"))

    OpenRTM_aist.CORBA_SeqUtil.push_back(conprof.properties,
                                    OpenRTM_aist.NVUtil.newNV("dataport.subscription_type",
                                                         subs_type))

    ret = obj2.connect(conprof)



##
# @brief 各RTCのパスを取得する関数
# @param context ネーミングコンテキスト
# @param rtclist データポートのリスト
# @param name 現在のパス名
# @param oParent ツリーの現在のオブジェクト
# @param oTreeDataModel ツリーオブジェクト
#
def ListRecursive(context, rtclist, name, oParent, oTreeDataModel):
    
    m_blLength = 100
    
    bl = context.list(m_blLength)
    

    cont = True
    while cont:
        for i in bl[0]:
            if i.binding_type == CosNaming.ncontext:
                
                next_context = context.resolve(i.binding_name)
                name_buff = name[:]
                name.append(i.binding_name[0].id)

                if oTreeDataModel == None:
                    oChild = None
                else:
                    oChild = oTreeDataModel.createNode(i.binding_name[0].id,False)
                    oParent.appendChild(oChild)
                
                
                
                ListRecursive(next_context,rtclist,name, oChild, oTreeDataModel)
                

                name = name_buff
            elif i.binding_type == CosNaming.nobject:
                if oTreeDataModel == None:
                    oChild = None
                else:
                    oChild = oTreeDataModel.createNode(i.binding_name[0].id,False)
                    oParent.appendChild(oChild)
                
                if len(rtclist) > m_blLength:
                    break
                if i.binding_name[0].kind == 'rtc':
                    name_buff = name[:]
                    name_buff.append(i.binding_name[0].id)
                    
                    tkm = OpenRTM_aist.CorbaConsumer()
                    tkm.setObject(context.resolve(i.binding_name))
                    inobj = tkm.getObject()._narrow(RTC.RTObject)

                    try:
                        pin = inobj.get_ports()
                        for p in pin:
                            name_buff2 = name_buff[:]
                            profile = p.get_port_profile()
                            props = nvlist_to_dict(profile.properties)
                            tp_n = profile.name.split('.')[1]
                            name_buff2.append(tp_n)
                            if oTreeDataModel == None:
                                pass
                            else:
                                oChild_port = oTreeDataModel.createNode(tp_n,False)
                                oChild.appendChild(oChild_port)

                            rtclist.append([name_buff2,p])
                    except:
                        pass
                        
            else:
                pass
        if CORBA.is_nil(bl[1]):
            cont = False
        else:
            bl = i.next_n(m_blLength)




##
# @brief
# @param naming ネーミングコンテキスト
# @param rtclist データポートのリスト
# @param name 現在のパス名
# @param oParent ツリーの現在のオブジェクト
# @param oTreeDataModel ツリーオブジェクト
def rtc_get_rtclist(naming, rtclist, name, oParent, oTreeDataModel):
    name_cxt = naming.getRootContext()
    ListRecursive(name_cxt,rtclist,name, oParent, oTreeDataModel)
    
    return 0


##
# @brief ネーミングサービスへ接続する関数
# @param s_name ネームサーバーの名前
# @param orb ORBオブジェクト
# @return ネーミングコンテキスト
def SetNamingServer(s_name, orb, MyMsgBox = None):
    
    try:
        namingserver = CorbaNaming(orb, s_name)
    except:
        if MyMsgBox != None:
            MyMsgBox(SetCoding('エラー','utf-8'),SetCoding('ネーミングサービスへの接続に失敗しました','utf-8'))
        return None
    return namingserver

##
# @brief ツリーで選択したアイテムがポートかどうか判定する関数
# @param objectTree ダイアログのツリー
# @param _path ポートのパスのリスト
# @return [データポートまでのPath、選択中のツリーノード]

def JudgePort(objectTree, _paths):
    m_list = []
        
    node = objectTree.getSelection()
    if node:
        parent = node.getParent()
        if parent:
            m_list.insert(0, node.getDisplayValue())
        else:
            return None
        if node.getChildCount() != 0:
            return None
    else:
        return None
            
    while(True):
        if node:
            node = node.getParent()
            if node:
                m_list.insert(0, node.getDisplayValue())
            else:
                break
        

    flag = False
    for t_comp in _paths:
        if t_comp[0] == m_list:
            return t_comp, node
            
            flag = True
            
                
    if flag == False:
        return None

##
# @brief ポートのパスのリストを取得する関数
# @param name ネームサーバーの名前
# @return ポートのパスのリスト
#
def GetPathList(name, m_mgr, MyMsgBox = None):
    if m_mgr != None:
        orb = m_mgr._orb
        namingserver = SetNamingServer(str(name), orb, MyMsgBox)
        if namingserver:
            _path = ['/', name]
            _paths = []
            rtc_get_rtclist(namingserver, _paths, _path, None, None)
            return _paths
    return None
