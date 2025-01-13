#!/usr/bin/env python
#
# BakeBit example for the basic functions of BakeBit 128x64 OLED (http://wiki.friendlyarm.com/wiki/index.php/BakeBit_-_OLED_128x64)
#
# The BakeBit connects the NanoPi NEO and BakeBit sensors.
# You can learn more about BakeBit here:  http://wiki.friendlyarm.com/BakeBit
#
# Have a question about this example?  Ask on the forums here:  http://www.friendlyarm.com/Forum/
#
'''
## License

The MIT License (MIT)

BakeBit: an open source platform for connecting BakeBit Sensors to the NanoPi NEO.
Copyright (C) 2016 FriendlyARM

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in
all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
THE SOFTWARE.
'''

import time, os, sys, subprocess, threading, signal, socket
import bakebit_128_64_oled as oled
from PIL import Image, ImageFont, ImageDraw

PAGE_0_TIME         = 0
PAGE_1_OS_INFO      = 1
PAGE_3_PWR_CANCEL   = 3
PAGE_4_PWR_OFF      = 4
PAGE_5_PWR_REBOOT   = 5
PAGE_6_PWR_OFF_S    = 6
PAGE_7_PWR_REBOOT_S = 7
PAGE_8_PHOTO        = 8

SCREEN_MODE_NORMAL  = 0
SCREEN_MODE_SAVE    = 1
SCREEN_MODE_SLEEP   = 2
SCREEN_MODE_WAKEUP  = 3
SCREEN_MODE_WAKEUP2 = 4
SCREEN_MODE_OFF     = 5

TIMEOUT_PHOTO_NEXT  = 5        #time in sec for Photo change 
TIMEOUT_PWR_MENU    = 30       #time in sec to exit power setting menu
TIMEOUT_SCREEN_SAVE = 60*30    #time in sec to enter screen saver if no KEY signal
TIMEOUT_SCREEN_SLEEP= 60*35    #time in sec to sleep screen if no KEY signal
TIMEOUT_SCREEN_OFF  = 60*60*24 #time in sec to turn off screen if no KEY signal
TIMEOUT_TIME_OFF    = 10        #time in sec to sleep screen after wakeup screen wakeup by timer 

t0 = time.time() #last KEY signal start time
t1 = time.time() #photo show start time
t2 = time.time() #time wakeup start time

width=128
height=64
pageCount=2
pageIndex=PAGE_0_TIME
showPageIndicator= False
screen_mode = SCREEN_MODE_NORMAL  
drawing = False
image = Image.new('1', (width, height))
draw = ImageDraw.Draw(image)
fontb24 = ImageFont.truetype('DejaVuSansMono-Bold.ttf', 24);
font14 = ImageFont.truetype('DejaVuSansMono.ttf', 14);
smartFont = ImageFont.truetype('DejaVuSansMono-Bold.ttf', 10);
fontb14 = ImageFont.truetype('DejaVuSansMono-Bold.ttf', 14);
font11 = ImageFont.truetype('DejaVuSansMono.ttf', 11);
lock = threading.Lock()
img_idx = 0

print( 'NanoHat OLED Init' ) 
oled.init()  #initialze SEEED OLED display
oled.setNormalDisplay()      #Set display to normal mode (i.e non-inverse mode)
oled.setHorizontalMode()
oled.setDisplayOn() 
#oled.setBrightness(255) #0~255, this oled do not support

def printc( msg  ):
    print(time.strftime("%X") + ' ' + msg)
    
def get_ip():
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        # doesn't even have to be reachable
        s.connect(('10.255.255.255', 1))
        IP = s.getsockname()[0]
    except:
        IP = '127.0.0.1'
    finally:
        s.close()
    return IP

