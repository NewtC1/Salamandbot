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

#---------------------------------------
# [Required] Script information
#---------------------------------------
ScriptName = "Counter"
Website = "https://www.twitch.tv/newtc"
Creator = "Newt"
Version = "1.0.0.0"
Description = "Allows users to select stories to have me tell."

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
counter_file = os.path.join(os.path.dirname(__file__), "counter.json")

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
            self.Command = "!counter"
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
    """Required tick function"""
    # Globals
    global MySet
    global m_Active
    m_Active = False
    # Load in saved settings
    MySet = Settings(settingsFile)

    if not os.path.exists(counter_file):

        Parent.SendStreamMessage("No counter file found. Creating a new one.")

        data = {}
        with codecs.open(counter_file, encoding='utf-8-sig', mode='w+') as f:
            json.dump(data, f, encoding='utf-8-sig')

    # End of Init
    return


def Execute(data):
    """Required Execute function"""
    retVal = ''

    if data.IsChatMessage():
        if data.GetParam(0).lower() == MySet.Command.lower():
            if data.GetParamCount() == 3:
                # if the command is invoked with add
                if data.GetParam(1).lower() == "add":
                    # if the counter already exists
                    if data.GetParam(2) in load_counter_list():
                        respond(data, "That counter already exists. Try adding to it with <counter name> #.")
                    # else if the counter does not exist
                    else:
                        # add the counter to the counters.json
                        counter_list = load_counter_list()
                        counter_list[data.GetParam(2).lower()] = "0"
                        with codecs.open(counter_file, encoding='utf-8-sig', mode='w+') as f:
                            json.dump(counter_list, f, encoding='utf-8-sig')
                        respond(data, 'Counter "'+ data.GetParam(2) + '" successfully created.')

                # if the command is invoked with remove
                if data.GetParam(1).lower() == "remove":
                    # if the counter does not exist
                    if data.GetParam(2) not in load_counter_list():
                        respond(data, "That counter does not exist.")
                    # else if the counter does exist
                    else:
                        # remove the counter
                        counter_list = load_counter_list()
                        del counter_list[data.GetParam(2).lower()]
                        # counter_list[data.GetParam(2).lower()] = "0"
                        with codecs.open(counter_file, encoding='utf-8-sig', mode='w+') as f:
                            json.dump(counter_list, f, encoding='utf-8-sig')

        if data.GetParam(0).lower()[0] == '+':
            if data.GetParam(0).lower()[1:] in load_counter_list():
                if data.GetParamCount() == 2:
                    add_counter(data.GetParam(0).lower()[1:], int(data.GetParam(1)))
                elif data.GetParamCount() == 1:
                    add_counter(data.GetParam(0).lower()[1:], 1)
                else:
                    respond(data, "Incorrect number of inputs.")
                    return

        if data.GetParam(0).lower()[0] == '-':
            if data.GetParam(0).lower()[1:] in load_counter_list():
                if data.GetParamCount() == 2:
                    subtract_counter(data.GetParam(0).lower()[1:], int(data.GetParam(1)))
                elif data.GetParamCount() == 1:
                    subtract_counter(data.GetParam(0).lower()[1:], 1)
                else:
                    respond(data, "Incorrect number of inputs.")
                    return

        if data.GetParam(0).lower()[0] == '!':
            if data.GetParam(0).lower()[1:] in load_counter_list():
                respond(data, load_counter_list()[data.GetParam(0).lower()[1:]])


        
    return


def Tick():
    """Required tick function"""
    return


def respond(data, output):
    retVal = output
    
    # If the original message is from a discord message
    if data.IsFromDiscord():
        # if the original message is from a whisper
        if data.IsWhisper():
            Parent.SendDiscordDM(data.User, retVal)
        else:
            Parent.SendDiscordMessage(retVal)
    # If the original message is from a live stream
    else:
        if data.IsWhisper():
            Parent.SendStreamWhisper(data.UserName, retVal)
        else:
            Parent.SendStreamMessage(str(retVal))


def add_counter(key, amount):

    with codecs.open(counter_file, encoding='utf-8-sig', mode='r') as f:
        data = json.load(f, encoding='utf-8-sig')

    data[key] = str(int(data[key]) + amount)

    Parent.SendStreamMessage(data[key])

    with codecs.open(counter_file, encoding='utf-8-sig', mode='w+') as f:
        json.dump(data, f, encoding='utf-8-sig')

    return


def subtract_counter(key, amount):
    with codecs.open(counter_file, encoding='utf-8-sig', mode='r') as f:
        data = json.load(f, encoding='utf-8-sig')

    data[key] = str(int(data[key]) - amount)

    Parent.SendStreamMessage(data[key])

    with codecs.open(counter_file, encoding='utf-8-sig', mode='w+') as f:
        json.dump(data, f, encoding='utf-8-sig')
    return

def load_counter_list():
    """Returns a the list of counters as a settings object"""
    with codecs.open(counter_file, encoding='utf-8-sig', mode='r') as f:
        data = json.load(f, encoding='utf-8-sig')

    return data