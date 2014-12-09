# -*- coding: utf-8 -*-



##
#   @file OOoDrawRTC.py
#   @brief OOoDrawControl Component

import optparse
import sys,os,platform
import re
import time
import random
import commands
import math

from os.path import expanduser
sv = sys.version_info

if os.name == 'posix':
    home = expanduser("~")
    sys.path += [home+'/OOoRTC', '/usr/lib/python2.' + str(sv[1]) + '/dist-packages', '/usr/lib/python2.' + str(sv[1]) + '/dist-packages/rtctree/rtmidl']
elif os.name == 'nt':
    sys.path += ['.\\OOoRTC', 'C:\\Python2' + str(sv[1]) + '\\lib\\site-packages', 'C:\\Python2' + str(sv[1]) + '\\Lib\\site-packages\\OpenRTM_aist\\RTM_IDL', 'C:\\Python2' + str(sv[1]) + '\\lib\\site-packages\\rtctree\\rtmidl']



import RTC
import OpenRTM_aist

from OpenRTM_aist import CorbaNaming
from OpenRTM_aist import RTObject
from OpenRTM_aist import CorbaConsumer
from omniORB import CORBA
import CosNaming
from rtctree.utils import build_attr_string, dict_to_nvlist, nvlist_to_dict




import uno
import unohelper
from com.sun.star.awt import XActionListener

from com.sun.star.script.provider import XScriptContext
from com.sun.star.view import XSelectionChangeListener

from com.sun.star.awt import Point
from com.sun.star.awt import Size

import OOoRTC
import DrawDataPort





#comp_num = random.randint(1,3000)
imp_id = "OOoDrawControl"# + str(comp_num)




##
# @class ControlName
# @brief ウィジェット名
#
class ControlName:
    XoffsetBName = "Xoffset"
    YoffsetBName = "Yoffset"
    RoffsetBName = "Roffset"
    XscaleBName = "Xscale"
    YscaleBName = "Yscale"
    NameServerFName = "nameserver"
    CreateBName = "CreateButton"
    DeleteBName = "DeleteButton"
    SetPosBName = "SetPosButton"
    TextFName = "TextField6"
    RTCTreeName = "RTCTreeControl"
    CreateTreeBName = "CreateRTCTreeButton"
    SetAllPosBName = "SetAllPosButton"
    DataTypeCBName = "DataTypeComboBox"
    PortTypeCBName = "PortTypeComboBox"
    def __init__(self):
        pass




ooodrawcontrol_spec = ["implementation_id", imp_id,
                  "type_name",         imp_id,
                  "description",       "Openoffice Draw Component",
                  "version",           "0.0.2",
                  "vendor",            "Miyamoto Nobuhiko",
                  "category",          "example",
                  "activity_type",     "DataFlowComponent",
                  "max_instance",      "10",
                  "language",          "Python",
                  "lang_type",         "script",
                  ""]





##
# @class OOoDrawControl
# @brief OpenOffice Drawを操作するためのRTCのクラス
#