def draw_page():
    global drawing
    global image
    global draw
    global oled
    global font
    global font14
    global smartFont
    global width
    global height
    global pageCount
    global pageIndex
    global showPageIndicator
    global width
    global height
    global lock
    global img_idx

    lock.acquire()
    is_drawing = drawing
    page_index = pageIndex
    lock.release()

    if is_drawing:
        return

    lock.acquire()
    drawing = True
    lock.release()
    
    # Draw a black filled box to clear the image.            
    draw.rectangle((0,0,width,height), outline=0, fill=0)
    # Draw current page indicator
    if showPageIndicator:
        dotWidth=4
        dotPadding=2
        dotX=width-dotWidth-1
        dotTop=(height-pageCount*dotWidth-(pageCount-1)*dotPadding)/2
        for i in range(pageCount):
            if i==page_index:
                draw.rectangle((dotX, dotTop, dotX+dotWidth, dotTop+dotWidth), outline=255, fill=255)
            else:
                draw.rectangle((dotX, dotTop, dotX+dotWidth, dotTop+dotWidth), outline=255, fill=0)
            dotTop=dotTop+dotWidth+dotPadding

    if page_index==PAGE_0_TIME: # Time info
        # text = time.strftime("%A")
        # draw.text((2,2),text,font=font14,fill=255)
        # text = time.strftime("%e %b %Y")
        # draw.text((2,18),text,font=font14,fill=255)
        # text = time.strftime("%X")
        # draw.text((2,40),text,font=fontb24,fill=255)  
              
        text = time.strftime("%y/%m/%d %a")
        draw.text((2,2),text,font=font14,fill=255)
        text = time.strftime("W%U")
        draw.rectangle((width-25,3,width-1,16), outline=0, fill=255)
        draw.text((width-23,4),text,font=font11,fill=0)
        
        text = time.strftime("%X")
        draw.text((8,22),text,font=fontb24,fill=255)
        
        text = time.strftime("%e %b %Y")
        cmd = "awk '{D=$1/86400;H=($1%86400)/3600;M=($1%3600)/60;printf(\"Up: %d day %02d:%02d\",D,H,M)}' /proc/uptime"
        text = subprocess.check_output(cmd, shell = True )
        #draw.rectangle((2,20,width,35), outline=1, fill=0)
        draw.text((2,50),text,font=font11,fill=255)
        
    elif page_index==PAGE_1_OS_INFO: # OS info
        # Draw some shapes.
        # First define some constants to allow easy resizing of shapes.
        padding = 2
        top = padding
        bottom = height-padding
        # Move left to right keeping track of the current x position for drawing shapes.
        x = 0
        IPAddress = get_ip()
        cmd = "top -bn1 | grep load | awk '{printf \"CPU Load: %.2f\", $(NF-2)}'"
        CPU = subprocess.check_output(cmd, shell = True )
        cmd = "free -m | awk 'NR==2{printf \"Mem: %s/%sMB %.2f%%\", $3,$2,$3*100/$2 }'"
        MemUsage = subprocess.check_output(cmd, shell = True )
        cmd = "df -h | awk '$NF==\"/\"{printf \"Disk: %d/%dGB %s\", $3,$2,$5}'"
        Disk = subprocess.check_output(cmd, shell = True )
        tempI = int(open('/sys/class/thermal/thermal_zone0/temp').read());
        if tempI>1000:
            tempI = tempI/1000
        tempStr = "CPU TEMP: %sC" % str(tempI)

        draw.text((x, top+5),       "IP: " + str(IPAddress),  font=smartFont, fill=255)
        draw.text((x, top+5+12),    str(CPU), font=smartFont, fill=255)
        draw.text((x, top+5+24),    str(MemUsage),  font=smartFont, fill=255)
        draw.text((x, top+5+36),    str(Disk),  font=smartFont, fill=255)
        draw.text((x, top+5+48),    tempStr,  font=smartFont, fill=255)
    
    elif page_index==PAGE_3_PWR_CANCEL: #shutdown -- cancel
        draw.text((2, 2),  'Shutdown?',  font=fontb14, fill=255)

        draw.rectangle((2,20,width-4,20+16), outline=0, fill=255)
        draw.text((4, 22),  'Cancel',  font=font11, fill=0)

        draw.rectangle((2,38,width-4,38+16), outline=0, fill=0)
        draw.text((4, 40),  'power off',  font=font11, fill=255)

    elif page_index==PAGE_4_PWR_OFF: #shutdown -- power off
        draw.text((2, 2),  'Shutdown?',  font=fontb14, fill=255)

        draw.rectangle((2,20,width-4,20+16), outline=0, fill=0)
        draw.text((4, 22),  'cancel',  font=font11, fill=255)

        draw.rectangle((2,38,width-4,38+16), outline=0, fill=255)
        draw.text((4, 40),  'Power off',  font=font11, fill=0)
    
    elif page_index==PAGE_5_PWR_REBOOT: #shutdown -- power off
        draw.text((2, 2),  'Shutdown?',  font=fontb14, fill=255)

        draw.rectangle((2,20,width-4,20+16), outline=0, fill=0)
        draw.text((4, 22),  'power off',  font=font11, fill=255)

        draw.rectangle((2,38,width-4,38+16), outline=0, fill=255)
        draw.text((4, 40),  'Reboot',  font=font11, fill=0)
        
    elif page_index==PAGE_6_PWR_OFF_S: #poweroff
        draw.text((2, 2),  'Powering off',  font=fontb14, fill=255)
        draw.text((2, 40),  'Please wait',  font=font11, fill=255)
        
    elif page_index==PAGE_7_PWR_REBOOT_S: #rebpoot
        draw.text((2, 2),  'Rebooting',  font=fontb14, fill=255)
        draw.text((2, 40),  'Please wait',  font=font11, fill=255)

    if page_index==PAGE_8_PHOTO: #photo
        oled.drawImage(imgList[img_idx])
    else:   
        oled.drawImage(image)

    lock.acquire()
    drawing = False
    lock.release()


