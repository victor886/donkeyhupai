#coding=utf-8
import wx,sys
import wx.lib.iewin as iewin
from wx.lib import sized_controls

import wx.grid

#python图像包，pyautogui和pytesser都需要依赖它，第一个装
#下载地址 https://pypi.python.org/pypi/Pillow/3.0.0 Pillow-3.0.0.win-amd64-py2.7.exe
#安装包 Pillow-3.0.0.win-amd64-py2.7.exe
from PIL import Image

#pyautogui用于模拟鼠标编辑和截屏，类似于按键精灵
#安装方式 pip install pyautogui
import pyautogui

#时间
import time
from datetime import datetime

#配置文件
import ConfigParser

import thread
import threading

import tesseract
import ctypes

import Queue as queue

import urllib2

import codecs

import wx.lib.agw.floatspin as FS

import  wx.lib.scrolledpanel as scrolled

api_page_time = tesseract.TessBaseAPI()
api_page_time.Init(".","num",tesseract.OEM_DEFAULT)
api_page_time.SetVariable("tessedit_char_whitelist", "0123456789")
api_page_time.SetPageSegMode(tesseract.PSM_SINGLE_LINE)

api_lowest_price = tesseract.TessBaseAPI()
api_lowest_price.Init(".","num",tesseract.OEM_DEFAULT)
api_lowest_price.SetVariable("tessedit_char_whitelist", "0123456789")
api_lowest_price.SetPageSegMode(tesseract.PSM_SINGLE_LINE)

api_my_price = tesseract.TessBaseAPI()
api_my_price.Init(".","eng",tesseract.OEM_DEFAULT)
api_my_price.SetVariable("tessedit_char_whitelist", "0123456789")
api_my_price.SetPageSegMode(tesseract.PSM_SINGLE_LINE)

api_return_btn = tesseract.TessBaseAPI()
api_return_btn.Init(".","chi_sim",tesseract.OEM_DEFAULT)
api_return_btn.SetPageSegMode(tesseract.PSM_SINGLE_LINE)

# 二值化    
threshold_num = 140    
table_num = []
for i in range(256):    
    if i < threshold_num:    
        table_num.append(0)    
    else:    
        table_num.append(1)
        
# 二值化    
threshold_hanzi = 140    
table_hanzi = []
for i in range(256):    
    if i < threshold_hanzi:    
        table_hanzi.append(1)    
    else:    
        table_hanzi.append(0)

def imageOptPageTime(im):
    im = im.convert('L')
    basewidth = 100
    wpercent = (basewidth/float(im.size[0]))
    hsize = int((float(im.size[1])*float(wpercent)))
    im = im.resize((basewidth,hsize), Image.ANTIALIAS)
    im = im.point(table_num, '1')
    return im
    
def imageOptLowestPrice(im):
    im = im.convert('L')
    basewidth = 250
    wpercent = (basewidth/float(im.size[0]))
    hsize = int((float(im.size[1])*float(wpercent)))
    im = im.resize((basewidth,hsize), Image.ANTIALIAS)
    im = im.point(table_num, '1')
    return im
    
def imageOptMyPrice(im):
    im = im.convert('L')
    basewidth = 250
    wpercent = (basewidth/float(im.size[0]))
    hsize = int((float(im.size[1])*float(wpercent)))
    im = im.resize((basewidth,hsize), Image.ANTIALIAS)
    return im
    
def imageOptReturnBtn(im):
    im = im.convert('L')
    basewidth = 300
    wpercent = (basewidth/float(im.size[0]))
    hsize = int((float(im.size[1])*float(wpercent)))
    im = im.resize((basewidth,hsize), Image.ANTIALIAS)
    im = im.point(table_hanzi, '1')
    return im    
    
#获取网页时间的秒数
def getPageTime(type = 'getPageTime', q = queue.Queue()):    
    global page_time_x_1, page_time_y_1, page_time_x_2, page_time_y_2
    global rep
    try:   
        im = pyautogui.screenshot(region=(page_time_x_1, page_time_y_1, page_time_x_2-page_time_x_1, page_time_y_2-page_time_y_1))
        im = imageOptPageTime(im)
        
        im.save('./log/' + 'getPageTime.bmp')
        pixImage = tesseract.pixRead('./log/' + 'getPageTime.bmp')
        api_page_time.SetImage(pixImage) 
        page_time_string = api_page_time.GetUTF8Text().split("\n")[0].strip().replace(" ","")

        page_time = int(page_time_string)
        q.put(page_time)
        return page_time
    except:
        sys_time = int(round(time.time() * 1000))
        im.save('./log/' + 'pagetime_' + str(sys_time)  + '.bmp')
        #sys_time = str(datetime.now().strftime('%Y%m%d%H%M%S'))
        #print sys_time + "\t" +  u'获取网页时间错误'
        q.put(0)
        return 0
        #raise

#获取左侧最低成交价（这个位置要包含冒号）
def getLowestPrice(type = 'getLowestPrice', q = queue.Queue()):
    global lowest_price_x_1, lowest_price_y_1, lowest_price_x_2, lowest_price_y_2
    global rep
    try:
        im = pyautogui.screenshot(region=(lowest_price_x_1, lowest_price_y_1, lowest_price_x_2-lowest_price_x_1, lowest_price_y_2-lowest_price_y_1))
        im = imageOptLowestPrice(im)
        
        im.save('./log/' + 'getLowestPrice.bmp')
        pixImage = tesseract.pixRead('./log/' + 'getLowestPrice.bmp')
        api_lowest_price.SetImage(pixImage) 
        lowest_price_string = api_lowest_price.GetUTF8Text().split("\n")[0].strip().replace(" ","")

        lowest_price =  int(lowest_price_string)
        q.put(lowest_price)
        return lowest_price
    except:
        sys_time = int(round(time.time() * 1000))
        im.save('./log/' + 'lowestprice_' + str(sys_time) + '.bmp') 
        #sys_time = str(datetime.now().strftime('%Y%m%d%H%M%S'))
        #print sys_time + "\t" +  u'获取最低成交价错误'
        q.put(0)
        return 0
        #raise

#获取右侧我的出价
def getMyPrice():
    global my_price_x_1, my_price_y_1, my_price_x_2, my_price_y_2
    global rep
    try:
        im = pyautogui.screenshot(region=(my_price_x_1, my_price_y_1, my_price_x_2-my_price_x_1, my_price_y_2-my_price_y_1))
        im = imageOptMyPrice(im)        
        im.save('./log/' + 'getMyPrice.bmp')
        pixImage = tesseract.pixRead('./log/' + 'getMyPrice.bmp')
        api_my_price.SetImage(pixImage) 
        my_price_string = api_my_price.GetUTF8Text().split("\n")[0].strip().replace(" ","")

        my_price =  int(my_price_string)
        return my_price
    except:
        sys_time = int(round(time.time() * 1000))
        im.save('./log/' + 'myprice_' + str(sys_time) + '.bmp')        
        sys_time = str(datetime.now().strftime('%Y%m%d%H%M%S'))
        print sys_time + "\t" + u'获取我的出价错误'
        return 0
        #raise
        
