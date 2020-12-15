#!/usr/bin/python
# -*- coding: utf-8 -*-
# pylint: disable=invalid-name
"""Let viewers pay currency to boost currency payouts
for everyone in chat for x seconds"""
import json
import os, os.path
import codecs
import time

# ---------------------------------------
# [Required] Script information
# ---------------------------------------
ScriptName = "Woodchips"
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
points_json = os.path.join(os.path.dirname(__file__), "points.json")


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
    global LastPayout
    # Load in saved settings
    MySet = Settings(settingsFile)
    LastPayout = time.time()

    if not os.path.exists(points_json):
        with open(points_json, "w+") as f:
            base_file = \
            {
                "Users": {

                }
            }

            result = json.dumps(base_file, f, indent=4)
            f.write(result)

    # End of Init
    return


def Execute(data):
    """Required Execute function, run whenever a user says anything."""

    return


def Tick():
    """Required tick function, run whenever possible."""
    global MySet
    global LastPayout

    # if the last payout was more than the interval's time ago, payout now.
    if time.time() - LastPayout > MySet.PayoutInterval and Parent.IsLive() is True:

        for viewer in set(Parent.GetViewerList()):
            change_points(viewer, MySet.PayoutRate)

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


def change_points(user, amount):
    points = load_points()

    if (points["Users"][user] + amount) < 0:
        return False

    if user in points.keys():
        points["Users"][user] += amount
    else:
        points["Users"][user] = amount

    update_points(points)

    return True


def load_points():
    """Loads the points json."""

    with open(points_json, "r") as json_file:
        points = json.load(json_file, encoding="utf-8-sig")

    return points


def update_points(points_data):
    """Saves the data."""
    with open(points_json, "w+") as json_file:
        points = json.dumps(points_data, json_file, encoding="utf-8-sig")
        json_file.write(points)

    return points