def is_showing_power_msgbox():
    global pageIndex
    lock.acquire()
    page_index = pageIndex
    lock.release()
    if page_index==PAGE_3_PWR_CANCEL or page_index==PAGE_4_PWR_OFF or page_index==PAGE_5_PWR_REBOOT:
        return True
    return False

def is_showing_photo():
    global pageIndex
    lock.acquire()
    page_index = pageIndex
    lock.release()
    if page_index==PAGE_8_PHOTO:
        return True
    return False

def next_photo():
    global t1
    global img_idx 
    printc( 'Next photo' ) 
    t1 = time.time()   
    img_idx = (img_idx + 1) % len(imgList)

def update_page_index(pi):
    global pageIndex
    lock.acquire()
    pageIndex = pi
    lock.release()
    printc( 'PAGE['+str(pi)+']' ) 

def screen_save_check():
    global screen_mode
    if screen_mode == SCREEN_MODE_NORMAL:
        if time.time()-t0 >= TIMEOUT_SCREEN_SAVE:  
            screen_mode = SCREEN_MODE_SAVE
            printc( 'SCREEN_MODE_SAVE' ) 
            update_page_index(PAGE_8_PHOTO)
        
def screen_off_check():
    global screen_mode
    if screen_mode == SCREEN_MODE_SAVE:
        if time.time()-t0 < TIMEOUT_SCREEN_SLEEP:
            return
    elif screen_mode == SCREEN_MODE_WAKEUP2:
        if time.time()-t2 < TIMEOUT_TIME_OFF:
            return   
    else:
        return        
    if time.time()-t0 < TIMEOUT_SCREEN_OFF:
        screen_mode = SCREEN_MODE_SLEEP
        printc( 'SCREEN_MODE_SLEEP' )
    else:
        screen_mode = SCREEN_MODE_OFF
        printc( 'SCREEN_MODE_OFF' )
    #oled.clearDisplay()
    oled.setDisplayOff() 
    update_page_index(PAGE_0_TIME)
    

def time_wakeup_check():
    global t2
    global screen_mode
    if screen_mode == SCREEN_MODE_SLEEP or screen_mode == SCREEN_MODE_WAKEUP:
        tt = time.strftime("%X")
        hh  = tt.split(":")[0]
        min = tt.split(":")[1]
        sec = tt.split(":")[2]
        if (hh>='08' and hh<='18') :
            if screen_mode == SCREEN_MODE_SLEEP and (sec=='00') :
                t2 = time.time()               
                #if int(min)&1==0:
                if min == '00':
                    printc( 'oled.setNormalDisplay' )
                    oled.setNormalDisplay()
                elif min == '30':
                    printc( 'oled.setInverseDisplay' )
                    oled.setInverseDisplay()
                oled.setDisplayOn()                 
                update_page_index(PAGE_0_TIME)
                screen_mode = SCREEN_MODE_WAKEUP
                printc( 'SCREEN_MODE_WAKEUP' )
                
            elif screen_mode == SCREEN_MODE_WAKEUP and (sec=='05') :
                update_page_index(PAGE_1_OS_INFO)
                screen_mode = SCREEN_MODE_WAKEUP2 
                printc( 'SCREEN_MODE_WAKEUP2' )
                
                
