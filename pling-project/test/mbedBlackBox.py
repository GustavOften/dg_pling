#!/usr/bin/env python

import time
import sys
from threading import Thread
from threading import Event
import globals

class mbedBlackBox(Thread):
    def __init__(self,events):
       super(mbedBlackBox, self).__init__()
       self.daemon = True
       self.events = events

    def run(self):
      while 1:
        k = raw_input()
        s = raw_input("Print pling to pling")
        if(s == 'pling'):
          globals.pling_type = "dame"
          for event in self.events:
            event.set()
            time.sleep(0.1)
        if(s == 'fernet'):
          globals.pling_type = "fernet"
          for event in self.events:
            event.set()
            time.sleep(0.1)
        