#获取返回按钮中文
def getReturnBtn():
    global return_btn_x_1, return_btn_y_1, return_btn_x_2, return_btn_y_2

    try:
        im = pyautogui.screenshot(region=(return_btn_x_1, return_btn_y_1, return_btn_x_2 - return_btn_x_1, return_btn_y_2 - return_btn_y_1))
        im = imageOptReturnBtn(im)
        im.save('./log/' + 'getReturnBtn.bmp')
        pixImage = tesseract.pixRead('./log/' + 'getReturnBtn.bmp')
        api_return_btn.SetImage(pixImage) 
        return_btn = api_return_btn.GetUTF8Text().split("\n")[0].strip().replace(" ","")
        return_btn = unicode(return_btn, encoding="utf-8", errors="ignore")
        
        return return_btn
    except:
        return '0'
        #raise
        
def pricePlan():    
    global sys_time_send, page_time_send, self_time_second, flag
    global btn_add_price, input_text_time
    try:
        btn_add_price.Enable(False)
        flag = True
        while True:
            #btn_add_price.SetBackgroundColour('Red')           
            if flag == False:
                btn_add_price.Enable(True)
                input_text_time.SetValue(u"不在监控")
                sys_time = str(datetime.now().strftime('%Y%m%d%H%M%S'))
                print sys_time + "\t" +  sys_time + "\t" + u"用户暂停"
                break
            time_start = int(round(time.time() * 1000))
            page_time = getPageTime()

            time_end = int(round(time.time() * 1000))
            ocr_time = time_end - time_start
            input_text_time.SetValue(str(page_time))
            sys_time = str(datetime.now().strftime('%Y%m%d%H%M%S'))
            print sys_time + "\t" +  u"当前秒数：" + str(page_time) + "\t" + str(ocr_time)
            if page_time >= self_time_second:
                page_time_send = page_time
                pyautogui.click(x=add_x, y=add_y) #加价
                pyautogui.click(x=send_x, y=send_y) #出价
                btn_add_price.Enable(True)
                sys_time = str(datetime.now().strftime('%Y%m%d%H%M%S'))
                print sys_time + "\t" +  u"到了预设的加价时间，直接加价！"
                break
        input_text_time.SetValue(u"不在监控")
    except:
        btn_add_price.Enable(True)
        input_text_time.SetValue(u"不在监控")
        sys_time = str(datetime.now().strftime('%Y%m%d%H%M%S'))
        print sys_time + "\t" +  u"定时启动结束！"
        return

def autoConfirm():
    global sys_time_send, page_time_send, flag
    global btn_confirm_price, input_text_time, input_text_lowest_price
    global force_send_time, force_send_delay_second, advance_price, delay_time, advance_work_time, supply_price_time
    global confirm_x, confirm_y
    global return_btn_confirm_x, return_btn_confirm_y
    global self_price_x, self_price_y
    global tab_advanced, supply_price_flag, advance_send_price_flag
    
    q_getPageTime = queue.Queue()
    q_getLowestPrice = queue.Queue()    
    
    try:
        btn_confirm_price.Enable(False)
        my_price = getMyPrice()
        flag = True
        while True:
            
            if flag == False:
                btn_confirm_price.Enable(True)
                input_text_time.SetValue(u"不在监控")
                input_text_lowest_price.SetValue(u"不在监控")
                sys_time = str(datetime.now().strftime('%Y%m%d%H%M%S'))
                print sys_time + "\t" +  u"用户暂停"
                return
            
            time_start = int(round(time.time() * 1000)) 
            
            t_getPageTime = threading.Thread(target=getPageTime, args=('getPageTime', q_getPageTime))
            t_getLowestPrice = threading.Thread(target=getLowestPrice, args=('getLowestPrice', q_getLowestPrice))

            t_getPageTime.start()
            t_getLowestPrice.start()
            t_getPageTime.join()
            t_getLowestPrice.join()
            
            page_time = q_getPageTime.get()
            input_text_time.SetValue(str(page_time))
            lowest_price = q_getLowestPrice.get()
            input_text_lowest_price.SetValue(str(lowest_price))
            highest_price = lowest_price + 300
            q_getPageTime.queue.clear()
            q_getLowestPrice.queue.clear()                           
             
            time_end = int(round(time.time() * 1000))
            ocr_time = time_end - time_start
            sys_time = str(datetime.now().strftime('%Y%m%d%H%M%S'))
            print sys_time + "\t" + str(page_time) + "\t" + str(highest_price) + "\t" + str(my_price) + "\t" + str(ocr_time)
            
            #根据差价决定出价时机
            if advance_send_price_flag and page_time >= advance_work_time:
                if lowest_price != 0 and my_price !=0 and my_price <= highest_price + advance_price:
                    time.sleep(delay_time)
                    pyautogui.click(x=confirm_x, y=confirm_y) #确定 
                    #btn_confirm_price.Enable(True)
                    sys_time = str(datetime.now().strftime('%Y%m%d%H%M%S'))
                    print sys_time + "\t" +  u"到了价格区间，直接出价！"
                    break
            else:
                if lowest_price != 0 and my_price !=0 and my_price <= highest_price:
                    pyautogui.click(x=confirm_x, y=confirm_y) #确定 
                    #btn_confirm_price.Enable(True)
                    sys_time = str(datetime.now().strftime('%Y%m%d%H%M%S'))
                    print sys_time + "\t" +  u"到了价格区间，直接出价！"
                    break
                
            #强制网页55秒出价
            if page_time >= force_send_time:
                if page_time == force_send_time:
                    time.sleep(force_send_delay_second)
                    pyautogui.click(x=confirm_x, y=confirm_y) #确定
                    sys_time = str(datetime.now().strftime('%Y%m%d%H%M%S'))
                    print sys_time + "\t" +  u"到了强制出价时间，延迟" + str(force_send_delay_second) + u"秒后，直接出价！"
                    break
                else:
                    pyautogui.click(x=confirm_x, y=confirm_y) #确定
                    sys_time = str(datetime.now().strftime('%Y%m%d%H%M%S'))
                    print sys_time + "\t" +  u"超过强制出价时间，直接出价！"
                    break
                    
        #智能补抢
        if supply_price_flag:
            input_text_time.SetValue(u"等待返回")
            input_text_lowest_price.SetValue(u"等待返回") 
            while True:
                if flag == False:
                    btn_confirm_price.Enable(True)
                    input_text_time.SetValue(u"不在监控")
                    input_text_lowest_price.SetValue(u"不在监控")
                    sys_time = str(datetime.now().strftime('%Y%m%d%H%M%S'))
                    print sys_time + "\t" +  u"用户暂停"
                    return
                
                return_btn = getReturnBtn()
                if return_btn.find(u'确') != -1 or return_btn.find(u'定') != -1:
                    #超过56秒就不补枪了
                    page_time = getPageTime()
                    if page_time > 56:
                        btn_confirm_price.Enable(True)
                        input_text_time.SetValue(u"不在监控")
                        input_text_lowest_price.SetValue(u"不在监控")
                        print sys_time + "\t" +  u"服务器已经返回，但是时间是" +str(page_time) + u"，超过56s，将不进行补抢!"
                        return
                    pyautogui.click(x = return_btn_confirm_x , y = return_btn_confirm_y) #确定
                    sys_time = str(datetime.now().strftime('%Y%m%d%H%M%S'))
                    print sys_time + "\t" +  u"服务器已经返回，将进行补抢!"
                    break
                sys_time = str(datetime.now().strftime('%Y%m%d%H%M%S'))
                print sys_time + "\t" +  u'等待返回补抢'
                
            while True:            
                if flag == False:
                    btn_confirm_price.Enable(True)
                    input_text_time.SetValue(u"不在监控")
                    input_text_lowest_price.SetValue(u"不在监控")
                    sys_time = str(datetime.now().strftime('%Y%m%d%H%M%S'))
                    print sys_time + "\t" +  u"用户暂停"
                    return
                    
                t_getPageTime = threading.Thread(target=getPageTime, args=('getPageTime', q_getPageTime))
                t_getLowestPrice = threading.Thread(target=getLowestPrice, args=('getLowestPrice', q_getLowestPrice))
                t_getPageTime.start()
                t_getLowestPrice.start()
                t_getPageTime.join()
                t_getLowestPrice.join()
                
                page_time = q_getPageTime.get()
                input_text_time.SetValue(str(page_time))                
                lowest_price = q_getLowestPrice.get()
                input_text_lowest_price.SetValue(str(lowest_price))
                
                q_getPageTime.queue.clear()
                q_getLowestPrice.queue.clear()                
            
                sys_time = str(datetime.now().strftime('%Y%m%d%H%M%S'))
                print sys_time + "\t" +  u"等待补抢时机:" + "\t" + str(page_time) + "\t" + str(lowest_price)
                
                if page_time >= supply_price_time:
                    supply_price = 300
                    try:
                        if page_time < 40:
                            supply_price = 300
                        else:
                            supply_price = int(tab_advanced.grid.GetCellValue(page_time-40, 1))
                    except:
                        supply_price = 300
                    new_price = lowest_price + supply_price
                    pyautogui.doubleClick(x=self_price_x, y=self_price_y) #双击自行输入价格输入框
                    pyautogui.typewrite(str(new_price)) #立即输入我的价格
                    pyautogui.click(x=send_x, y=send_y) #出价
                    sys_time = str(datetime.now().strftime('%Y%m%d%H%M%S'))
                    print sys_time + "\t" + str(new_price) +"\t" + u"完成智能补抢..."
                    break
        
        #完成后按钮恢复
        btn_confirm_price.Enable(True)
        input_text_time.SetValue(u"不在监控")
        input_text_lowest_price.SetValue(u"不在监控")
        
    except:
        raise
        btn_confirm_price.Enable(True)
        input_text_time.SetValue(u"不在监控")
        input_text_lowest_price.SetValue(u"不在监控")
        sys_time = str(datetime.now().strftime('%Y%m%d%H%M%S'))
        print sys_time + "\t" + u"智能确认异常结束！"
        return