def receive_signal(signum, stack):
    global pageIndex
    global t0
    global screen_mode
    
    lock.acquire()
    page_index = pageIndex
    lock.release()

    if page_index==PAGE_6_PWR_OFF_S or page_index==PAGE_7_PWR_REBOOT_S: #shuting down
        return
    
    t0 = time.time()
    if screen_mode != SCREEN_MODE_NORMAL:
        screen_mode = SCREEN_MODE_NORMAL
        printc( 'SCREEN_MODE_NORMAL' ) 
        oled.setNormalDisplay()
        oled.setDisplayOn()  
        printc( 'oled.setNormalDisplay' )
    
    if signum == signal.SIGUSR1:
        printc( 'K1 pressed' ) 
        if is_showing_power_msgbox():
            if page_index==PAGE_3_PWR_CANCEL:
                update_page_index(PAGE_4_PWR_OFF)
            elif page_index==PAGE_4_PWR_OFF:
                update_page_index(PAGE_5_PWR_REBOOT)
            else:
                update_page_index(PAGE_3_PWR_CANCEL)
        elif page_index==PAGE_0_TIME:
            printc( 'Start photo' ) 
            update_page_index(PAGE_8_PHOTO)
        elif page_index==PAGE_8_PHOTO:            
            next_photo() 
        else:
            update_page_index(PAGE_0_TIME)

    elif signum == signal.SIGUSR2:
        printc( 'K2 pressed' ) 
        if is_showing_power_msgbox():
            if page_index==PAGE_4_PWR_OFF:
                update_page_index(PAGE_6_PWR_OFF_S)
            elif page_index==PAGE_5_PWR_REBOOT:
                update_page_index(PAGE_7_PWR_REBOOT_S)
            else:
                update_page_index(PAGE_0_TIME)
        else:
            update_page_index(1)

    elif signum == signal.SIGALRM:
        printc( 'K3 pressed' ) 
        if is_showing_power_msgbox():
            update_page_index(PAGE_0_TIME)
        else:                   
            update_page_index(PAGE_3_PWR_CANCEL)
    
    elif signum == signal.SIGTERM:
        printc( 'Task kill' )                
        update_page_index(PAGE_6_PWR_OFF_S)
        draw_page()
        os._exit(0)
        
    draw_page()


#image0 = Image.open('friendllyelec.png').convert('1')
imgList = {}
imgList[0] = Image.open('fmlogo.png').convert('1')
imgList[1] = Image.open('heman.png').convert('1')
imgList[2] = Image.open('man.png').convert('1')
imgList[3] = Image.open('xixi.png').convert('1')
imgList[4] = Image.open('xixi2.png').convert('1')
imgList[5] = Image.open('planet.png').convert('1')
oled.drawImage(imgList[0])
time.sleep(2)

signal.signal(signal.SIGUSR1, receive_signal) #KEY1
signal.signal(signal.SIGUSR2, receive_signal) #KEY2
signal.signal(signal.SIGALRM, receive_signal) #KEY3
signal.signal(signal.SIGTERM, receive_signal) #poweroff

while True:
    try:
        lock.acquire()
        page_index = pageIndex
        lock.release()
            
        screen_save_check()
        screen_off_check()
        time_wakeup_check()
        
        if not (screen_mode==SCREEN_MODE_SLEEP or screen_mode==SCREEN_MODE_OFF):  
            if page_index==PAGE_0_TIME or page_index==PAGE_1_OS_INFO:
                draw_page() 

            if page_index==PAGE_6_PWR_OFF_S or page_index==PAGE_7_PWR_REBOOT_S: # shutdown clean up
                printc( 'process shutdown...' ) 
                time.sleep(2)
                while True:
                    lock.acquire()
                    is_drawing = drawing
                    lock.release()
                    if not is_drawing:
                        lock.acquire()
                        drawing = True
                        lock.release()
                        oled.clearDisplay()
                        break
                    else:
                        time.sleep(0.1)
                        continue
                time.sleep(1)
                if page_index==PAGE_6_PWR_OFF_S:
                    printc( 'execute poweroff' ) 
                    os.system('systemctl poweroff')
                else:
                    printc( 'execute reboot' ) 
                    os.system('systemctl reboot')
                break
            
            if page_index==PAGE_8_PHOTO: # photo auto play by 5s
                if time.time()-t1 >= TIMEOUT_PHOTO_NEXT:
                    next_photo()  
                    draw_page()                             
                
            if is_showing_power_msgbox():
                if time.time()-t0 >= TIMEOUT_PWR_MENU:
                    update_page_index(PAGE_0_TIME) 
                    draw_page()
           
        time.sleep(0.8)
        
    except KeyboardInterrupt:                                                                                                          
        break                     
    except IOError:                                                                              
        printc ("Error")
