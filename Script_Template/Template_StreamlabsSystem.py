#!/usr/bin/python
# -*- coding: utf-8 -*-
# pylint: disable=invalid-name
"""Let viewers pay currency to boost currency payouts
for everyone in chat for x seconds"""
import json
import os, os.path
import codecs

# ---------------------------------------
# [Required] Script information
# ---------------------------------------
ScriptName = "Template"
Website = "https://www.twitch.tv/newtc"
Creator = "Newt"
Version = "1.0.0.0"
Description = "Basic Template, use to create other scripts"

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
    """Required Init function, run when the bot loads the script."""
    # Globals
    global MySet
    # Load in saved settings
    MySet = Settings(settingsFile)

    # End of Init
    return


def Execute(data):
    """Required Execute function, run whenever a user says anything."""
    # user ID parsing based on origin
    send_user_id = parse_origin(data)[0]
    send_user_display = parse_origin(data)[1]

    return


def Tick():
    """Required tick function, run whenever possible."""
    return


def respond(data, output):
    """Basic upgraded response function. Delivers responses to whatever origin it was received from."""
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


def parse_origin(data):
    sender_user_id = ""
    sender_user_display = ""
    if data.IsFromTwitch():
        sender_user_id = data.UserName.lower
        sender_user_display = data.UserName
    elif data.IsFromYoutube():
        sender_user_id = data.User
        sender_user_display = data.UserName

    return sender_user_id, sender_user_display