#更新检测      
def checkConfUpdate():
    global logged_in 
    while True:
        if logged_in:                   
            global logged_type
            get_conf_file(logged_type)
            sys_time = str(datetime.now().strftime('%Y%m%d%H%M%S'))
            print sys_time + "\t" + "checking update"
            #time.sleep(300)
            exit();
        else:
            time.sleep(1)

class RedirectText(object):
    global log_file
    def __init__(self):
        self.out=codecs.open(log_file, "a", 'utf-8')

    def write(self,string):
        self.out.write(string)

class MyFrame(wx.Frame):
    """ We simply derive a new class of Frame. """
    def __init__(self, parent, title):
   
        self.t_checkConfUpdate = threading.Thread(target=checkConfUpdate, args=())
        self.t_checkConfUpdate.daemon = True
        self.t_checkConfUpdate.start()
    
        #主面板
        wx.Frame.__init__(self, parent, title=title, size=(1200,750),style=wx.STAY_ON_TOP|wx.DEFAULT_FRAME_STYLE^(wx.RESIZE_BORDER|wx.MAXIMIZE_BOX))
        
        #关闭事件
        self.Bind(wx.EVT_CLOSE, self.on_close)
        
        _icon = wx.Icon('./image/paimai.ico', wx.BITMAP_TYPE_ICO)
        self.SetIcon(_icon)
        
        self.ie = iewin.IEHtmlWindow(self)
        
        mainSizer = wx.BoxSizer(wx.HORIZONTAL)        
        consoleSizer = wx.BoxSizer(wx.VERTICAL)        
        self.consolePanel = wx.Panel(self, wx.ID_ANY)
        
        #信息监控拦
        monitor = wx.StaticBox(self.consolePanel, -1, u"信息监控:")
        wx_font = wx.Font(15, wx.MODERN, wx.NORMAL, wx.BOLD)
        monitor.SetFont(wx_font)        
        monitorSizer = wx.StaticBoxSizer(monitor, wx.VERTICAL)        
        
        #当前秒数
        textSizer_time = wx.BoxSizer(wx.HORIZONTAL)
        static_text = wx.StaticText(self.consolePanel, -1, u'系统秒数：')
        #static_text.SetForegroundColour('red')  #颜色  
        wx_font = wx.Font(12, wx.MODERN, wx.NORMAL, wx.LIGHT)  
        static_text.SetFont(wx_font)  
        textSizer_time.Add(static_text)
        
        global input_text_time
        input_text_time = wx.TextCtrl(self.consolePanel, -1, u'0', size=(60, -1), style=wx.TE_READONLY)  
        input_text_time.SetInsertionPoint(0)
        input_text_time.SetForegroundColour('red')  #颜色
        input_text_time.SetValue(u"不在监控")
        #self.input_text_time.Enable(False)
        textSizer_time.Add(input_text_time)
        
        static_text = wx.StaticText(self.consolePanel, -1, u' 秒')  
        #static_text.SetForegroundColour('red')  #颜色  
        wx_font = wx.Font(12, wx.MODERN, wx.NORMAL, wx.LIGHT)  
        static_text.SetFont(wx_font)  
        textSizer_time.Add(static_text)
        monitorSizer.Add(textSizer_time, 0, wx.ALL|wx.CENTER, 5)        
        
        #当前最低成交价
        textSizer_lowest_price = wx.BoxSizer(wx.HORIZONTAL)
        static_text = wx.StaticText(self.consolePanel, -1, u'最低价格：')  
        #static_text.SetForegroundColour('red')  #颜色  
        wx_font = wx.Font(12, wx.MODERN, wx.NORMAL, wx.LIGHT)  
        static_text.SetFont(wx_font)  
        textSizer_lowest_price.Add(static_text)
        
        global input_text_lowest_price
        input_text_lowest_price = wx.TextCtrl(self.consolePanel, -1, u'0', size=(60, -1), style=wx.TE_READONLY)  
        input_text_lowest_price.SetInsertionPoint(0)
        input_text_lowest_price.SetForegroundColour('red')  #颜色
        input_text_lowest_price.SetValue(u"不在监控")
        #input_text_lowest_price.Enable(False)
        textSizer_lowest_price.Add(input_text_lowest_price)
        
        static_text = wx.StaticText(self.consolePanel, -1, u' 元')  
        #static_text.SetForegroundColour('red')  #颜色  
        wx_font = wx.Font(12, wx.MODERN, wx.NORMAL, wx.LIGHT)  
        static_text.SetFont(wx_font)  
        textSizer_lowest_price.Add(static_text)
        monitorSizer.Add(textSizer_lowest_price, 0, wx.ALL|wx.CENTER, 5)        
        consoleSizer.Add(monitorSizer, 0, wx.EXPAND|wx.ALL, 9)        
        
        #分割线
        consoleSizer.Add(wx.StaticLine(self.consolePanel), 0, wx.ALL|wx.EXPAND, 4)
        
        #信息栏
        #log = wx.TextCtrl(self.consolePanel, wx.ID_ANY, style = wx.TE_MULTILINE|wx.TE_READONLY|wx.HSCROLL)
        #consoleSizer.Add(log, 3, wx.ALL|wx.EXPAND, 5)

        #基本设置的tab        
        self.notebook = wx.Notebook(self.consolePanel)        
        tab_basic = PageBasic(self.notebook)        
        self.notebook.AddPage(tab_basic, u"主面板")
        wx_font = wx.Font(13, wx.MODERN, wx.NORMAL, wx.BOLD)
        self.notebook.SetFont(wx_font)        
        
        #智能补抢的tab
        global tab_advanced
        tab_advanced = PageAdvanced(self.notebook)        
        self.notebook.AddPage(tab_advanced, u"智能补抢")
        wx_font = wx.Font(13, wx.MODERN, wx.NORMAL, wx.BOLD)
        self.notebook.SetFont(wx_font)        
                        
        #说明的tab
        '''
        tab_manual = PageManual(self.notebook)        
        self.notebook.AddPage(tab_manual, u"使用说明")
        wx_font = wx.Font(13, wx.MODERN, wx.NORMAL, wx.BOLD)
        self.notebook.SetFont(wx_font)
        '''
        
        consoleSizer.Add(self.notebook, 1, wx.EXPAND|wx.ALL, 5)
        
        self.consolePanel.SetSizer(consoleSizer)
		
        # layout
        mainSizer.Add(self.ie, 10, wx.EXPAND)
        mainSizer.Add(self.consolePanel, 3, wx.EXPAND)
        #mainSizer.Add(self.panel, 0, wx.EXPAND)
        self.SetSizer(mainSizer)
    
        # redirect text here
        redir=RedirectText()
        sys.stdout=redir        
    
        # Global accelerators        
        self.panel = wx.Panel(self, -1)
        id_enter = wx.NewId()
        id_ctrl = wx.NewId()
        id_escape = wx.NewId()
        id_f5 = wx.NewId()
        self.Bind(wx.EVT_MENU, tab_basic.pressed_enter, id=id_enter)
        self.Bind(wx.EVT_MENU, tab_basic.pressed_space, id=id_ctrl)
        self.Bind(wx.EVT_MENU, tab_basic.pressed_escape, id=id_escape)
        self.Bind(wx.EVT_MENU, tab_basic.pressed_f5, id=id_f5)
        accel_tbl = wx.AcceleratorTable([
            (wx.ACCEL_NORMAL, wx.WXK_RETURN, id_enter),
            (wx.ACCEL_NORMAL, wx.WXK_SPACE, id_ctrl),
            (wx.ACCEL_NORMAL, wx.WXK_ESCAPE, id_escape),
            (wx.ACCEL_NORMAL, wx.WXK_F5, id_f5)            
        ])
        self.SetAcceleratorTable(accel_tbl) 
        self.panel.SetFocus()
    
    def on_close(self, event):
        global flag
        flag = False
        dlg = wx.MessageDialog(self,u"                 感谢使用沪牌助手-2017年2月版！", u"确认", wx.OK|wx.CANCEL|wx.ICON_QUESTION)
        result = dlg.ShowModal()
        dlg.Destroy()
        if result == wx.ID_OK:
            self.Destroy()
        else:
            event.skip()
     

