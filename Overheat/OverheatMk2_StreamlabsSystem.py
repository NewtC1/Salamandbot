#!/usr/bin/python
# -*- coding: utf-8 -*-
# pylint: disable=invalid-name
"""Let viewers pay currency to boost currency payouts
for everyone in chat for x seconds"""
import json
import os, os.path
import operator
import time
import codecs
import glob
import random
import threading
import io

#---------------------------------------
# [Required] Script information
#---------------------------------------
ScriptName = "Overheat"
Website = "https://www.twitch.tv/newtc"
Creator = "Newt"
Version = "1.0.0.0"
Description = "Causes the campgrounds setup to overheat, pulling logs at random into the main campfire"

#---------------------------------------
# Versions
#---------------------------------------
"""
1.0.0.0 - Initial release
"""
#---------------------------------------
# Variables
#---------------------------------------
settingsFile = os.path.join(os.path.dirname(__file__), "settings.json")

#---------------------------------------
# Classes
#---------------------------------------
class Settings:
    """
    Tries to load settings from file if given
    The 'default' variable names need to match UI_Config"""
    def __init__(self, settingsFile=None):
        if settingsFile is not None and os.path.isfile(settingsFile):
            with codecs.open(settingsFile, encoding='utf-8-sig', mode='r') as f:
                self.__dict__ = json.load(f, encoding='utf-8-sig')

        else: #set variables if no settings file
            self.Enabled = True
            self.OnlyLive = False
            self.Command = "!overheat"
            self.Cost = 0
            self.UseCD = False
            self.Cooldown = 5
            self.cd_response = "{0} the command is still on cooldown for {1} seconds!"
    def ReloadSettings(self, data):
        """Reload settings on save through UI"""
        self.__dict__ = json.loads(data, encoding='utf-8-sig')
        return


    def SaveSettings(self, settingsFile):
        """Save settings to files (json and js)"""
        with codecs.open(settingsFile, encoding='utf-8-sig', mode='w+') as f:
            json.dump(self.__dict__, f, encoding='utf-8-sig')
        with codecs.open(settingsFile.replace("json", "js"), encoding='utf-8-sig', mode='w+') as f:
            f.write("var settings = {0};".format(json.dumps(self.__dict__, encoding='utf-8-sig')))
        return

def ReloadSettings(jsonData):
    """Reload settings"""
	# Globals
    global MySet

	# Reload saved settings
    MySet.ReloadSettings(jsonData)

	# End of ReloadSettings
    return

#---------------------------------------
# [Required] functions
#---------------------------------------
def Init():
    # Globals
    global MySet
    global shieldDir
    global attackTime
    global reduceby
    reduceby = 5
    shieldDir = "D:/Program Files/Streamlabs Chatbot/Services/Twitch/shields.txt"
    attackTime = time.time()
    # Load in saved settings
    MySet = Settings(settingsFile)

    # End of Init
    return

def Execute(data):
    
    # if there isn't an active timer and the stream is live
    return

def Tick():
    global attackTime
    global reduceby
    multiplier = 1
    newTime = 0

    # if the time is less than the projected time, start an attack
    if time.time() >= attackTime:
        newTime = feed(reduceby)
    
    if newTime > 0:
        attackTime = time.time()+(newTime * multiplier)
    

    return

# ----------------------------------------
# Helper functions
# ----------------------------------------
def feed():
    success = True

    # choose a value at random
    # roll for the value to reduce it by
    #


    return success


    
def respond(output):
    retVal = output
    Parent.SendStreamMessage(str(retVal))
    