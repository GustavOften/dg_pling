#!/usr/bin/env python
# -*- coding: utf-8 -*-

import Tkinter
import time
import tkFont
import csv
import os
import sys
import Queue
from musicControl import musicControl
from threading import Event
import globals

class plingMeny:
  def __init__(self, verbose=False, meny_fin=None):
    #Misc init
    self.verbose = verbose
    self.musicCtrl = musicControl(self.eventHandlerMusic, verbose=verbose)
    self.MetaLogged = False
    self.windowClosed = False
    self.plingFinishedEvent = Event()
    self.meny_fin = meny_fin
    #Tkinte init
    Tkinter.CallWrapper = CallWrapper
    self.master = Tkinter.Tk()
    self.master.protocol("WM_DELETE_WINDOW", self.on_closing)
    self.master.call('wm', 'attributes', '.', '-topmost', '1')
    self.script_dir = os.path.dirname(__file__) #<-- absolute dir the script is in
    #Title and icon 
    self.master.wm_title("Pling DG-bar")
    #icon = Tkinter.PhotoImage(file=os.path.join(self.script_dir,'files/icon.png'))
    #self.master.tk.call('wm', 'iconphoto', self.master._w, icon)
    
    self.masterFrame = Tkinter.Frame(self.master)
    self.masterFrame.pack(side="top", fill="both", expand=True)
    self.masterFrame.grid_rowconfigure(0, weight=1)
    self.masterFrame.grid_columnconfigure(0, weight=1)
    self.startPage()
    self.statPage()
    self.startPageFrame.grid()
    self.bool_StartPageRaised = True
    
  
  #------------------------Initialize start and stat page--------------------------- 
  def startPage(self):
    self.startPageFrame = Tkinter.Frame(self.masterFrame)
    #Pics and fonts
    self.imButton = Tkinter.PhotoImage(file=os.path.join(self.script_dir,"files/redButton.pgm"))
    self.imArrowDown = Tkinter.PhotoImage(file=os.path.join(self.script_dir,"files/arrowDown.pgm"))
    self.imArrowUp = Tkinter.PhotoImage(file=os.path.join(self.script_dir,"files/arrowUp.pgm"))
    self.customFont = tkFont.Font(family="Helvetica", size=50)
    self.customFont2= tkFont.Font(family="Helvetica", size=40)
    self.customFont3= tkFont.Font(family="Helvetica", size=35)
    #Volume buttons
    self.plingButton = Tkinter.Button(self.startPageFrame,
                         text="STOPP \n \"FØRR EI DAME\"", 
                         font=self.customFont,
                         command=self.stopMusic,
                         compound=Tkinter.TOP, 
                         image=self.imButton)
    self.plingButton.pack(side=Tkinter.RIGHT)
    self.volDownButton = Tkinter.Button(self.startPageFrame,
                         font=self.customFont,
                         command=self.volDown,
                         compound=Tkinter.TOP,
                         image=self.imArrowDown)
    self.volDownButton.pack(side=Tkinter.BOTTOM)
    self.volUpButton = Tkinter.Button(self.startPageFrame,
                     font=self.customFont,
                     command=self.volUp,
                     compound=Tkinter.TOP,
                     image=self.imArrowUp)
    self.volUpButton.pack(side=Tkinter.TOP)
    self.textFill = Tkinter.Canvas(self.startPageFrame,width=170,height=45)
    self.textFill.create_text(87,20,text="VOLUM",font=self.customFont3)
    self.textFill.pack(pady=40)
  
  def statPage(self):
    self.statPageFrame = Tkinter.Frame(self.masterFrame)
    self.statPageFrame.configure(bg='green')
    self.customFont2= tkFont.Font(family="Helvetica", size=20) 
    self.buttonInit()
    self.nmbOfColums = self.statPageFrame.grid_size()[0]
    self.gifInit1()
    self.gifInit2()
    Tkinter.Label(self.statPageFrame,text='Hvem Plinga?',bg='green',bd=3,font=self.customFont2).grid(row=0,column=0,columnspan=self.nmbOfColums)
 
  #------------------Button functions-----------------------------------   
  def stopMusic(self):
    if(self.verbose): print("Button pushed") 
    self.musicCtrl.stopPling()
    self.startPageFrame.grid_remove()
    self.statPageFrame.grid()
    self.bool_StartPageRaised = False
    self.afterInstance1 = self.master.after(120*1000, self.killGUI)
  
  def volUp(self):
    if(self.verbose): print "Volume up"   
    self.musicCtrl.vlcVolumeUp()
  
  def volDown(self):
    if(self.verbose): print "Volume down"
    self.musicCtrl.vlcVolumeDown()
  
  def on_closing(self):
    self.windowClosed = True
    self.killGUI()
    if self.bool_StartPageRaised:
      self.musicCtrl.stopPling()
    
  
  def killGUI(self):
    if not self.bool_StartPageRaised:
      self.master.after_cancel(self.afterInstance1)
    self.master.after_cancel(self.afterInstance2)
    self.master.after_cancel(self.afterInstance3)
    self.master.quit()
    self.master.destroy()
    
    #---Debug info/pling metadata collection---
    if not self.MetaLogged:
      if self.windowClosed:
        noLogReason = 'Window closed'
      else:
        noLogReason = 'Timeout'
      metaDataFile = open(os.path.join(self.script_dir,'plingMeta.csv'),'ab')
      csvMetaWrite = csv.writer(metaDataFile)
      csvMetaWrite.writerow(['Not registered ('+noLogReason+')', time.strftime('%A'), time.strftime('%d.%m.%Y'),time.strftime('%H:%M:%S')])
      metaDataFile.close()
    print("Pling finished, release blocking")
    self.meny_fin.set()
    self.plingFinishedEvent.set()

  def buttonInit(self):
    plingStats = []
    csvfile = open(os.path.join(self.script_dir,'plingStats.csv'), 'rb')
    plingStats.extend(csv.reader(csvfile))
    csvfile.close()
    j = 0
    i = 0
    for row in plingStats:
      names = row[0]+' '+row[1]
      (Tkinter.Button(self.statPageFrame,bg='green',borderwidth=5, width=25, text=names,font=self.customFont2, command=lambda name=names: self.ButtonHandler(name))).grid(row=i+1,column=j) 
      if not i%15 and i:
         j = j+1
         i = 0
      else:  
        i = i+1
  
  def ButtonHandler(self,name):
    plingStats = []
    csvfile = open(os.path.join(self.script_dir,'plingStats.csv'), 'rb')
    plingStats.extend(csv.reader(csvfile))
    csvfile.close()
    csvfile = open(os.path.join(self.script_dir,'plingStats.csv'), 'wb')
    csvWriter = csv.writer(csvfile)
    for row in plingStats:
        names = row[0]+' '+row[1]
        if(name in names):
          csvWriter.writerow([row[0],row[1], int(row[2])+1])
          globals.plinger_name = row[0]
        else:
          csvWriter.writerow([row[0],row[1], row[2]])
    csvfile.close()
    #---Debug info/pling metadata collection---
    metaDataFile = open(os.path.join(self.script_dir,'plingMeta.csv'),'ab')
    csvMetaWrite = csv.writer(metaDataFile)
    csvMetaWrite.writerow([name, time.strftime('%A'), time.strftime('%d.%m.%Y'),time.strftime('%H:%M:%S')])
    metaDataFile.close()
    self.MetaLogged = True 
    self.killGUI() 
  
  def gifInit1(self):
    self.labelGif1 = Tkinter.Label(self.statPageFrame, bg='green')
    self.labelGif1.grid(row=0,column=0)
    self.num1 = 0
    self.master.after(40, self.animate1)

  def gifInit2(self):
    self.labelGif2 = Tkinter.Label(self.statPageFrame, bg='green')
    self.labelGif2.grid(row=0,column=self.nmbOfColums-1)
    self.num2 = 0
    self.master.after(40, self.animate2)
            
  def animate1(self):
    try:
      img = Tkinter.PhotoImage(file=os.path.join(self.script_dir,"files/LeftHand.gif"), format="gif - {}".format(self.num1))
      self.labelGif1.config(image=img)
      self.labelGif1.image=img
      self.num1 += 1
    except:
      self.num1 = 0
    self.afterInstance2 = self.master.after(40, self.animate1)
        
  def animate2(self):
    try:
      img = Tkinter.PhotoImage(file=os.path.join(self.script_dir,"files/RightHand.gif"), format="gif - {}".format(self.num2))
      self.labelGif2.config(image=img)
      self.labelGif2.image=img
      self.num2 += 1
    except:
      self.num2 = 0
    self.afterInstance3 = self.master.after(40, self.animate2)

