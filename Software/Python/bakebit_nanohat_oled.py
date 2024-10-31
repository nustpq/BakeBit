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

import bakebit_128_64_oled as oled
from PIL import Image
from PIL import ImageFont
from PIL import ImageDraw
import time
import sys
import subprocess
import threading
import signal
import os
import socket

global width
width=128
global height
height=64

global pageCount
pageCount=2
global pageIndex
pageIndex=0
global showPageIndicator
showPageIndicator= False

oled.init()  #initialze SEEED OLED display
oled.setNormalDisplay()      #Set display to normal mode (i.e non-inverse mode)
oled.setHorizontalMode()

global drawing 
drawing = False

global image
image = Image.new('1', (width, height))
global draw
draw = ImageDraw.Draw(image)
global fontb24
fontb24 = ImageFont.truetype('DejaVuSansMono-Bold.ttf', 24);
global font14 
font14 = ImageFont.truetype('DejaVuSansMono.ttf', 14);
global smartFont
smartFont = ImageFont.truetype('DejaVuSansMono-Bold.ttf', 10);
global fontb14
fontb14 = ImageFont.truetype('DejaVuSansMono-Bold.ttf', 14);
global font11
font11 = ImageFont.truetype('DejaVuSansMono.ttf', 11);

global lock
lock = threading.Lock()
global img_idx
img_idx = 0
global t0
t0 = time.time()

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

    if page_index==0: # Time info
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
        
    elif page_index==1: # OS info
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
    
    elif page_index==3: #shutdown -- cancel
        draw.text((2, 2),  'Shutdown?',  font=fontb14, fill=255)

        draw.rectangle((2,20,width-4,20+16), outline=0, fill=255)
        draw.text((4, 22),  'Cancel',  font=font11, fill=0)

        draw.rectangle((2,38,width-4,38+16), outline=0, fill=0)
        draw.text((4, 40),  'power off',  font=font11, fill=255)

    elif page_index==4: #shutdown -- power off
        draw.text((2, 2),  'Shutdown?',  font=fontb14, fill=255)

        draw.rectangle((2,20,width-4,20+16), outline=0, fill=0)
        draw.text((4, 22),  'cancel',  font=font11, fill=255)

        draw.rectangle((2,38,width-4,38+16), outline=0, fill=255)
        draw.text((4, 40),  'Power off',  font=font11, fill=0)
    
    elif page_index==5: #shutdown -- power off
        draw.text((2, 2),  'Shutdown?',  font=fontb14, fill=255)

        draw.rectangle((2,20,width-4,20+16), outline=0, fill=0)
        draw.text((4, 22),  'power off',  font=font11, fill=255)

        draw.rectangle((2,38,width-4,38+16), outline=0, fill=255)
        draw.text((4, 40),  'Reboot',  font=font11, fill=0)
        
    elif page_index==6: #poweroff
        draw.text((2, 2),  'Powering off',  font=fontb14, fill=255)
        draw.text((2, 40),  'Please wait',  font=font11, fill=255)
        
    elif page_index==7: #rebpoot
        draw.text((2, 2),  'Rebooting',  font=fontb14, fill=255)
        draw.text((2, 40),  'Please wait',  font=font11, fill=255)

    if page_index==8: #photo
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
    if page_index==3 or page_index==4 or page_index==5:
        return True
    return False

def is_showing_photo():
    global pageIndex
    lock.acquire()
    page_index = pageIndex
    lock.release()
    if page_index==8:
        return True
    return False

def next_photo():
    global t0
    global img_idx 
    print 'Next photo' 
    t0 = time.time()   
    img_idx = (img_idx + 1) % len(imgList)

def update_page_index(pi):
    global pageIndex
    lock.acquire()
    pageIndex = pi
    lock.release()
    print 'PAGE['+str(pi)+']'

def receive_signal(signum, stack):
    global pageIndex
    global t0
    
    lock.acquire()
    page_index = pageIndex
    lock.release()

    if page_index==6 or page_index==7: #shutdown
        return
    
    t0 = time.time() 
    if signum == signal.SIGUSR1:
        print 'K1 pressed'
        if is_showing_power_msgbox():
            if page_index==3:
                update_page_index(4)
            elif page_index==4:
                update_page_index(5)
            else:
                update_page_index(3)
        elif page_index==0:
            print 'Start photo'
            update_page_index(8)
        elif page_index==8:            
            next_photo() 
        else:
            update_page_index(0)

    elif signum == signal.SIGUSR2:
        print 'K2 pressed'
        if is_showing_power_msgbox():
            if page_index==4:
                update_page_index(6)
            elif page_index==5:
                update_page_index(7)
            else:
                update_page_index(0)
        else:
            update_page_index(1)

    elif signum == signal.SIGALRM:
        print 'K3 pressed'
        if is_showing_power_msgbox():
            update_page_index(0)
        else:                   
            update_page_index(3)
    
    elif signum == signal.SIGTERM:
        print 'Task kill'                   
        update_page_index(6)
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
        
        if page_index==0 or page_index==1:
            draw_page()         

        if page_index==6 or page_index==7: # shutdown clean up
            print 'process shutdown...'
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
                    time.sleep(.1)
                    continue
            time.sleep(1)
            if page_index==6:
                print 'execute poweroff'
                os.system('systemctl poweroff')
            else:
                print 'execute reboot'
                os.system('systemctl reboot')
            break
        
        if page_index==8: # photo auto play by 5s
            if time.time()-t0 >= 5:
               next_photo()  
               draw_page()
        elif is_showing_power_msgbox():
            if time.time()-t0 >= 30:
               update_page_index(0) 
               draw_page()
            
        time.sleep(1)
    except KeyboardInterrupt:                                                                                                          
        break                     
    except IOError:                                                                              
        print ("Error")