class PageManual(scrolled.ScrolledPanel):
    def __init__(self, parent):
        scrolled.ScrolledPanel.__init__(self, parent, -1)
        vbox = wx.BoxSizer(wx.VERTICAL)
        
        imageFile = './image/manual.bmp'
        png = wx.Image(imageFile, wx.BITMAP_TYPE_ANY).ConvertToBitmap()
        a = wx.StaticBitmap(self, -1, png, (0, 0), (png.GetWidth(), png.GetHeight()))

        vbox.Add(a, 0, wx.ALIGN_CENTRE|wx.ALL, 5)
      
        self.SetSizer(vbox)
        self.SetAutoLayout(1)
        self.SetupScrolling()
        
        

class PageAdvanced(wx.Panel):
    def __init__(self, parent):
        wx.Panel.__init__(self, parent)
        
        self.mainSizer = wx.BoxSizer(wx.VERTICAL)
        
        #Grid
        self.grid = wx.grid.Grid(self, -1)

        # Then we call CreateGrid to set the dimensions of the grid
        # (100 rows and 10 columns in this example)
        self.grid.CreateGrid(20, 2)
        
        for i in range(20):
            operate_second = str(40+i)
            operate_time = '11:29:'+ operate_second
            self.grid.SetCellValue(i, 0, operate_time)
            self.grid.SetCellFont(i, 0, wx.Font(12, wx.MODERN, wx.NORMAL, wx.BOLD))
            self.grid.SetCellFont(i, 1, wx.Font(12, wx.MODERN, wx.NORMAL, wx.BOLD))            
            self.grid.SetCellAlignment(i, 0, wx.ALIGN_CENTRE, wx.ALIGN_CENTRE)
            self.grid.SetCellAlignment(i, 1, wx.ALIGN_CENTRE, wx.ALIGN_CENTRE)
            self.grid.SetReadOnly(i, 0, True)        
        
        #补抢幅度初始化值
        self.grid.SetCellValue(0, 1, '1100')
        self.grid.SetCellValue(1, 1, '1100')
        self.grid.SetCellValue(2, 1, '1100')
        self.grid.SetCellValue(3, 1, '1000')
        self.grid.SetCellValue(4, 1, '1000')
        self.grid.SetCellValue(5, 1, '900')
        self.grid.SetCellValue(6, 1, '800')
        self.grid.SetCellValue(7, 1, '800')
        self.grid.SetCellValue(8, 1, '700')
        self.grid.SetCellValue(9, 1, '700')
        self.grid.SetCellValue(10, 1, '600')
        self.grid.SetCellValue(11, 1, '600')
        self.grid.SetCellValue(12, 1, '600')
        self.grid.SetCellValue(13, 1, '500')
        self.grid.SetCellValue(14, 1, '500')
        self.grid.SetCellValue(15, 1, '300')
        self.grid.SetCellValue(16, 1, '300')
        self.grid.SetCellValue(17, 1, '300')
        self.grid.SetCellValue(18, 1, '300')
        self.grid.SetCellValue(19, 1, '300')

        
        self.grid.SetColLabelValue(0, u"补抢时间")
        self.grid.SetColLabelValue(1, u"补抢金额")
        
        self.grid.SetRowLabelSize(2)
        #self.grid.SetColLabelSize(2)
        
        #grid.SetLabelBackgroundColour('green')

        # We can set the sizes of individual rows and columns
        # in pixels
        #self.grid.SetRowSize(0, 60)
        self.grid.SetColSize(0, 120)
        self.grid.SetColSize(1, 120)
        self.grid.SetDefaultRowSize(25)
        #智能补枪默认关闭
        self.grid.Enable(False)

        self.mainSizer.Add(self.grid, 0, wx.EXPAND|wx.ALL, 5)        
        self.SetSizer(self.mainSizer)
    
    '''
    def OnCheckbox(self, evt): 
        if self.checkbox_supply_price.Value == False:
            self.grid.Enable(False)
        else:
            self.grid.Enable(True)
            
        evt.Skip() # if this is commented out, then the event does not 
                    # propogate up to the panel
    '''
    
