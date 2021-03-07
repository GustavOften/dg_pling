#!/usr/bin/env python
# -*- coding: utf-8 -*-

import Tkinter
import tkFont
import os
import csv
import time
import errorMail
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

class plingOmeter:
  def __init__(self):
    self.root = Tkinter.Tk()
    self.script_dir = "/home/dgmusic/dg_pling/plingOmeter-project" #<-- absolute dir the script is in
    self.fileName = '../pling-project/plingStats.csv'
    self.abs_file_path = os.path.join(self.script_dir, self.fileName)
    self.totalNmbPlings = 0
    self.masterFrame = Tkinter.Frame(self.root,bg='green')
    self.masterFrame.grid()
    
    #Minimize the window when x-button pushed 
    self.root.protocol("WM_DELETE_WINDOW", self.root.iconify)
    
    #Title and icon 
    self.root.wm_title("Pling-O-Meter")
    icon = Tkinter.PhotoImage(file=os.path.join(self.script_dir,'files/iconOmeter.pgm'))
    self.root.tk.call('wm', 'iconphoto', self.root._w, icon)
      
    # get screen width and height    
    self.ws = self.root.winfo_screenwidth() # width of the screen
    
    # y coordinate for the Tk root window
    self.y = 40

    self.customFont= tkFont.Font(family="Helvetica", size=20) 
    self.label = Tkinter.Label(self.masterFrame, text='Totalt antall plinger:',bd=3,bg='green',font=self.customFont)
    self.label.grid(row=0,column=0,columnspan=2)
    self.label1 = Tkinter.Label(self.masterFrame, text=str(self.totalNmbPlings),bd=3,bg='red',font=self.customFont)
    self.label1.grid(row=1,column=0,columnspan=2)
    self.label2 = Tkinter.Label(self.masterFrame, text='-----Top 5 Plingers-----',bd=3,bg='green',font=self.customFont)
    self.label2.grid(row=2,column=0,columnspan=2)
    self.labelTop5 = [0,0,0,0,0]
    for i in range(5):
      fonts = tkFont.Font(family="Helvetica", size=22-i*3)
      self.labelTop5[i] = Tkinter.Label(self.masterFrame,bd=3 ,bg='green',font=fonts)
      self.labelTop5[i].grid(row=i+3,column=0,columnspan=2)
    
    self.updateFrame()

  def updateFrame(self):
    try:
      self.root.lift()
      self.readStats()
      self.label1.config(text=str(self.totalNmbPlings))
      for i in range(5):
        strLabel = str(i+1)+'. '+self.listTop5[i*2] +': '+str(self.listTop5[i*2+1])
        self.labelTop5[i].config(text=strLabel)

      # Place the window in top right corner
      self.masterFrame.update()
      w = self.masterFrame.winfo_width() # width for the Tk
      h = self.masterFrame.winfo_height()# height for the Tk root
      # calculate x and y coordinates for the Tk root window
      x = self.ws - w
      self.root.geometry('%dx%d+%d+%d' % (w, h, x, self.y))
    except IOError:
      print 'Error: Cant open plingStats.csv file!'
 
  def readStats(self):
    #Read stats from plingStats file
    plingStats = []
    csvfile = open(self.abs_file_path, 'rb') 
    plingStats.extend(csv.reader(csvfile))
    csvfile.close()
    #Get total number of plings, and top 3
    self.totalNmbPlings = 0
    self.listTop5 = []
    dicPlingList = {}
    for row in plingStats:
      self.totalNmbPlings += int(row[2])
      dicPlingList[row[0]] = int(row[2])
    for i in range(5):
      maxPlingName = max(dicPlingList, key=lambda key: dicPlingList[key])
      self.listTop5 += (maxPlingName, dicPlingList[maxPlingName]) 
      del dicPlingList[maxPlingName]
  
  def run(self):
    self.root.mainloop()
    

class eventHandlerFileChanged(FileSystemEventHandler):
  def __init__(self, meter, dirPath, user, pw, from_addr, to_addr, verbose):
    self.meter = meter
    self.errorLogFile = os.path.join(dirPath,'errorlog.txt')
    self.errorMailObj = errorMail.errorMail(user=user, pw=pw, from_addr=from_addr, to_addr=to_addr, verbose=verbose)
    
  def on_modified(self, event):
    if 'plingStats.csv' in event.src_path: 
      self.meter.updateFrame()
    
    elif 'errorlog.txt' in event.src_path:
      file = open(self.errorLogFile, 'r')
      msg = file.read()
      file.close()
      self.errorMailObj.sendErrorMail(msg)
      

#--------Main-------------------     
def main(observer):
  #Constants for errorMail 
  VERBOSE = True
  USER = "testdgpling@gmail.com"      
  PW = "!dettepassordeterfantastisk"               
  FROM_ADDR = "DG-PLING FAILED"          
  TO_ADDR = "g.often94@gmail.com"

  print(os.path.dirname(__file__))
  
  #Get absolute paths to directories
  script_dir = "/home/dgmusic/dg_pling/plingOmeter-project" #<-- absolute dir the script is in
  rel_path = '../pling-project'
  abs_dir_path = os.path.join(script_dir, rel_path)
  
  #Instantiate plingOmeter and Watchdog
  meter = plingOmeter()
  
  eventHandler = eventHandlerFileChanged(meter, abs_dir_path, user=USER, pw=PW, from_addr=FROM_ADDR, to_addr=TO_ADDR, verbose=VERBOSE)
  observer.schedule(eventHandler, abs_dir_path, recursive=True)
  observer.start()
  
  #Start Tkinter main loop
  meter.run()
  
  
        
if __name__ =='__main__':
  #try:
  observer = Observer()
  main(observer)    
  #except:
  #  observer.stop()
  #observer.join()
    
    
    