class OOoDrawControl(OpenRTM_aist.DataFlowComponentBase):
    ##
    # @brief コンストラクタ
    # @param self 
    # @param manager マネージャーオブジェクト
    #
  def __init__(self, manager):
    OpenRTM_aist.DataFlowComponentBase.__init__(self, manager)
    
    self.InPorts = {}
    self.OutPorts = {}

    self.sleepTime = 0

    

    try:
      self.draw = OOoDraw()
    except NotOOoDrawException:
      return
    
    return

  ##
  # @brief 実行周期を設定する関数
  # @param self 
  # @param rate：実行周期
  #
  def mSetRate(self, rate):
      m_ec = self.get_owned_contexts()
      m_ec[0].set_rate(rate)

  ##
  # @brief 活性化するための関数
  # @param self 
  #
  def mActivate(self):
      m_ec = self.get_owned_contexts()
      m_ec[0].activate_component(self._objref)

  ##
  # @brief 不活性化するための関数
  # @param self 
  #
  def mDeactivate(self):
      m_ec = self.get_owned_contexts()
      m_ec[0].deactivate_component(self._objref)

  

  ##
  # @brief インポート追加の関数
  # @param self 
  # @param name インポートの名前
  # @param m_outport 接続するアウトポート
  # @param offset 位置、角度のオフセット[X,Y,R]
  # @param scale 位置の拡大率[X,Y]
  # @param pos 図形の初期位置、角度[X,Y,R]
  # @param obj 図形のオブジェクト
  #
  def mAddInPort(self, name, m_outport, offset, scale, pos, obj, autoCon = True):

      m_data_i = None
      m_data_type = None
    
      if autoCon:
        m_data_i, m_data_type =  DrawDataPort.GetDataType(m_outport[1])
      else:
        m_data_i, m_data_type =  DrawDataPort.GetDataSType(m_outport[1])

      
      
      if m_data_i:
        m_inport = OpenRTM_aist.InPort(name, m_data_i)
        self.addInPort(name, m_inport)
        if autoCon:
            OOoRTC.ConnectPort(m_inport._objref, m_outport[1], name)
        self.InPorts[name] = DrawDataPort.DrawPortObject(m_inport, m_data_i, name, offset, scale, pos, obj, m_outport, m_data_type)


  ##
  # @brief アウトポート追加の関数
  # @param self 
  # @param name インポートの名前
  # @param m_outport 接続するアウトポート
  # @param offset 位置、角度のオフセット[X,Y,R]
  # @param scale 位置の拡大率[X,Y]
  # @param pos 図形の初期位置、角度[X,Y,R]
  # @param obj 図形のオブジェクト
  #
  def mAddOutPort(self, name, m_inport, offset, scale, pos, obj, autoCon = True):
      
      m_data_o = None
      m_data_type = None
    
      if autoCon:
        m_data_o, m_data_type =  DrawDataPort.GetDataType(m_inport[1])
      else:
        m_data_o, m_data_type =  DrawDataPort.GetDataSType(m_inport[1])
        
      
      if m_data_o:
        m_outport = OpenRTM_aist.OutPort(name, m_data_o)
        self.addOutPort(name, m_outport)
        if autoCon:
            OOoRTC.ConnectPort(m_outport._objref, m_inport[1], name)
        self.OutPorts[name] = DrawDataPort.DrawPortObject(m_outport, m_data_o, name, offset, scale, pos, obj, m_inport, m_data_type)

  ##
  # @brief データポート全削除の関数
  # @param self 
  #
  def mRemoveAllPort(self):
      for n,op in self.OutPorts.items():
          op._port.disconnect_all()
          self.removePort(op._port)
      self.OutPorts = {}

      for n,ip in self.InPorts.items():
          ip._port.disconnect_all()
          self.removePort(ip._port)
      self.InPorts = {}

  ##
  # @brief インポート削除の関数
  # @param self 
  # @param inport 削除するインポート
  #

  def mRemoveInPort(self, inport):
      inport._port.disconnect_all()
      self.removePort(inport._port)
      del self.InPorts[inport._name]


  ##
  # @brief アウトポート削除の関数
  # @param self 
  # @param outport 削除するアウトポート
  #

  def mRemoveOutPort(self, outport):
      outport._port.disconnect_all()
      self.removePort(outport._port)
      del self.OutPorts[outport._name]


  ##
  # @brief 初期化処理用コールバック関数
  # @param self 
  # @return RTC::ReturnCode_t
  def onInitialize(self):
    
    OOoRTC.draw_comp = self
    
    
    return RTC.RTC_OK

  ##
  # @brief 活性化処理用コールバック関数
  # @param self 
  # @param ec_id target ExecutionContext Id
  # @return RTC::ReturnCode_t
  def onActivated(self, ec_id):
      m_ec = self.get_owned_contexts()
      
 
      rate = m_ec[0].get_rate()
      if 3 < rate:
          self.sleepTime = 1./3. - 1./rate

      return RTC.RTC_OK

  ##
  # @brief 周期処理用コールバック関数
  # @param self 
  # @param ec_id target ExecutionContext Id
  # @return RTC::ReturnCode_t
  
  def onExecute(self, ec_id):
    
    basic = DrawDataPort.DataType.basic
    extended = DrawDataPort.DataType.extended


    for n,op in self.OutPorts.items():
      if JudgeRTCObjDraw(op._obj):
        pass
      else:
        self.mRemoveOutPort(op)
        UpdateSaveSheet()

    for n,ip in self.InPorts.items():
      if JudgeRTCObjDraw(ip._obj):
        pass
      else:
        self.mRemoveInPort(ip)
        UpdateSaveSheet()


    




    for n,op in self.OutPorts.items():
        px, py = ObjGetPos(op)
        rot = float(op._obj.RotateAngle + op._or)/100.*3.14159/180.
        
        if op._dataType[1] == basic:
            op._data.data = [op._dataType[0](px), op._dataType[0](py), op._dataType[0](rot)]
                
            
            
            
        elif op._dataType[1] == extended:
            if op._dataType[2] == 'TimedPoint2D':
                op._data.x = px
                op._data.y = py
            elif op._dataType[2] == 'TimedVector2D':
                op._data.x = px
                op._data.y = py
            elif op._dataType[2] == 'TimedPose2D':
                op._data.position.x = px
                op._data.position.y = py
                op._data.heading = rot
            elif op._dataType[2] == 'TimedGeometry2D':
                op._data.pose.position.x = px
                op._data.pose.position.y = py
                op._data.pose.heading = rot
                
              
        OpenRTM_aist.setTimestamp(op._data)
        op._port.write()

    
    
    for n,ip in self.InPorts.items():
        dt = None
        while ip._port.isNew():
            dt = ip._port.read()
            
        if dt != None:
          if ip._dataType[1] == basic:
            if len(dt.data) < 2:
              pass
            else:
              
              if len(dt.data) > 2:
                ip._obj.RotateAngle = long((dt.data[2] + ip._or)*100. * 180/3.141592)
              ObjSetPos(ip, dt.data[0], dt.data[1])
              
                
          elif ip._dataType[1] == extended:
            if ip._dataType[2] == 'TimedPoint2D':
              ObjSetPos(ip, dt.data.x, dt.data.y)
            elif ip._dataType[2] == 'TimedVector2D':
              ObjSetPos(ip, dt.data.x, dt.data.y)
            elif ip._dataType[2] == 'TimedPose2D':
              ip._obj.RotateAngle = long((dt.data.heading + ip._or)*100. * 180/3.141592)
              ObjSetPos(ip, dt.data.position.x, dt.data.position.y)
            elif ip._dataType[2] == 'TimedGeometry2D':
              ip._obj.RotateAngle = long((dt.data.pose.heading + ip._or)*100. * 180/3.141592)
              ObjSetPos(ip, dt.data.pose.position.x, dt.data.pose.position.y)
            
              


    time.sleep(self.sleepTime)
    
    return RTC.RTC_OK

  ##
  # @brief 終了処理用コールバック関数
  # @param self 
  # @param ec_id target ExecutionContext Id
  # @return RTC::ReturnCode_t
  
  def on_shutdown(self, ec_id):
      OOoRTC.draw_comp = None
      return RTC.RTC_OK