class PageBasic(wx.Panel):
    def __init__(self, parent):
        wx.Panel.__init__(self, parent)
        
        self.t_pricePlan = threading.Thread(target=pricePlan, args=())
        self.t_autoConfirm = threading.Thread(target=autoConfirm, args=())
        
        #self.SetBackgroundColour(wx.Colour(240,240,240))

        mainSizer = wx.BoxSizer(wx.VERTICAL)        
        
        consoleSizer = wx.BoxSizer(wx.VERTICAL)        
        self.consolePanel = wx.Panel(self, wx.ID_ANY)
        
        #基本设置
        basic_settings = wx.StaticBox(self.consolePanel, -1, u"基本设置:")
        wx_font = wx.Font(15, wx.MODERN, wx.NORMAL, wx.BOLD)
        basic_settings.SetFont(wx_font)        
        basicsettingsSizer = wx.StaticBoxSizer(basic_settings, wx.VERTICAL)
        
        #加价秒数文本框
        textSizer_add_price_time = wx.BoxSizer(wx.HORIZONTAL)
        static_text = wx.StaticText(self.consolePanel, -1, u'定时加价：')  
        #static_text.SetForegroundColour('red')  #颜色  
        wx_font = wx.Font(12, wx.MODERN, wx.NORMAL, wx.LIGHT)  
        static_text.SetFont(wx_font)  
        textSizer_add_price_time.Add(static_text)
        
        self.input_text_add_price_time = FS.FloatSpin(self.consolePanel, -1, size=(50, -1), min_val=0, max_val=59, increment=1, value=48, digits=0, agwStyle=FS.FS_LEFT)        
        #self.input_text_add_price_time = wx.TextCtrl(self.consolePanel, -1, u'48', size=(50, -1))  
        #self.input_text_add_price_time.GetTextCtrl().SetInsertionPoint(0)
        self.input_text_add_price_time.GetTextCtrl().SetForegroundColour('red')  #颜色
        textSizer_add_price_time.Add(self.input_text_add_price_time)
        
        
        static_text = wx.StaticText(self.consolePanel, -1, u' 秒')  
        #static_text.SetForegroundColour('red')  #颜色  
        wx_font = wx.Font(12, wx.MODERN, wx.NORMAL, wx.LIGHT)  
        static_text.SetFont(wx_font)  
        textSizer_add_price_time.Add(static_text)        
        
        basicsettingsSizer.Add(textSizer_add_price_time, 0, wx.ALL|wx.CENTER, 5)        
        
        #强制出价时间文本框
        textSizer_force_send_time = wx.BoxSizer(wx.HORIZONTAL)
        static_text = wx.StaticText(self.consolePanel, -1, u'强制出价：')
        #static_text.SetForegroundColour('red')  #颜色  
        wx_font = wx.Font(12, wx.MODERN, wx.NORMAL, wx.LIGHT)  
        static_text.SetFont(wx_font)  
        textSizer_force_send_time.Add(static_text)
        
        self.input_text_force_send_time = FS.FloatSpin(self.consolePanel, -1, size=(50, -1), min_val=0.0, max_val=59.0, increment=0.1, value=56.0, digits=1, agwStyle=FS.FS_LEFT)
        #self.input_text_force_send_time = wx.TextCtrl(self.consolePanel, -1, u'48', size=(50, -1)) 
        #self.input_text_force_send_time.GetTextCtrl().SetInsertionPoint(0)
        self.input_text_force_send_time.GetTextCtrl().SetForegroundColour('red')  #颜色
        textSizer_force_send_time.Add(self.input_text_force_send_time)
        
        static_text = wx.StaticText(self.consolePanel, -1, u' 秒')   
        #static_text.SetForegroundColour('red')  #颜色  
        wx_font = wx.Font(12, wx.MODERN, wx.NORMAL, wx.LIGHT)  
        static_text.SetFont(wx_font)  
        textSizer_force_send_time.Add(static_text)        
        
        basicsettingsSizer.Add(textSizer_force_send_time, 0, wx.ALL|wx.CENTER, 5)
        
        consoleSizer.Add(basicsettingsSizer, 0, wx.EXPAND|wx.ALL, 9)  
        
        #分割线
        consoleSizer.Add(wx.StaticLine(self.consolePanel), 0, wx.ALL|wx.EXPAND, 4)
        
        #高级设置
        advanced_settings = wx.StaticBox(self.consolePanel, -1, u"高级设置:")
        wx_font = wx.Font(15, wx.MODERN, wx.NORMAL, wx.BOLD)
        advanced_settings.SetFont(wx_font)        
        advancedsettingsSizer = wx.StaticBoxSizer(advanced_settings, wx.VERTICAL)
        
        #是否提前出价        
        wx_font = wx.Font(12, wx.MODERN, wx.NORMAL, wx.LIGHT)
        self.checkbox_advance_send_price = wx.CheckBox(self.consolePanel, -1, u'提前出价') # child of panel
        self.checkbox_advance_send_price.SetFont(wx_font)
        advancedsettingsSizer.Add(self.checkbox_advance_send_price, 0, wx.ALL|wx.ALIGN_LEFT , 5)
        self.checkbox_advance_send_price.SetValue(True)         
        
        #提前出价幅度
        textSizer_advance_send_price = wx.BoxSizer(wx.HORIZONTAL)
        static_text = wx.StaticText(self.consolePanel, -1, u'提前幅度：')
        #static_text.SetForegroundColour('red')  #颜色
        wx_font = wx.Font(12, wx.MODERN, wx.NORMAL, wx.LIGHT)  
        static_text.SetFont(wx_font)  
        textSizer_advance_send_price.Add(static_text)
        
        self.input_text_advance_send_price = FS.FloatSpin(self.consolePanel, -1, size=(50, -1), min_val=0, max_val=500, increment=100, value=100, digits=0, agwStyle=FS.FS_LEFT)
        #self.input_text_advance_send_price = wx.TextCtrl(self.consolePanel, -1, u'100', size=(50, -1))
        #self.input_text_advance_send_price.SetInsertionPoint(0)
        self.input_text_advance_send_price.GetTextCtrl().SetForegroundColour('red')  #颜色
        #self.input_text_advance_send_price.Enable(False)
        textSizer_advance_send_price.Add(self.input_text_advance_send_price)
        
        static_text = wx.StaticText(self.consolePanel, -1, u' 元')   
        #static_text.SetForegroundColour('red')  #颜色  
        wx_font = wx.Font(12, wx.MODERN, wx.NORMAL, wx.LIGHT)  
        static_text.SetFont(wx_font)  
        textSizer_advance_send_price.Add(static_text)
        advancedsettingsSizer.Add(textSizer_advance_send_price, 0, wx.ALL|wx.CENTER , 5)
        
        #延迟毫秒
        textSizer_advance_send_delay = wx.BoxSizer(wx.HORIZONTAL)
        static_text = wx.StaticText(self.consolePanel, -1, u'延迟秒数：')        
        #static_text.SetForegroundColour('red')  #颜色  
        wx_font = wx.Font(12, wx.MODERN, wx.NORMAL, wx.LIGHT)  
        static_text.SetFont(wx_font)  
        textSizer_advance_send_delay.Add(static_text)
        
        self.input_text_advance_send_delay = FS.FloatSpin(self.consolePanel, -1, size=(50, -1), min_val=0.0, max_val=5.0, increment=0.1, value=0, digits=1, agwStyle=FS.FS_LEFT)
        #self.input_text_advance_send_delay = wx.TextCtrl(self.consolePanel, -1, u'0.5', size=(50, -1))
        #self.input_text_advance_send_delay.SetInsertionPoint(0)
        self.input_text_advance_send_delay.GetTextCtrl().SetForegroundColour('red')  #颜色
        #self.input_text_advance_send_delay.Enable(False)        
        textSizer_advance_send_delay.Add(self.input_text_advance_send_delay)
        
        static_text = wx.StaticText(self.consolePanel, -1, u' 秒')   
        #static_text.SetForegroundColour('red')  #颜色  
        wx_font = wx.Font(12, wx.MODERN, wx.NORMAL, wx.LIGHT)  
        static_text.SetFont(wx_font)  
        textSizer_advance_send_delay.Add(static_text)
        advancedsettingsSizer.Add(textSizer_advance_send_delay, 0, wx.ALL|wx.CENTER , 5)
        
        #生效时间
        textSizer_advance_send_work = wx.BoxSizer(wx.HORIZONTAL)
        static_text = wx.StaticText(self.consolePanel, -1, u'生效时间：')
        
        #static_text.SetForegroundColour('red')  #颜色  
        wx_font = wx.Font(12, wx.MODERN, wx.NORMAL, wx.LIGHT)  
        static_text.SetFont(wx_font)  
        textSizer_advance_send_work.Add(static_text)
        
        self.input_text_advance_send_work = FS.FloatSpin(self.consolePanel, -1, size=(50, -1), min_val=0, max_val=59, increment=1, value=54, digits=0, agwStyle=FS.FS_LEFT)
        #self.input_text_advance_send_work = wx.TextCtrl(self.consolePanel, -1, u'50', size=(50, -1))
        #self.input_text_advance_send_work.SetInsertionPoint(0)
        self.input_text_advance_send_work.GetTextCtrl().SetForegroundColour('red')  #颜色
        #self.input_text_advance_send_work.Enable(False)        
        textSizer_advance_send_work.Add(self.input_text_advance_send_work)
        
        static_text = wx.StaticText(self.consolePanel, -1, u' 秒')   
        #static_text.SetForegroundColour('red')  #颜色  
        wx_font = wx.Font(12, wx.MODERN, wx.NORMAL, wx.LIGHT)  
        static_text.SetFont(wx_font)  
        textSizer_advance_send_work.Add(static_text)
        advancedsettingsSizer.Add(textSizer_advance_send_work, 0, wx.ALL|wx.CENTER , 5)
        
        #绑定
        self.checkbox_advance_send_price.Bind(wx.EVT_CHECKBOX, self.OnCheckboxAdvanceSendPrice) 
        
        #智能补抢        
        wx_font = wx.Font(12, wx.MODERN, wx.NORMAL, wx.LIGHT)
        self.checkbox_supply_price = wx.CheckBox(self.consolePanel, -1, u'智能补抢')
        self.checkbox_supply_price.SetFont(wx_font)
        advancedsettingsSizer.Add(self.checkbox_supply_price, 0, wx.ALL|wx.ALIGN_LEFT , 5)
        #智能补抢默认关闭
        self.checkbox_supply_price.SetValue(False)
        
        #补抢时间
        textSizer_supply_price_time = wx.BoxSizer(wx.HORIZONTAL)
        static_text = wx.StaticText(self.consolePanel, -1, u'补抢时间：')
        #static_text.SetForegroundColour('red')  #颜色  
        wx_font = wx.Font(12, wx.MODERN, wx.NORMAL, wx.LIGHT)  
        static_text.SetFont(wx_font)  
        textSizer_supply_price_time.Add(static_text)
        
        self.input_text_supply_price_time = FS.FloatSpin(self.consolePanel, -1, size=(50, -1), min_val=0, max_val=59, increment=1, value=48, digits=0, agwStyle=FS.FS_LEFT)
        #self.input_text_supply_price_time = wx.TextCtrl(self.consolePanel, -1, u'47', size=(50, -1))
        #self.input_text_supply_price_time.SetInsertionPoint(0)
        self.input_text_supply_price_time.GetTextCtrl().SetForegroundColour('red')  #颜色
        #self.input_text_supply_price_time.Enable(False)
        textSizer_supply_price_time.Add(self.input_text_supply_price_time)
        
        static_text = wx.StaticText(self.consolePanel, -1, u' 秒')   
        #static_text.SetForegroundColour('red')  #颜色  
        wx_font = wx.Font(12, wx.MODERN, wx.NORMAL, wx.LIGHT)  
        static_text.SetFont(wx_font)  
        textSizer_supply_price_time.Add(static_text)
        advancedsettingsSizer.Add(textSizer_supply_price_time, 0, wx.ALL|wx.CENTER , 5)
        #智能补抢默认关闭
        self.input_text_supply_price_time.Enable(False)
        
        #绑定checkbox
        self.checkbox_supply_price.Bind(wx.EVT_CHECKBOX, self.OnCheckboxSupplyPrice)
        consoleSizer.Add(advancedsettingsSizer, 0, wx.EXPAND|wx.ALL, 9)
        
        #分割线
        consoleSizer.Add(wx.StaticLine(self.consolePanel), 0, wx.ALL|wx.EXPAND, 4)        
        
        #操作指南边框
        guider = wx.StaticBox(self.consolePanel, -1, u"操作指南:")
        wx_font = wx.Font(15, wx.MODERN, wx.NORMAL, wx.BOLD) 
        guider.SetFont(wx_font)        
        guiderSizer = wx.StaticBoxSizer(guider, wx.VERTICAL)
        
        #定时加价按钮
        global btn_add_price
        btn_add_price = wx.Button(self.consolePanel, -1, u"定时加价(空格键)", size=(150, -1), style=wx.BU_EXACTFIT)
        #btn_add_price.SetBackgroundColour(wx.Colour(100,100,100))
        self.Bind(wx.EVT_BUTTON, self.pressed_space, btn_add_price)        
        guiderSizer.Add(btn_add_price, 0, wx.ALL|wx.CENTER, 5)
        
        
        #智能确认
        global btn_confirm_price
        btn_confirm_price = wx.Button(self.consolePanel, -1, u"智能确认(回车键)", size=(150, -1), style=wx.BU_EXACTFIT)
        #btn_confirm_price.SetBackgroundColour(wx.Colour(100,100,100))
        self.Bind(wx.EVT_BUTTON, self.pressed_enter, btn_confirm_price)        
        guiderSizer.Add(btn_confirm_price, 0, wx.ALL|wx.CENTER, 5)
        
        
        #取消
        global btn_cancle
        btn_cancle = wx.Button(self.consolePanel, -1, u"取消出价(ESC键)", size=(150, -1), style=wx.BU_EXACTFIT)
        #btn_cancle.SetBackgroundColour(wx.Colour(100,100,100))
        self.Bind(wx.EVT_BUTTON, self.pressed_escape, btn_cancle)        
        guiderSizer.Add(btn_cancle, 0, wx.ALL|wx.CENTER, 5)
        
        consoleSizer.Add(guiderSizer, 0, wx.EXPAND|wx.ALL, 9)

        self.consolePanel.SetSizer(consoleSizer)        
        mainSizer.Add(self.consolePanel, 0,wx.EXPAND|wx.ALL)        
        self.SetSizer(mainSizer)
        
    def OnCheckboxAdvanceSendPrice(self, evt): 
        if self.checkbox_advance_send_price.Value==False:
            self.input_text_advance_send_price.Enable(False)
            self.input_text_advance_send_delay.Enable(False)
            self.input_text_advance_send_work.Enable(False)
        else:
            self.input_text_advance_send_price.Enable(True)
            self.input_text_advance_send_delay.Enable(True)
            self.input_text_advance_send_work.Enable(True)
            
        evt.Skip() # if this is commented out, then the event does not 
                    # propogate up to the panel
                    
    def OnCheckboxSupplyPrice(self, evt):
        global tab_advanced
        if self.checkbox_supply_price.Value==False:
            self.input_text_supply_price_time.Enable(False)
            tab_advanced.grid.Enable(False)
        else:
            self.input_text_supply_price_time.Enable(True)
            tab_advanced.grid.Enable(True)
        evt.Skip() # if this is commented out, then the event does not 
                    # propogate up to the panel
        
    def pressed_space(self, event):
        global self_time_second
        #self.panel.SetFocus()        
        if self.t_pricePlan.isAlive() == False and self.t_autoConfirm.isAlive() == False:
            try:
                self_time_second = int(self.input_text_add_price_time.GetTextCtrl().GetValue())
            except:
                self_time_second = 48
            sys_time = str(datetime.now().strftime('%Y%m%d%H%M%S'))
            print sys_time + "\t" + u"定时" + str(self_time_second) + u"秒加价启动"
            self.t_pricePlan = threading.Thread(target=pricePlan, args=())
            self.t_pricePlan.start()
        #self.panel.SetFocus()
    
    def pressed_enter(self, event):
        global supply_price_flag, advance_send_price_flag
        global force_send_time, force_send_delay_second, advance_price, delay_time, advance_work_time, supply_price_time
        #self.panel.SetFocus()        
        if self.t_autoConfirm.isAlive() == False and self.t_pricePlan.isAlive() == False:            
            try:
                force_send_time_value = float(self.input_text_force_send_time.GetTextCtrl().GetValue())
                force_send_time = int(force_send_time_value)                
                force_send_delay_second = force_send_time_value - force_send_time
            except:                
                force_send_time = 56
                force_send_delay_second = 0.0                
            
            #智能补抢标志
            if self.checkbox_supply_price.Value == True:
                supply_price_flag = True
                try:
                    supply_price_time = int(self.input_text_supply_price_time.GetTextCtrl().GetValue())

                except:
                    supply_price_time = 48
            else:
                supply_price_flag = False
             
            #提前出价标志              
            if self.checkbox_advance_send_price.Value == True:
                advance_send_price_flag = True
                try:
                    advance_price = int(self.input_text_advance_send_price.GetTextCtrl().GetValue())
                except:
                    advance_price = 100
                try:
                    delay_time = float(self.input_text_advance_send_delay.GetTextCtrl().GetValue())
                except:
                    delay_time = 0.0
                try:
                    advance_work_time = int(self.input_text_advance_send_work.GetTextCtrl().GetValue())
                except:
                    advance_work_time = 54
            else:
                advance_send_price_flag = False
                advance_price = 0
                delay_time = 0
             
            sys_time = str(datetime.now().strftime('%Y%m%d%H%M%S'))
            print sys_time + "\t" + u"智能确认启动!"
            self.t_autoConfirm = threading.Thread(target=autoConfirm, args=())
            self.t_autoConfirm.start()
        #self.panel.SetFocus()        
        
    def pressed_escape(self, event):
        global flag
        flag = False
        #self.panel.SetFocus()
        
    def pressed_f5(self, event):
        global frame
        frame.ie.RefreshPage()
        #self.panel.SetFocus()
        
