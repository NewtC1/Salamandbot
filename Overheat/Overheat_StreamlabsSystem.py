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
timerActive = False

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
    global m_Active
    global shieldDir
    global timerActive
    timerActive = 0
    shieldDir = "D:/Program Files/Streamlabs Chatbot/Services/Twitch/shields.txt"
    m_Active = False
    # Load in saved settings
    MySet = Settings(settingsFile)

    # End of Init
    return

def Execute(data):
    campfireDir = 'D:/Program Files/Streamlabs Chatbot/Services/Twitch/flame.txt'
    global shieldDir
    global timerActive

    shieldInterval = 800
    shieldThreshold = 200
    # read in the campfire value
    with io.open(campfireDir, 'r', encoding='utf-8-sig') as file:
        campfire = file.read()
        campfire = int(campfire.decode('utf-8-sig'))

    if campfire > shieldInterval + shieldThreshold:
        campfire = campfire - shieldInterval

        with io.open(shieldDir, 'r', encoding='utf-8-sig') as file:
            shields = file.read()
            shields = int(shields.decode('utf-8-sig')) + 1

        with open(shieldDir, 'w+') as file:
            file.write(str(shields))

        # write the new campfire value in
        with open(campfireDir, 'w+') as file:
            file.write(str(campfire))
        Parent.SendStreamMessage("Flames scorch the ground around the central bonfire as a twisted wooden tree emerges from it, curling protectively around the Campgrounds.")
    
    #Parent.SendStreamMessage("Timers active: " + str(timerActive))
    # if there isn't an active timer and the stream is live
    elif timerActive < 1 and Parent.IsLive() is True:
        global shieldDir
        minRange = 40
        maxRange = 60
        multiplier = 60
        reduceby = int(Parent.GetRandom(minRange, maxRange)) # randomly generate how much to reduce it by
        
        with io.open(shieldDir, 'r', encoding = 'utf-8-sig') as file:
            shields = file.read()
            shields = int(shields.decode('utf-8-sig'))
            reduceby = reduceby - shields
                
        if reduceby > 0:
            timer = threading.Timer((reduceby*multiplier), feed, args=[reduceby, data])
            timer.start()
            timerActive = timerActive + 1
            #Parent.SendStreamMessage("Timers active: " + str(timerActive))
    #elif timerActive == True:
    #    Parent.SendStreamMessage('The flames are still sleeping.')
    return

def Tick():
    return

# ----------------------------------------
# Helper functions
# ----------------------------------------

def feed(reduceby, data):
    #Parent.SendStreamMessage("Beginning Overheat")
    global timerActive
    voteDir = 'D:/Program Files/Streamlabs Chatbot/Services/Twitch/Votes/'
    campfireDir = 'D:/Program Files/Streamlabs Chatbot/Services/Twitch/flame.txt'
    global shieldDir
    retVal = ''
    threshold = 800
    interval = 50 # for every 100 past 1000, increase the multiplier by 1
    payoutBase = 4 # base logs
    payoutInterval = 1000 # for every 1000 logs in the campfire, everyone gets an additional log per feed
    timerActive-=timerActive
    choices = os.listdir(voteDir)
    
    
    #read in the campfire value
    with io.open(campfireDir, 'r', encoding = 'utf-8-sig') as file:
        campfire = file.read()
        campfire = int(campfire.decode('utf-8-sig'))

    
    #else:
    # add multiple copies of choices with higher values
    for file in os.listdir(voteDir):
        #Parent.SendStreamMessage(file)
        with io.open(voteDir + file, 'r', encoding="utf-8-sig") as f:
            campfire = int(f.read().decode('utf-8-sig'))

            if campfire >= (threshold+interval):
                multiplier = (campfire-threshold)/ interval

                for i in range(multiplier):
                    choices.append(file)
            # displays the list after modifications
            #Parent.SendStreamMessage(str(campfire))


    choice = choices[Parent.GetRandom(0,len(choices))]
    name = choice # choose a random file from within the directory

    # Uncomment for a peek at what the choices look like
    #for each in choices:
    #    Parent.SendStreamMessage(str(each))

    with open(voteDir + name, 'r') as file: # open the random file
        filedata = int(file.read().decode('utf-8-sig'))

    #Parent.SendStreamMessage('Opened name: ' + name)

    if reduceby > filedata: # make sure it has enough logs to reduce by that much
        retVal += 'The questing tendrils of salamander flame pass up ' + name.split('.')[0] + '; It is too small to sate it\'s appetite.'

        #Parent.SendStreamMessage('Too small')
    else: # feed
        filedata = filedata - reduceby
        retVal += 'The salamander flame gorges itself on '+ name.split('.')[0] + '\'s log pile, consuming ' + str(reduceby) + ' logs. It is sated for now.'

        #Parent.SendStreamMessage('The right size.')

        # Write the reduced log count to the file.
        with open(voteDir + name, 'w+') as file:
            file.write(str(filedata))

        #Parent.SendStreamMessage('The right size, but smaller')

        # read in the campfire
        with io.open(campfireDir, 'r', encoding = 'utf-8-sig') as file:
            campfire = file.read()
            campfire = int(campfire.decode('utf-8-sig'))

            #Parent.SendStreamMessage("Old value: "+ str(campfire))
            #Parent.SendStreamMessage("Reduceby value: "+ str(reduceby))
            campfire = campfire + reduceby
            #Parent.SendStreamMessage("New value: "+ str(campfire))

            payout = int(payoutBase) + int(campfire / payoutInterval)

        #Parent.SendStreamMessage("The growing forest rewards users with " + str(payout) + ' logs.')

        # write the new campfire value in
        with open(campfireDir, 'w+') as file:
            file.write(str(campfire))

        #Parent.SendStreamMessage('New value written in.')

        myDict = {}
        for viewers in Parent.GetViewerList():
            # this controls how much chatters get payed
            myDict[viewers] = payout

        Parent.AddPointsAll(myDict)
        #Parent.SendStreamMessage("The growing forest rewards users with " + str(payout))

    if data.IsFromDiscord():
        if data.IsWhisper():
            Parent.SendDiscordDM(data.User, retVal)
        else:
            Parent.SendDiscordMessage(retVal)
    else:
        if data.IsWhisper():
            Parent.SendStreamWhisper(data.UserName, retVal)
        else:
            Parent.SendStreamMessage(retVal)
            
    return retVal