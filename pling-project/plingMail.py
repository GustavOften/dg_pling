#!/usr/bin/env python
# -*- coding: utf-8 -*-

import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.image import MIMEImage
from email.header import Header
from email.utils import formataddr
from threading import Thread
from threading import Event
import os
import random
import time
import globals

class plingMail(Thread):
  def __init__(self,addr='smtp.gmail.com', port=587, user=None, pw=None, from_addr=None, to_addr=None, plingEvent=None, plingFinishedEvent=None,meny_fin=None, verbose=False):
    #Misc
    if(verbose): print 'Init plingMail class'
    self.MAX_NMB_MAILS = 10 
    self.nmbOfMails = 0
    self.oldDate = time.strftime('%d.%m')
    
    #Thread and event class stuff
    super(plingMail, self).__init__()
    self.daemon = True
    self.plingEvent = plingEvent
    self.plingFinishedEvent = plingFinishedEvent
    self.meny_fin = meny_fin

    #Email stuff 
    self.verbose = verbose
    self.addr = addr
    self.port = port
    self.user = user
    self.pw = pw
    self.from_addr = from_addr
    self.to_addr = to_addr
    self.script_dir = os.path.dirname(__file__) #<-- absolute dir the script is in
  
  def run(self):
    if(self.verbose): print "Run method started"
    while True:
      #Wait for pling event
      self.plingEvent.clear()
      self.plingEvent.wait()
      self.plingEvent.clear()

      self.meny_fin.clear()
      self.meny_fin.wait()
      self.meny_fin.clear()
      
      
      #Check spam blocker, and send mail 
      if(self.spamBlocker()):
        if(self.verbose): print "Pling Event, mail blocked by spam blocker"
      else:
        if(self.verbose): print "Pling Event, sending email!"
        self.sendPlingMail()

       #Lock pling mail until the pling meny is finished
      if(self.verbose): print 'Pling mail locked, waits for pling to finish'
      self.plingFinishedEvent.wait()
      if(self.verbose): print 'Pling mail released, pling finished'
      self.plingFinishedEvent.clear()
      
     
        
     
      
  def sendMsg(self, msg):
    if(self.verbose): print "Connect and login"
    self.server = smtplib.SMTP(self.addr, self.port, timeout=120)
    self.server.starttls()
    self.server.login(self.user, self.pw)
    
    if(self.verbose): print 'Sending email'
    self.server.sendmail(self.from_addr, self.to_addr, msg)
    
    if(self.verbose): print 'Closing connection'
    self.server.quit()
   
  def makePlingMsg(self):
    if(self.verbose): print 'Generating pling message'
    #Compose mail
    name = globals.plinger_name 
    if(name == 'GAMMEL PANG'):
      name = 'En GAMMEL PANG'
    subject  = "PLING!"
    author = formataddr((str(Header(u'DG-Pling', 'utf-8')), self.from_addr))
    quote = self.getPlingQuote()
    if(globals.pling_type == 'dame'):
	    html = """\
	    <html>
	      <head></head>
	      <body>
		   <font size="6"> 
		    """\
		     +globals.plinger_name+ \
		    """\
		    plinger på DG!!!<br>
		   </font>
		<picture> 
		  <img src="cid:image1">
		</picture>
		<p><br>
		Gammelt pling ordtak:
		</p>
		<i>
		""" \
		+quote+ \
		"""\
		</i>
		<p><br>
		   Hilsen <br>
		   DGs Plingkomite<br>
		</p>
	      </body>
	    </html>
	    """
    if(globals.pling_type == 'fernet'):
    	    html = """\
	    <html>
	      <head></head>
	      <body>
		   <font size="6"> 
		    """\
		     +globals.plinger_name+ \
		    """\
		    plinger Fernet på DG!!!<br>
		   </font>
		<picture> 
		  <img src="cid:image1">
		</picture>
		<p><br>
		Gammelt pling ordtak:
		</p>
		<i>
		""" \
		+quote+ \
		"""\
		</i>
		<p><br>
		   Hilsen <br>
		   DGs Plingkomite<br>
		</p>
	      </body>
	    </html>
	    """
    
    #Add picture
    if(globals.pling_type == 'dame'):
    	pic = os.path.join(self.script_dir, 'files/halvdan.jpg')
    if(globals.pling_type == 'fernet'):
	pic = os.path.join(self.script_dir, 'files/fernet_pic.jpg')
    fp = open(pic, 'rb')
    msgImage = MIMEImage(fp.read())
    fp.close()
    
    #Generate mail message
    self.plingMsg = MIMEMultipart()
    self.plingMsg['From'] = author
    self.plingMsg['To'] = self.to_addr
    self.plingMsg['Subject'] = subject
    message = MIMEText(html, 'html')
    self.plingMsg.attach(message)
    #Attach picture
    msgImage.add_header('Content-ID', '<image1>')
    self.plingMsg.attach(msgImage)
  
  def getPlingQuote(self):
    filePathSitater = os.path.join(self.script_dir, 'files/sitater.txt')
    randNmb = random.randint(0, 158)
    with open(filePathSitater,'r') as fp:
     for i, line in enumerate(fp):
         if i == randNmb:
           return line
           
    
  def sendPlingMail(self):
    self.makePlingMsg()
    try:
      self.sendMsg(self.plingMsg.as_string())

    except Exception as e:
      print str(e)
  
  def spamBlocker(self):
    date = time.strftime('%d.%m')
    if(date == self.oldDate):
      if (self.nmbOfMails < self.MAX_NMB_MAILS):
        self.nmbOfMails += 1
        return False
      else:
        return True
    else:
      self.oldDate = date
      self.nmbOfMails = 1
      return False
    
def main():
  user = "testdgpling@gmail.com"
  pw   = "!dettepassordeterfantastisk"
  from_addr = "testdgpling@gmail.com"
  to_addr = "g.often94@gmail.com"
  plingEvent = Event()
  plingFinishedEvent = Event()
  mail = plingMail(user=user, pw=pw, from_addr=from_addr, to_addr=to_addr, verbose=True, plingEvent=plingEvent, plingFinishedEvent=plingFinishedEvent)
  mail.sendPlingMail = dummyMailSender
  mail.start()

  while True:
    s = raw_input('Pling Mail Ready \n')
    if(s == 'mail'):
      plingEvent.set()
      print 'Sleep for 5 sek, and release pling mail'
      time.sleep(5)
      plingFinishedEvent.set()
def dummyMailSender():
  pass    

if __name__ =='__main__':
    main()
    






  
