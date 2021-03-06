#!/usr/bin/env python
# -*- coding: utf-8 -*-

import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.image import MIMEImage
import os
      
class errorMail():
  def __init__(self,addr='smtp.gmail.com', port=587, user=None, pw=None, from_addr=None, to_addr=None, verbose=False):
    if(verbose): print 'Init errorMail class'

    #Email stuff 
    self.verbose = verbose
    self.addr = addr
    self.port = port
    self.user = user
    self.pw = pw
    self.from_addr = from_addr
    self.to_addr = to_addr
    

  def sendMsg(self, msg):
    if(self.verbose): print "Connect and login"
    self.server = smtplib.SMTP(self.addr, self.port, timeout=120)
    self.server.starttls()
    self.server.login(self.user, self.pw)
    
    if(self.verbose): print 'Sending email'
    self.server.sendmail(self.from_addr, self.to_addr, msg)
    
    if(self.verbose): print 'Closing connection'
    self.server.quit()
   
  def makeErrorMsg(self, msg):
    if(self.verbose): print 'Generating error message'
    #Compose mail
    subject  = "Pling script crashed!"
    
    #Generate mail
    self.errorMsg = MIMEMultipart()
    self.errorMsg['From'] = self.from_addr
    self.errorMsg['To'] = self.to_addr
    self.errorMsg['Subject'] = subject
    message = MIMEText(msg)
    self.errorMsg.attach(message)
    
  def sendErrorMail(self, msg):
    self.makeErrorMsg(msg)
    try:
      self.sendMsg(self.errorMsg.as_string())

    except Exception as e:
      print str(e)

def main():
  USER = "testdgpling@gmail.com"      
  PW = "!dettepassordeterfantastisk"               
  FROM_ADDR = "DG-PLING FAILED" 
  TO_ADDR = "g.often94@gmail.com"
  
  file = open('C:\Users\g-oft\OneDrive\Dokumenter\DG\dg-prosjekt\pling-project\errorlog.txt', 'r')
  msg = file.read()
  file.close()
  
  mail = errorMail(user=USER, pw=PW, from_addr=FROM_ADDR, to_addr=TO_ADDR, verbose=True)
  mail.sendErrorMail(msg)
          

if __name__ =='__main__':
    main()
    






  