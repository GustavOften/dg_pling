#!/bin/bash

apt-get update
apt-get -y install vlc
apt-get -y install python-setuptools

easy_install python-vlc
easy_install watchdog

