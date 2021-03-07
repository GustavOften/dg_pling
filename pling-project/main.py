#!/usr/bin/env python
from mbed import mbed
from test.mbedBlackBox import mbedBlackBox
from musicControl import musicControl
from plingMeny import plingMeny
from plingMail import plingMail
import Tkinter
import logging
import time
import sys
import os
from threading import Event
from threading import Thread
import globals

def main():
    VERBOSE = True
    INCLUDE_MAIL = True
    plinger_name = ""
    
    #Generate event list
    NMB_OF_EVENTS = 2 #0:Start pling meny, 1:Send pling mail
    eventPlingList = makeEventList(NMB_OF_EVENTS)
    
    #Instantiate pling finished event 
    plingFinishedEvent = Event()
    meny_fin = Event()

    #Instantiate Mcu object and start thread
    if sys.argv[-1] == 'test':
      mcu = mbedBlackBox(eventPlingList)
    else:
      mcu = mbed(eventPlingList, verbose=VERBOSE)
    mcu.start()
    globals.initialize()
    if INCLUDE_MAIL:  
      #Instantiate Pling Mail object and start thread
      USER = "dgplingpling@gmail.com"
      PW = "chUswa+H7Mu!"
      FROM_ADDR = "DG-PLING"
      TO_ADDR = "g.often94@gmail.com"
      plingMailObj = plingMail(user=USER, pw=PW, from_addr=FROM_ADDR, to_addr=TO_ADDR, plingEvent=eventPlingList[1], plingFinishedEvent=plingFinishedEvent,meny_fin=meny_fin, verbose=VERBOSE)
      plingMailObj.start()
    #Start main loop
    while(True):
      global meny
      meny = plingMeny(verbose=VERBOSE, meny_fin=meny_fin)
      eventPlingList[0].clear()
      eventPlingList[0].wait() 
      eventPlingList[0].clear()
      meny.run()
      plingFinishedEvent.set()
      

#Function for generating event list
def makeEventList(nmbOfEvents = 1):
    eventList = []
    for i in range(nmbOfEvents):
      eventList.append(Event())
    return eventList

if(__name__ == '__main__'):
    script_dir = os.path.dirname(__file__) #<-- absolute dir the script is in
    logging.basicConfig(filename=os.path.join(script_dir,'errorlog.txt'), level=logging.DEBUG)
    try:
      main()
    except KeyboardInterrupt:
      if(meny.musicCtrl.appsMuted):
        meny.musicCtrl.unmuteApps()
    except:
      logging.exception("\n"+time.strftime("%c"))
      if(meny.musicCtrl.appsMuted):
        meny.musicCtrl.unmuteApps()
      raise Exception, 'Error logged'