##
# @brief コンポーネントを活性化してDrawの操作を開始する関数
#

def Start():
    
    if OOoRTC.draw_comp:
        OOoRTC.draw_comp.mActivate()

##
# @brief コンポーネントを不活性化してDrawの操作を終了する関数
#

def Stop():
    
    if OOoRTC.draw_comp:
        OOoRTC.draw_comp.mDeactivate()


##
# @brief コンポーネントの実行周期を設定する関数
#

def Set_Rate():
    
    if OOoRTC.draw_comp:
      try:
        draw = OOoDraw()
      except NotOOoDrawException:
          return

      oDrawPages = draw.drawpages
      for i in range(0, oDrawPages.Count):
        oDrawPage = oDrawPages.getByIndex(i)
        forms = oDrawPage.getForms()
        for j in range(0, forms.Count):
          st_control = oDrawPage.getForms().getByIndex(j).getByName('Rate')
          if st_control:
            try:
              text = float(st_control.Text)
            except:
               return
              
            OOoRTC.draw_comp.mSetRate(text)
      
      

      
        
        
      
##
# @brief 図形の位置を取得
# @param port 追加したデータポート
# @return 図形の位置(X,Y)
#
def ObjGetPos(_port):
  size = _port._obj.Size

  t_pos = _port._obj.getPosition()
          
  t_rot = math.atan2(size.Height, size.Width)

  rot = -(_port._obj.RotateAngle / 100.) * 3.141592/180. + t_rot
  leng = math.sqrt(size.Width*size.Width + size.Height*size.Height)

  tx = t_pos.X/_port._sx*100./10. + _port._ox + leng*math.cos(rot)/2.

  ty = t_pos.Y/_port._sy*100./10. + _port._oy + leng*math.sin(rot)/2.

  return tx, ty

##
# @brief 図形の位置を設定
# @param _port 追加したデータポート
# @param _x 設定する位置(X)
# @param _y 設定する位置(Y)
#
def ObjSetPos(_port, _x, _y):
  size = _port._obj.Size
              
  t_pos = Point()
  t_rot = math.atan2(size.Height, size.Width)
    
  rot = -(_port._obj.RotateAngle / 100.) * 3.141592/180. + t_rot
  leng = math.sqrt(size.Width*size.Width + size.Height*size.Height)
  t_pos.X = long(_x*_port._sx/100.*10. - leng*math.cos(rot)/2.) + _port._ox
  t_pos.Y = long(_y*_port._sy/100.*10. - leng*math.sin(rot)/2.) + _port._oy
                
  _port._obj.setPosition(t_pos)



##
# @brief 設定した図形がどのページに存在するか取得する関数
# @param obj 図形オブジェクト
# @return 図形のページ番号、図形番号
#
def JudgeRTCObjDraw(obj):
  
  try:
    draw = OOoDraw()
  except NotOOoDrawException:
    return
  oDrawPages = draw.drawpages
  for i in range(0, oDrawPages.Count):
    oDrawPage = oDrawPages.getByIndex(i)
    for j in range(0, oDrawPage.Count):
      if oDrawPage.getByIndex(j) == obj:
        return i,j
  return None
      
  



##
# @brief RTCをマネージャに登録する関数
# @param manager マネージャーオブジェクト
#
def OOoDrawControlInit(manager):
  profile = OpenRTM_aist.Properties(defaults_str=ooodrawcontrol_spec)
  manager.registerFactory(profile,
                          OOoDrawControl,
                          OpenRTM_aist.Delete)

##
# @brief 
# @param manager マネージャーオブジェクト
#
def MyModuleInit(manager):
  manager._factory.unregisterObject(imp_id)
  OOoDrawControlInit(manager)

  
  comp = manager.createComponent(imp_id)






##
# @brief オブジェクトがポートと関連付けされているかの判定の関数
# @param obj 図形オブジェクト
# @return データポートとデータポートのタイプ
#
def JudgeDrawObjRTC(obj):
  
  if OOoRTC.draw_comp:
    for n,i in OOoRTC.draw_comp.InPorts.items():
      if i._obj == obj:
        return i, "DataInPort"
    for n,o in OOoRTC.draw_comp.OutPorts.items():
      if o._obj == obj:
        return o, "DataOutPort"
  return None, None



            




