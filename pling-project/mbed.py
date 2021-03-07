#!/usr/bin/env python

import serial
import time
import sys
import globals
from threading import Thread
from threading import Event

class mbed(Thread):
    def __init__(self,events, verbose=False):
       self.verbose = verbose
       super(mbed, self).__init__()
       self.daemon = True
       self.events = events
       
    def run(self):
       self.connect()
       self.communicate()
           
    def connect(self):
        serdev = '/dev/ttyACM0'
        while(1):
            try:
                self.s = serial.Serial(port=serdev,timeout=None)
                if(self.verbose): print "Connected to MCU!"
                break
            except Exception as e: 
		print(e)
                if(self.verbose): print("Error when connecting to MCU!! \nTrying to reconnect in 10s")
                time.sleep(10)
            
    def communicate(self):
        while(1):
            try:
                time.sleep(1)
                if self.s.inWaiting():
                    self.s.flushInput()
                mld = ''
                while(True):
                    mld = self.s.read() 
                    while(self.s.inWaiting()):
                        mld += self.s.read()        
                    if(mld[0:5] == "PLING"):  
                        if(self.verbose): print "PLING"
			globals.pling_type = "dame"
                        for event in self.events:        
                          event.set()
                        time.sleep(5)
                        if self.s.inWaiting():
                          self.s.flushInput()
		    if(mld[0:6] == "FERNET"):
     			if(self.verbose): print "FERNET"
			globals.pling_type = "fernet"
                        for event in self.events:        
                          event.set()
                        time.sleep(5)
                        if self.s.inWaiting():
                          self.s.flushInput()
                    mld = ''   
            except KeyboardInterrupt:
                self.s.close()
                break
            except IOError:
                if(self.verbose): print "MCU unplugged, trying to reconnect!"
                self.s.close()
                self.connect()
            
    def __del___(self):
        try:
            self.s.close()
        except:
            pass
