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
import io

# ---------------------------------------
# [Required] Script information
# ---------------------------------------
ScriptName = "Shields"
Website = "https://www.twitch.tv/newtc"
Creator = "Newt"
Version = "1.0.0.0"
Description = "Adds a constant increase in the currency gain rate based on the value the Shields file."

# ---------------------------------------
# Versions
# ---------------------------------------
"""
1.0.0.0 - Initial release
"""
# ---------------------------------------
# Variables
# ---------------------------------------
settingsFile = os.path.join(os.path.dirname(__file__), "settings.json")


# ---------------------------------------
# Classes
# ---------------------------------------
class Settings:
    """
    Tries to load settings from file if given
    The 'default' variable names need to match UI_Config"""

    def __init__(self, settingsFile=None):
        if settingsFile is not None and os.path.isfile(settingsFile):
            with codecs.open(settingsFile, encoding='utf-8-sig', mode='r') as f:
                self.__dict__ = json.load(f, encoding='utf-8-sig')

        else:  # set variables if no settings file
            self.Enabled = True
            self.OnlyLive = False
            self.Command = "!checkOptions"
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


# ---------------------------------------
# [Required] functions
# ---------------------------------------
def Init():
    """Required tick function"""
    # Globals
    global MySet
    global LastPayout
    LastPayout = time.time()
    global PayoutInterval
    PayoutInterval = 600  # base is set to 10 minutes between payout
    global BasePayout  # base payout of the script
    BasePayout = 0
    global PayoutMultiplier
    PayoutMultiplier = 1.0
    global shieldsFile
    shieldsFile = os.path.join(os.path.dirname(__file__), '../../Twitch/shields.txt')

    # Load in saved settings
    MySet = Settings(settingsFile)

    # End of Init
    return


def Execute(data):
    """Required Execute function"""

    return


def Tick():
    """Required tick function"""
    global LastPayout
    global PayoutInterval
    global BasePayout
    global PayoutMultiplier
    global shieldsFile

    # if the last payout was more than the interval's time ago, payout now.
    if time.time() - LastPayout > PayoutInterval and Parent.IsLive() is True:
        myDict = {}

        with io.open(shieldsFile, encoding='utf-8-sig', mode='r') as shields:
            shieldCount = int(shields.read().decode('utf-8-sig'))
            for viewers in set(Parent.GetViewerList()):
                myDict[viewers] = int(float(BasePayout) + (float(shieldCount) * PayoutMultiplier))

        # add points to all present viewers
        Parent.AddPointsAll(myDict)
        # Parent.SendTwitchMessage("The shields creak and wooden slabs fall from them.")

        LastPayout = time.time()
    return