##
# @brief データポートを追加する関数
# @param o_port 接続するデータポート
# @param dlg_control ダイアログオブジェクト
# @param obj 図形オブジェクト
# @param d_type データポートのタイプ
# @return 成功ならばTrue、失敗ならばFalse
#

def CompAddPort(name, o_port, dlg_control, obj, d_type, autoCon = True):
    
    if OOoRTC.draw_comp == None:
        return False
    else:      
        
          xo_control = dlg_control.getControl( ControlName.XoffsetBName )
          xo = long(xo_control.Text)

          yo_control = dlg_control.getControl( ControlName.YoffsetBName )
          yo = long(yo_control.Text)

          ro_control = dlg_control.getControl( ControlName.RoffsetBName )
          ro = float(ro_control.Text)

          xs_control = dlg_control.getControl( ControlName.XscaleBName )
          xs = long(xs_control.Text)

          ys_control = dlg_control.getControl( ControlName.YscaleBName )
          ys = long(ys_control.Text)

          pos = obj.getPosition()
          
          rot = obj.RotateAngle

          

          if d_type == 'DataInPort':
              
              OOoRTC.draw_comp.mAddOutPort(name, o_port, [xo,yo,ro], [xs,ys], [pos.X, pos.Y, rot], obj, autoCon)
          elif d_type== 'DataOutPort':
              OOoRTC.draw_comp.mAddInPort(name, o_port, [xo,yo,ro], [xs,ys], [pos.X, pos.Y, rot], obj, autoCon)

          
    return True

##
# @brief RTC起動の関数
#

def createOOoDrawComp():
    if OOoRTC.draw_comp:
        MyMsgBox('',OOoRTC.SetCoding('RTCは起動済みです','utf-8'))
        return                
    
    if OOoRTC.mgr == None:
        if os.name == 'posix':
            home = expanduser("~")
            OOoRTC.mgr = OpenRTM_aist.Manager.init([os.path.abspath(__file__), '-f', home+'/OOoRTC/rtc.conf'])
        elif os.name == 'nt':
            OOoRTC.mgr = OpenRTM_aist.Manager.init([os.path.abspath(__file__), '-f', '.\\rtc.conf'])
        else:
            return

      
        OOoRTC.mgr.setModuleInitProc(MyModuleInit)
        OOoRTC.mgr.activateManager()
        OOoRTC.mgr.runManager(True)
    else:
        MyModuleInit(OOoRTC.mgr)
      
          

    try:
      draw = OOoDraw()
    except NotOOoDrawException:
      return

    
    MyMsgBox('',OOoRTC.SetCoding('RTCを起動しました','utf-8'))

    LoadSheet()
    
    
    return




##
# @brief メッセージボックス表示の関数
# @param title ウインドウのタイトル
# @param message 表示する文章
# http://d.hatena.ne.jp/kakurasan/20100408/p1のソースコード(GPLv2)の一部
#

def MyMsgBox(title, message):
    try:
        m_bridge = Bridge()
    except:
        return
    m_bridge.run_infodialog(title, message)


##
# @brief OpenOfficeを操作するためのクラス
# http://d.hatena.ne.jp/kakurasan/20100408/p1のソースコード(GPLv2)の一部
#

class Bridge(object):
  def __init__(self):
    self._desktop = XSCRIPTCONTEXT.getDesktop()
    self._document = XSCRIPTCONTEXT.getDocument()
    self._frame = self._desktop.CurrentFrame
    self._window = self._frame.ContainerWindow
    self._toolkit = self._window.Toolkit
  def run_infodialog(self, title='', message=''):
    try:
        msgbox = self._toolkit.createMessageBox(self._window,uno.createUnoStruct('com.sun.star.awt.Rectangle'),'infobox',1,title,message)
        msgbox.execute()
        msgbox.dispose()
    except:
        msgbox = self._toolkit.createMessageBox(self._window,'infobox',1,title,message)
        msgbox.execute()
        msgbox.dispose()






##
# @brief ダイアログのツリーにネーミングサーバーのオブジェクトを登録する関数
# @param oTreeModel ツリーオブジェクト
# @param smgr UNOコンポーネントコンテキスト
# @param ctx UNOサービスマネージャー
# @param dlg_control ダイアログオブジェクト