class LoginFrame(sized_controls.SizedDialog):

    def __init__(self, *args, **kwargs):
        super(LoginFrame, self).__init__(*args, **kwargs)
        self.parent = args[0]

        pane = self.GetContentsPane()
        '''
        pane_form = sized_controls.SizedPanel(pane)
        pane_form.SetSizerType('form')

        #label = wx.StaticText(pane_form, label=u'用户名')
        #label.SetSizerProps(halign='right', valign='center')
        #self.user_name_ctrl = wx.TextCtrl(pane_form, value=u"测试用户", size=((200, -1)))

        label = wx.StaticText(pane_form, label=u'登录码')
        label.SetSizerProps(halign='right', valign='center')

        self.password_ctrl = wx.TextCtrl(pane_form, size=((200, -1)), style=wx.TE_PASSWORD)
        self.password_ctrl.SetFocus()
        '''

        pane_btns = sized_controls.SizedPanel(pane)
        pane_btns.SetSizerType('horizontal')
        pane_btns.SetSizerProps(halign='right')

        test_btn = wx.Button(pane_btns, size=(100,-1), label=u'练习')
        login_btn = wx.Button(pane_btns, size=(100,-1), label=u'正式')        
        login_btn.SetDefault()
        #cancle_btn = wx.Button(pane_btns, label=u'取消')
        self.Fit()
        self.SetTitle(u'沪牌助手')
        self.CenterOnParent()
        self.parent.Disable()

        test_btn.Bind(wx.EVT_BUTTON, self.on_btn_test)
        login_btn.Bind(wx.EVT_BUTTON, self.on_btn_login)
        #cancle_btn.Bind(wx.EVT_BUTTON, self.on_btn_cancle)
        self.Bind(wx.EVT_CLOSE, self.on_close)
        
    def on_btn_test(self, event):
        self.SetTitle(u"体验版登录成功")
        sys_time = str(datetime.now().strftime('%Y%m%d%H%M%S'))
        print sys_time + "\t" +  u"体验版登录成功"
        global logged_in, logged_type
        logged_in = True
        logged_type = 'test'
        self.Close()

    def on_btn_login(self, event):
        self.SetTitle(u"正式环境登录成功")
        sys_time = str(datetime.now().strftime('%Y%m%d%H%M%S'))
        print sys_time + "\t" +  u"正式环境登录成功"
        global logged_in, logged_type
        logged_in = True
        logged_type = 'online'
        self.Close()
    
        '''
        #user_name = self.user_name_ctrl.GetValue()
        password = self.password_ctrl.GetValue()
        response = urllib2.urlopen('http://cbf1488.duapp.com/login?password='+password)
        ret = response.read()
        
        if ret == '0':
            self.SetTitle(u"正式环境登录成功")
            sys_time = str(datetime.now().strftime('%Y%m%d%H%M%S'))
            print sys_time + "\t" +  u"正式环境登录成功"
            global logged_in, logged_type
            logged_in = True
            logged_type = 'online'
            self.Close()
        elif ret == '1':            
            self.SetTitle(u"密码不正确")
            sys_time = str(datetime.now().strftime('%Y%m%d%H%M%S'))
            print sys_time + "\t" +  u"密码不正确！"
        elif ret == '2':
            self.SetTitle(u"密码过期")
            sys_time = str(datetime.now().strftime('%Y%m%d%H%M%S'))
            print sys_time + "\t" +  u"密码过期！"
        else:
            self.SetTitle(u"登录失败")
            sys_time = str(datetime.now().strftime('%Y%m%d%H%M%S'))
            print sys_time + "\t" +  u"登录失败！"
        '''

    def on_btn_cancle(self, event):
        self.Close()

    def on_close(self, event):
        global logged_in
        if not logged_in:
            self.parent.Close()
        self.parent.Enable()
        event.Skip()
        
