#!/usr/bin/env python

from subprocess import *
import re
import StringIO
import time
import os
import vlc
import sys
import globals

class musicControl:
  def __init__(self, eventHandler, verbose=False):
    self.verbose = verbose
    self.spotifyWasPlaying = False
    self.vlcSinkInputFound = False
    self.appsMuted         = False
    self.player            = None
    self.plingSongVol      = 70
    self.songFinishedHandler = eventHandler
    self.script_dir = os.path.dirname(__file__) #<-- absolute dir the script is in
        
  def playSong(self):
    if globals.pling_type == "dame":
      self.player = vlc.MediaPlayer(os.path.join(self.script_dir,"files/dame.mp3"))
    elif globals.pling_type == "fernet":
      self.player = vlc.MediaPlayer(os.path.join(self.script_dir,"files/fernet.mp3"))
    self.player.play()
    time.sleep(0.5)
    self.findVlcSinkInput()
    self.setVlcStartVolume()
    self.playerEvents = self.player.event_manager()
    self.playerEvents.event_attach(vlc.EventType.MediaPlayerEndReached, self.songFinishedHandler)
  
  def stopSong(self):
    if(not self.player is None):
      if self.player.is_playing():
        self.player.stop()
        self.player = None

  def stopSpotify(self):
    spotify = Popen("dbus-send --print-reply --dest=org.mpris.MediaPlayer2.spotify /org/mpris/MediaPlayer2 org.freedesktop.DBus.Properties.Get string:'org.mpris.MediaPlayer2.Player' string:'PlaybackStatus'|grep 'string \"[^\"]*\"'|sed 's/.*\"\\(.*\\)\"[^\"]*$/\\1/'", shell=True, stdout=PIPE,stderr=PIPE)
    out, err = spotify.communicate()
    if("Playing" in out):
        spotify = Popen("dbus-send --print-reply --dest=org.mpris.MediaPlayer2.spotify /org/mpris/MediaPlayer2 org.mpris.MediaPlayer2.Player.PlayPause", shell=True, stdout=PIPE,stderr=PIPE)
        self.spotifyWasPlaying = True    
  
  def startSpotify(self):
    if(self.spotifyWasPlaying):
        spotify = Popen("dbus-send --print-reply --dest=org.mpris.MediaPlayer2.spotify /org/mpris/MediaPlayer2 org.mpris.MediaPlayer2.Player.PlayPause", shell=True, stdout=PIPE,stderr=PIPE)
        self.spotifyWasPlaying = False
        
  def muteApps(self):
    sinkList = Popen("pactl list sink-inputs", shell=True, stdout=PIPE,stderr=PIPE)
    out, err = sinkList.communicate()
    self.sinkInputs = [] 
    out = StringIO.StringIO(out)
    for line in out: 
      if("Sink Input" in line):
        sinkInputNmb = re.findall(r'\d+',line)
        self.sinkInputs += sinkInputNmb
        Popen("pactl set-sink-input-mute "+sinkInputNmb.pop()+" toggle", shell=True)
        self.appsMuted = True
            
  def unmuteApps(self):
    if(self.appsMuted):
      for num in self.sinkInputs:
        Popen("pactl set-sink-input-mute "+num+" toggle", shell=True)
      self.appsMuted = False
      self.sinkInputs = []
    
  def findVlcSinkInput(self):
    i = 0
    while(i < 20):
      print(i)
      if(self.verbose): print(str(0.5+i*0.5)+'s: Trying to find the VLC sink input')
      sinkList = Popen("pactl list sink-inputs", shell=True, stdout=PIPE,stderr=PIPE)
      out, err = sinkList.communicate()
      out = StringIO.StringIO(out)
      for line in out: 
          if("Sink Input" in line):
              sinkInputNmb = re.findall(r'\d+',line)
              if(sinkInputNmb[0] not in self.sinkInputs):
                  self.vlcSinkNmb = sinkInputNmb.pop()
                  self.vlcSinkInputFound = True
                  break
      if(self.vlcSinkInputFound):
        break
      i += 1      
      time.sleep(0.5)

  def vlcVolumeUp(self):
    if (self.plingSongVol < 100 and self.vlcSinkInputFound): 
        self.plingSongVol = self.plingSongVol + 10
        Popen("pactl set-sink-input-volume "+self.vlcSinkNmb+" " +str(self.plingSongVol)+"%", shell=True)
        
  def vlcVolumeDown(self):
    if (self.plingSongVol > 0 and self.vlcSinkInputFound):
      self.plingSongVol = self.plingSongVol - 10
      Popen("pactl set-sink-input-volume "+self.vlcSinkNmb+" " +str(self.plingSongVol)+"%", shell=True)

  def setVlcStartVolume(self):
    if (self.vlcSinkInputFound):
      Popen("pactl set-sink-input-volume "+self.vlcSinkNmb+" " +str(self.plingSongVol)+"%", shell=True)

  def startPling(self):
    self.vlcSinkInputFound = False
    try:
      self.stopSpotify()
      self.muteApps()
      self.playSong()
    except:
      self.unmuteApps()
      self.stopSong()
      self.exc_info = sys.exc_info()
      raise self.exc_info[1], None, self.exc_info[2]
  
  def stopPling(self):
    self.stopSong()
    self.unmuteApps()
    self.startSpotify()
                
  def __del__(self):
    try:
        self.unmuteApps()
    except:
        pass

 