def SetRTCTree(oTreeModel, smgr, ctx, dlg_control):
    oTree = dlg_control.getControl( ControlName.RTCTreeName )
    tfns_control = dlg_control.getControl( ControlName.NameServerFName )
    if OOoRTC.mgr != None:
        

               
        orb = OOoRTC.mgr._orb

        
       
        namingserver = OOoRTC.SetNamingServer(str(tfns_control.Text), orb, MyMsgBox)
        
        
        
        if namingserver:
            
            
            oTreeDataModel = smgr.createInstanceWithContext("com.sun.star.awt.tree.MutableTreeDataModel", ctx)
            root = oTreeDataModel.createNode("/", False)
            oTreeDataModel.setRoot(root)
            oChild = oTreeDataModel.createNode(str(tfns_control.Text),False)
            root.appendChild(oChild)

            
            
            _path = ['/', str(tfns_control.Text)]
            _paths = []
            OOoRTC.rtc_get_rtclist(namingserver, _paths, _path, oChild, oTreeDataModel)

            
                      
            
            oTreeModel.DataModel = oTreeDataModel
            
            
            oTree.addSelectionChangeListener(TreeSelectListener(dlg_control, _paths))


            create_listener = CreatePortListener( dlg_control, _paths)
            create_control = dlg_control.getControl(ControlName.CreateBName)
            create_control.addActionListener(create_listener)

            delete_listener = DeleteListener(dlg_control, _paths)
            delete_control = dlg_control.getControl(ControlName.DeleteBName)
            delete_control.addActionListener(delete_listener)

            setPos_listener = SetPosListener(dlg_control, _paths)
            setpos_control = dlg_control.getControl(ControlName.SetPosBName)
            setpos_control.addActionListener(setPos_listener)


##
# @brief OpenOffice Drawを操作するためのクラス
# http://d.hatena.ne.jp/kakurasan/20100408/p1のソースコード(GPLv2)の一部を改変
#

class OOoDraw(Bridge):
  def __init__(self):
    Bridge.__init__(self)
    if not self._document.supportsService('com.sun.star.drawing.DrawingDocument'):
      self.run_errordialog(title='エラー', message='このマクロはOpenOffice.org Drawの中で実行してください')
      raise NotOOoDrawException()
    self.__current_controller = self._document.CurrentController
    self.__drawpages = self._document.DrawPages
  @property
  def drawpages(self): return self.__drawpages
  @property
  def document(self): return self._document
  

def LoadParam(m_list, oDrawPages):
    m_i = long(m_list[1])
    m_j = long(m_list[2])
    _ox = long(m_list[3])
    _oy = long(m_list[4])
    _or = float(m_list[5])
    _sx = long(m_list[6])
    _sy = long(m_list[7])
    _x = long(m_list[8])
    _y = long(m_list[9])
    _r = long(m_list[10])

    flag = True
    if m_i > oDrawPages.Count:
                
        flag = False
        
    m_oDrawPage = oDrawPages.getByIndex(m_i)
    if m_j > m_oDrawPage.Count:
                
        flag = False
    _obj = m_oDrawPage.getByIndex(m_j)

    return m_i,m_j,_ox,_oy,_or,_sx,_sy,_x,_y,_r,_obj,flag

##
# @brief 読み込んだ保存用シートからポートを作成する関数
#

def LoadSheet():
  
    
    if OOoRTC.draw_comp:
      
      draw = OOoRTC.draw_comp.draw
      
      OOoRTC.draw_comp.mRemoveAllPort()
      oDrawPages = draw.drawpages
      oDrawPage = oDrawPages.getByIndex(0)
      
      st_control = oDrawPage.getForms().getByIndex(0).getByName('SaveTextBox')
      text = str(st_control.Text)
      m_port = re.split(';',text)

      m_hostname = ''
      _path = []
      
      for mp in m_port:
        m_list = re.split('#',mp)
        if len(m_list) > 10:
          m_name = re.split(':',m_list[0])
          if len(m_name) < 2:
            return
          if len(m_name) == 2:
              for dn in DrawDataPort.DataType.DataTypeList:
                  if m_name[1] == dn:
                      m_name[1] = dn
                  m_i,m_j,_ox,_oy,_or,_sx,_sy,_x,_y,_r,_obj,flag = LoadParam(m_list, oDrawPages)
                  F_Name = m_name[1] + str(m_i) + str(m_j)

                  if m_name[0] == "DataOutPort":
                    OOoRTC.draw_comp.mAddOutPort(F_Name, [[m_name[0],m_name[1]],m_name[1]], [_ox,_oy,_or], [_sx,_sy], [_x, _y, _r], _obj, False)
                  if m_name[0] == 'DataOutPort':
                    OOoRTC.draw_comp.mAddInPort(F_Name, [[m_name[0],m_name[1]],m_name[1]], [_ox,_oy,_or], [_sx,_sy], [_x, _y, _r], _obj, False)
              
          else:
              if m_hostname == m_name[1]:
                pass
              else:
                _paths = OOoRTC.GetPathList(m_name[1], OOoRTC.mgr ,MyMsgBox)
                m_hostname = m_name[1]
              if _paths == None:
                return
              for p in _paths:
                if p[0] == m_name:
                  
                  
                  profile = p[1].get_port_profile()
                  props = nvlist_to_dict(profile.properties)

                  m_i,m_j,_ox,_oy,_or,_sx,_sy,_x,_y,_r,_obj,flag = LoadParam(m_list, oDrawPages)

                  F_Name = p[0][-2] + p[0][-1] + str(m_i) + str(m_j)

                  
                  
                  
                  
                  
                  if flag:
                    if props['port.port_type'] == 'DataInPort':
                        OOoRTC.draw_comp.mAddOutPort(F_Name, p, [_ox,_oy,_or], [_sx,_sy], [_x, _y, _r], _obj)
                    if props['port.port_type'] == 'DataOutPort':
                        OOoRTC.draw_comp.mAddInPort(F_Name, p, [_ox,_oy,_or], [_sx,_sy], [_x, _y, _r], _obj)


