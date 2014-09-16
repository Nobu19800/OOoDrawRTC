# -*- coding: utf-8 -*-

import os

mgr = None
calc_comp = None
draw_comp = None
writer_comp = None
impress_comp = None
base_comp = None





##
# 入力文字列をWriterのドキュメント上で文字化けしない文字コードで文字列を返す
# m_str：変換前の文字列
# m_code：変換前の文字コード
# 戻り値：変換後の文字列
##
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
# 文字、背景色の色をRGB形式から変換して返すクラス
# red、green、blue：各色(0～255)
# 戻り値：変換後の色の値
##

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