def get_conf_file(type = 'test'):
    #屏幕坐标配置文件      
    config = ConfigParser.ConfigParser()
    
    sys_time = str(datetime.now().strftime('%Y%m%d%H%M%S'))
    print sys_time + "\t" +  "read local conf"        
    if type == 'test':
        conf = config.read("./conf/pos_51hupai.conf")
    elif type == 'online':
        conf = config.read("./conf/pos_online.conf")
    else:
        conf = config.read("./conf/pos_51hupai.conf")
            
    global first_login, version, pre_version
    version = int(config.get('version','version'))
    
    if first_login == True or version > pre_version:
            
        global frame, url
        url  = config.get('url','url')
        if first_login:
            frame.ie.LoadUrl(url)
        
        global page_time_x_1, page_time_y_1, page_time_x_2, page_time_y_2
        page_time_x_1 = int(config.get('page_time_1','x'))
        page_time_y_1 = int(config.get('page_time_1','y'))
        page_time_x_2 = int(config.get('page_time_2','x'))
        page_time_y_2 = int(config.get('page_time_2','y'))
        
        global lowest_price_x_1, lowest_price_y_1, lowest_price_x_2, lowest_price_y_2
        lowest_price_x_1 = int(config.get('lowest_price_1','x'))
        lowest_price_y_1 = int(config.get('lowest_price_1','y'))
        lowest_price_x_2 = int(config.get('lowest_price_2','x'))
        lowest_price_y_2 = int(config.get('lowest_price_2','y'))
        
        global add_x, add_y
        add_x = int(config.get('add','x'))
        add_y = int(config.get('add','y'))    
            
        global send_x, send_y
        send_x = int(config.get('send','x'))
        send_y = int(config.get('send','y'))
        
        global add_300_x, add_300_y
        add_300_x = int(config.get('add_300','x'))
        add_300_y = int(config.get('add_300','y'))
        
        global self_price_x, self_price_y
        self_price_x = int(config.get('self_price','x'))
        self_price_y = int(config.get('self_price','y'))
        
        global my_price_x_1, my_price_y_1, my_price_x_2, my_price_y_2
        my_price_x_1 = int(config.get('my_price_1','x'))
        my_price_y_1 = int(config.get('my_price_1','y'))
        my_price_x_2 = int(config.get('my_price_2','x'))
        my_price_y_2 = int(config.get('my_price_2','y'))
        
        global confirm_x, confirm_y
        confirm_x = int(config.get('confirm','x'))
        confirm_y = int(config.get('confirm','y'))
        
        global cancle_x, cancle_y
        cancle_x = int(config.get('cancle','x'))
        cancle_y = int(config.get('cancle','y'))
        
        global return_btn_x_1, return_btn_y_1, return_btn_x_2, return_btn_y_2
        return_btn_x_1 = int(config.get('return_btn_1','x'))
        return_btn_y_1 = int(config.get('return_btn_1','y'))
        return_btn_x_2 = int(config.get('return_btn_2','x'))
        return_btn_y_2 = int(config.get('return_btn_2','y'))
        
        global return_btn_confirm_x, return_btn_confirm_y
        return_btn_confirm_x = int(config.get('return_btn_confirm','x'))
        return_btn_confirm_y = int(config.get('return_btn_confirm','y'))
        
        if first_login:
            sys_time = str(datetime.now().strftime('%Y%m%d%H%M%S'))
            print sys_time + "\t" +  'setting new conf on first time'
        else:
            sys_time = str(datetime.now().strftime('%Y%m%d%H%M%S'))
            print sys_time + "\t" +  'updating new conf'
        
        first_login = False
        pre_version = version
        
    else:
        sys_time = str(datetime.now().strftime('%Y%m%d%H%M%S'))
        print sys_time + "\t" +  "conf not changed"  

if __name__ == "__main__":

    global log_time
    log_time = datetime.now().strftime('%Y%m%d%H%M%S')
    log_file = './log/' + log_time + '.log'

    #get_conf_file()
    global first_login, logged_in
    first_login = True
    logged_in = False
    
    #记录出价时刻的系统时间,以及自定义出价时间,强制出价时间
    global sys_time_send, page_time_send, self_time_second, force_time_second
    sys_time_send = 0
    page_time_send = 0
    self_time_second = 0
    force_time_second = 0  
        
    global flag
    flag = True
    
    app = wx.App(False)
    global frame
    frame = MyFrame(None, u"沪牌助手-2017年2月版")
    frame.SetPosition((0,0))
    #print frame.GetScreenPositionTuple()
    #print frame.GetPosition()
    frame.Show()
    
    login_frame = LoginFrame(frame)
    login_frame.Show()
    
    app.MainLoop()