##
# @brief 作成したポートの設定を保存する関数
#

def UpdateSaveSheet():
    try:
      draw = OOoDraw()
    except NotOOoDrawException:
        return

    oDrawPage = draw.drawpages.getByIndex(0)
    
    st_control = oDrawPage.getForms().getByIndex(0).getByName('SaveTextBox')
    
    text = ''

    PortList = []
    for n,i in OOoRTC.draw_comp.InPorts.items(): 
        PortList.append(i)
    for n,o in OOoRTC.draw_comp.OutPorts.items(): 
        PortList.append(o)
        
    for p in PortList:
      m_i,m_j = JudgeRTCObjDraw(p._obj)
      
      if m_i != None:
        
        for j in range(0, len(p._port_a[0])):
          if j == 0:
            text = text + ';' + p._port_a[0][j]
          else:
            text = text + ':' + p._port_a[0][j]
        
        text = text + '#' + str(m_i)
        text = text + '#' + str(m_j)
        text = text + '#' + str(p._ox)
        text = text + '#' + str(p._oy)
        text = text + '#' + str(p._or)
        text = text + '#' + str(p._sx)
        text = text + '#' + str(p._sy)
        text = text + '#' + str(p._x)
        text = text + '#' + str(p._y)
        text = text + '#' + str(p._r)
        

    
    st_control.Text = text

##
# @brief ツリーの選択位置が変わったときに各テキストボックスの内容を変更する関数
# @param dlg_control ダイアログオブジェクト
# @param m_port データポートオブジェクト
#
def UpdateTree(dlg_control, m_port):
    
    info_control = dlg_control.getControl( ControlName.TextFName )
    info_control.setText(OOoRTC.SetCoding('作成済み','utf-8'))

    dtcb_control = dlg_control.getControl( ControlName.DataTypeCBName )
    if len(m_port._port_a[0]) == 2:
        dtcb_control.setText(m_port._port_a[1])
    else:
        dtcb_control.setText("")
    
    xo_control = dlg_control.getControl( ControlName.XoffsetBName )
    xo_control.setText(str(m_port._ox))

    yo_control = dlg_control.getControl( ControlName.YoffsetBName )
    yo_control.setText(str(m_port._oy))

    ro_control = dlg_control.getControl( ControlName.RoffsetBName )
    ro_control.setText(str(m_port._or))

    xs_control = dlg_control.getControl( ControlName.XscaleBName )
    xs_control.setText(str(m_port._sx))

    ys_control = dlg_control.getControl( ControlName.YscaleBName )
    ys_control.setText(str(m_port._sy))

##
# @brief ポートを削除したときに各テキストボックスを変更する関数
# @param dlg_control ダイアログオブジェクト

def ClearInfo(dlg_control):
    info_control = dlg_control.getControl( ControlName.TextFName )
    info_control.setText(OOoRTC.SetCoding('未作成','utf-8'))

##
# @class CreatePortListener
# @brief ポート作成ボタンのコールバック
#

class CreatePortListener( unohelper.Base, XActionListener):
    ##
    # @brief コンストラクタ
    # @param self 
    # @param dlg_control ダイアログオブジェクト
    # @param _paths データポートのパス
    def __init__(self, dlg_control, _paths):
        
        self._paths = _paths
        self.dlg_control = dlg_control

    ##
    # @brief 
    # @param self 
    # @param actionEvent 
    def actionPerformed(self, actionEvent):

        

        try:
            draw = OOoDraw()
        except NotOOoDrawException:
            return

        sobj = draw.document.CurrentSelection

        if sobj:
            if sobj.Count > 0:
                obj = sobj.getByIndex(0)
                
                jport, d_type = JudgeDrawObjRTC(obj)
                
                if jport:
                    xo_control = self.dlg_control.getControl( ControlName.XoffsetBName )
                    yo_control = self.dlg_control.getControl( ControlName.YoffsetBName )
                    ro_control = self.dlg_control.getControl( ControlName.RoffsetBName )
                    xs_control = self.dlg_control.getControl( ControlName.XscaleBName )
                    ys_control = self.dlg_control.getControl( ControlName.YscaleBName )
                    jport._ox = long(xo_control.Text)
                    jport._oy = long(yo_control.Text)
                    jport._or = float(ro_control.Text)
                    jport._sx = long(xs_control.Text)
                    jport._sy = long(ys_control.Text)
                    UpdateSaveSheet()

                    return

                dtcb_control = self.dlg_control.getControl( ControlName.DataTypeCBName )
                dt = str(dtcb_control.Text)
                if dt != "":
                    F_Name = dt + str(OpenRTM_aist.uuid1())
                    ptcb_control = self.dlg_control.getControl( ControlName.PortTypeCBName )
                    pt = str(ptcb_control.Text)
                    

                    for d in DrawDataPort.DataType.DataTypeList:
                        if dt == d:
                            dt = d
                    
                    if pt == "DataOutPort":
                        pt = "DataInPort"
                    else:
                        pt = "DataOutPort"
                    CompAddPort(F_Name, [[pt,dt],dt], self.dlg_control, obj, pt, False)
                    if pt == "DataInPort":
                        MyMsgBox('',OOoRTC.SetCoding(dt+"型のOutPortを作成しました。",'utf-8'))
                    else:
                        MyMsgBox('',OOoRTC.SetCoding(dt+"型のInPortを作成しました。",'utf-8'))
                    UpdateSaveSheet()

                    info_control = self.dlg_control.getControl( ControlName.TextFName )
                    info_control.setText(OOoRTC.SetCoding('作成済み','utf-8'))

                    return
                    
                    
                objectTree = self.dlg_control.getControl(ControlName.RTCTreeName)
                t_comp, nd = OOoRTC.JudgePort(objectTree, self._paths)
                
                
                if t_comp:
                    
                    m_i,m_j = JudgeRTCObjDraw(obj)
                    
                    F_Name = t_comp[0][-2] + t_comp[0][-1] + str(m_i) + str(m_j)
                    
                    
                    profile = t_comp[1].get_port_profile()
                    props = nvlist_to_dict(profile.properties)

                    
                    CompAddPort(F_Name, t_comp, self.dlg_control, obj, props['port.port_type'])
                    
                        
                    t_str = str(m_i) + "ページの" +  str(m_j) + "番目の図形と" + t_comp[0][-2] + t_comp[0][-1] + "を関連付けました"
                    MyMsgBox('',OOoRTC.SetCoding(t_str,'utf-8'))
                        
                        

                    

                    UpdateSaveSheet()

                    info_control = self.dlg_control.getControl( ControlName.TextFName )
                    info_control.setText(OOoRTC.SetCoding('作成済み','utf-8'))
        

