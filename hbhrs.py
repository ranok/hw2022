#!/usr/bin/env python3
from time import sleep
from sys import argv
from libAnt.drivers.serial import SerialDriver
from libAnt.node import Node
from libAnt.profiles.factory import Factory
from libAnt.drivers.usb import USBDriver

import requests
recent_hrs = []

USER_ID = 0
if len(argv) > 1:
    USER_ID = int(argv[1])
else:
    print("Please pass your user ID number from the browser")

def callback(msg):
    global recent_hrs
    if type(msg) != str:
        recent_hrs.append(int(str(msg)))
        if len(recent_hrs) == 10:
            avg_hr = str(round(sum(recent_hrs)/len(recent_hrs)))
            requests.get('http://heartbeatz.media:5000/hr/' + str(USER_ID) + '?hr=' + avg_hr)
            recent_hrs = []
            print("Sending avg HR of: " + avg_hr)


def eCallback(e):
    raise e


with Node(SerialDriver('/home/ranok/myserial'), 'SerialNode1') as n:
    #with Node(SerialDriver('/dev/ttyUSB0'), 'SerialNode1') as n:
#with Node(USBDriver(vid=0x0FCF, pid=0x1008), 'MyNode') as n:
    n.enableRxScanMode()
    f = Factory(callback)
    n.start(f.parseMessage, eCallback)
    sleep(30)  # Listen for 30sec