#---------------------Music finished event handler-------------------------------    
  def eventHandlerMusic(self, ev):
    self.musicCtrl.stopPling()
    self.startPageFrame.grid_remove()
    self.statPageFrame.grid()
    self.bool_StartPageRaised = False
    self.afterInstance1 = self.master.after(120*1000, self.killGUI)
 
 
#---------------------Start pling sequence----------------------------------------
  def run(self):
    #Start music
    self.musicCtrl.startPling()
    #Open meny
    self.master.mainloop()
    #Block until pling finished

    self.plingFinishedEvent.wait()
    print("afterPling finished event")
    if(self.verbose): print 'Pling Finished'


#--------------------Overriding Tkinter callWrapper to catch exceptions-----------
class CallWrapper:
    """Internal class. Stores function to call when some user
    defined Tcl function is called e.g. after an event occurred."""
    def __init__(self, func, subst, widget):
        """Store FUNC, SUBST and WIDGET as members."""
        self.func = func
        self.subst = subst
        self.widget = widget
    def __call__(self, *args):
        """Apply first function SUBST to arguments, than FUNC."""
        try:
            if self.subst:
                args = self.subst(*args)
            return self.func(*args)
        except SystemExit, msg:
            raise SystemExit, msg
        except:
            self.exc_info = sys.exc_info()
            raise self.exc_info[1], None, self.exc_info[2]
            #self.widget._report_exception()



#--------Main-------------------     
def main():
        NO_MUSIC = True
        meny = plingMeny()
        
        if(NO_MUSIC):
          meny.musicCtrl.startPling = dummyPlingHandler
          meny.stopPling = dummyPlingHandler

        meny.run()    

def dummyPlingHandler():
  pass

if __name__ =='__main__':
    main()
    
    
    
    