##
# @class SetRTCTreeListener
# @brief ツリー作成ボタンのコールバック
#

class SetRTCTreeListener( unohelper.Base, XActionListener ):
    ##
    # @brief コンストラクタ
    # @param self 
    # @param oTreeModel ツリーオブジェクト
    # @param smgr UNOコンポーネントコンテキスト
    # @param ctx UNOサービスマネージャー
    # @param dlg_control ダイアログオブジェクト
    def __init__(self, oTreeModel, smgr, ctx, dlg_control):
        
        self.oTreeModel = oTreeModel
        self.smgr = smgr
        self.ctx = ctx
        self.dlg_control = dlg_control

    ##
    # @brief 
    # @param self 
    # @param actionEvent 
    def actionPerformed(self, actionEvent):
        SetRTCTree(self.oTreeModel, self.smgr, self.ctx, self.dlg_control)


##
# @class TreeSelectListener
# @brief ツリーのマウスでの操作に対するコールバック
#

class TreeSelectListener( unohelper.Base, XSelectionChangeListener):
    ##
    # @brief コンストラクタ
    # @param self 
    # @param dlg_control ダイアログオブジェクト
    # @param _paths データポートのパス
    def __init__(self, dlg_control, _paths):
        self.dlg_control = dlg_control
        self._paths = _paths

    ##
    # @brief 
    # @param self 
    # @param ev 
    def selectionChanged(self, ev):
        try:
            draw = OOoDraw()
        except NotOOoDrawException:
            return

        sobj = draw.document.CurrentSelection
        
        if sobj:
            if sobj.Count > 0:
                obj = sobj.getByIndex(0)
                jport, d_type = JudgeDrawObjRTC(obj)

                
                
                if jport:
                    UpdateTree(self.dlg_control, jport)
                    return
        else:
            return

        info_control = self.dlg_control.getControl( ControlName.TextFName )
        info_control.setText(OOoRTC.SetCoding('未作成','utf-8'))





##
# @class DeleteListener
# @brief ポート削除ボタンのコールバック
#
class DeleteListener( unohelper.Base, XActionListener ):
    ##
    # @brief コンストラクタ
    # @param self 
    # @param dlg_control ダイアログオブジェクト
    # @param _paths データポートのパス
    def __init__(self, dlg_control, _paths):
        self._paths = _paths
        self.dlg_control = dlg_control

    ##
    # @brief 
    # @param self 
    # @param actionEvent 
    def actionPerformed(self, actionEvent):
        try:
            draw = OOoDraw()
        except NotOOoDrawException:
              return

        sobj = draw.document.CurrentSelection

        if sobj:
            if sobj.Count > 0:
                obj = sobj.getByIndex(0)
                jport, d_type = JudgeDrawObjRTC(obj)
                if jport:
                    if d_type == "DataInPort":
                        OOoRTC.draw_comp.mRemoveInPort(jport)
                    else:
                        OOoRTC.draw_comp.mRemoveOutPort(jport)
                    ClearInfo(self.dlg_control)
                    MyMsgBox('',OOoRTC.SetCoding('削除しました','utf-8'))

                    UpdateSaveSheet()
                    return
                    
            
        
        
        MyMsgBox(OOoRTC.SetCoding('エラー','utf-8'),OOoRTC.SetCoding('削除済みです','utf-8'))

