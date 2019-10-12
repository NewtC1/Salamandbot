#!/usr/bin/python
# -*- coding: utf-8 -*-
# pylint: disable=invalid-name
"""Let viewers pay currency to boost currency payouts
for everyone in chat for x seconds"""
import json
import os, os.path
import time
import codecs
import glob

#---------------------------------------
# [Required] Script information
#---------------------------------------
ScriptName = "NextGame"
Website = "https://www.twitch.tv/newtc"
Creator = "Newt"
Version = "1.0.0.0"
Description = "Displays what the next game played will be based on votes."

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
            self.Command = "!nextGame"
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

    # End of Init
    return

def Execute(data):
	"""Required Execute function"""
	currentMax = 0
	nextGame = 'missingFile'

	if data.IsChatMessage() and data.GetParam(0).lower() == MySet.Command.lower():
		
		for filename in glob.glob('Services/Twitch/Votes/*.txt'):
			#Load in all the file information we need
			f = codecs.open(filename, 'r', encoding='utf-8-sig')
			fileValue = int(f.read())
			
			#Check if the next file has a higher value.
			if fileValue > currentMax:
				currentMax = fileValue
				nextGame = filename
			
			f.close()
		
		#returns the next game
		nextGame = nextGame.split('\\', 1)[-1]
		nextGame = nextGame.split('.')[0]
		retVal = 'The next game is ' + nextGame + ' with ' + str(currentMax) + ' logs!'
		
		#sends the final message
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
	return

def Tick():
    """Required tick function"""
    return