##
# @class SetPosListener
# @brief 位置の初期化ボタンのコールバック
#
class SetPosListener( unohelper.Base, XActionListener ):
    ##
    # @brief コンストラクタ
    # @param self 
    # @param dlg_control ダイアログオブジェクト
    # @param _paths データポートのパス
    def __init__(self, dlg_control, _paths):
        
        self._paths = _paths
        self.dlg_control = dlg_control

    ##
    # @brief 
    # @param self 
    # @param actionEvent 
    def actionPerformed(self, actionEvent):
        
        objectTree = self.dlg_control.getControl(ControlName.RTCTreeName)
        
        t_comp, nd = OOoRTC.JudgePort(objectTree, self._paths)
        
        if t_comp:
            
            for n,i in OOoRTC.draw_comp.InPorts.items():
                if i._port_a[0] == t_comp[0]:
                    i._obj.RotateAngle = i._r
                    t_pos = Point()
                    t_pos.X = i._x
                    t_pos.Y = i._y
                    i._obj.setPosition(t_pos)
                    return
        else:
            MyMsgBox(OOoRTC.SetCoding('エラー','utf-8'),OOoRTC.SetCoding('データポートを選択してください','utf-8'))
            return
        
        MyMsgBox(OOoRTC.SetCoding('エラー','utf-8'),OOoRTC.SetCoding('削除済みです','utf-8'))


##
# @class SetAllPosListener
# @brief 位置の全初期化ボタンのコールバック
#
class SetAllPosListener( unohelper.Base, XActionListener ):
    ##
    # @brief コンストラクタ
    # @param self 
    # @param dlg_control ダイアログオブジェクト
    def __init__(self, dlg_control):
        self.dlg_control = dlg_control

    ##
    # @brief 
    # @param self 
    # @param actionEvent 
    def actionPerformed(self, actionEvent):
        
        for n,i in OOoRTC.draw_comp.InPorts.items():
          i._obj.RotateAngle = i._r
          t_pos = Point()
          t_pos.X = i._x
          t_pos.Y = i._y
          i._obj.setPosition(t_pos)


##
# @brief ダイアログ作成の関数
#
def SetDialog():
    try:
      draw = OOoDraw()
    except NotOOoDrawException:
        return
      
    sobj = draw.document.CurrentSelection
    if sobj == None:
        MyMsgBox(OOoRTC.SetCoding('エラー','utf-8'), OOoRTC.SetCoding('図形を選択してください','utf-8'))
        return
    elif sobj.Count < 1:
        MyMsgBox(OOoRTC.SetCoding('エラー','utf-8'), OOoRTC.SetCoding('図形を選択してください','utf-8'))
        return

  
    dialog_name = "OOoDrawControlRTC.RTCTreeDialog"

    ctx = uno.getComponentContext()
    smgr = ctx.ServiceManager
    dp = smgr.createInstance("com.sun.star.awt.DialogProvider")
    dlg_control = dp.createDialog("vnd.sun.star.script:"+dialog_name+"?location=application")




    oTree = dlg_control.getControl(ControlName.RTCTreeName)

    LoadSheet()
    

    oTreeModel = oTree.getModel()

    SetRTCTree_listener = SetRTCTreeListener( oTreeModel, smgr, ctx, dlg_control )
    setrtctree_control = dlg_control.getControl(ControlName.CreateTreeBName)
    setrtctree_control.addActionListener(SetRTCTree_listener)

    tfns_control = dlg_control.getControl( ControlName.NameServerFName )
    tfns_control.setText('localhost')

    xo_control = dlg_control.getControl( ControlName.XoffsetBName )
    xo_control.setText(str(0))

    yo_control = dlg_control.getControl( ControlName.YoffsetBName )
    yo_control.setText(str(0))

    ro_control = dlg_control.getControl( ControlName.RoffsetBName )
    ro_control.setText(str(0))

    xs_control = dlg_control.getControl( ControlName.XscaleBName )
    xs_control.setText(str(100))

    ys_control = dlg_control.getControl( ControlName.YscaleBName )
    ys_control.setText(str(100))

    dtcb_control = dlg_control.getControl( ControlName.DataTypeCBName )
    dtcb_control.addItem ("", dtcb_control.ItemCount)
    for n in DrawDataPort.DataType.DataTypeList:
        dtcb_control.addItem (n, dtcb_control.ItemCount)
    
    ptcb_control = dlg_control.getControl( ControlName.PortTypeCBName )
    ptcb_control.addItem ("DataInPort", ptcb_control.ItemCount)
    ptcb_control.addItem ("DataOutPort", ptcb_control.ItemCount)
    ptcb_control.setText('DataInPort')

    setallpos_listener = SetAllPosListener( dlg_control )
    setallpos_control = dlg_control.getControl(ControlName.SetAllPosBName)
    setallpos_control.addActionListener(setallpos_listener)

    
    
    
    
    
    dlg_control.execute()
    dlg_control.dispose()




    
    
    


g_exportedScripts = (SetDialog, createOOoDrawComp, Start, Stop, Set_Rate)
