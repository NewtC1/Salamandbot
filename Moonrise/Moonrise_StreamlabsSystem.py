#!/usr/bin/python
# -*- coding: utf-8 -*-
# pylint: disable=invalid-name
"""Let viewers pay currency to boost currency payouts
for everyone in chat for x seconds"""
import json
import os
import os.path
import codecs
import threading
import io
import sys
sys.path.append(os.path.dirname(__file__))
from DarkForestCreature import DarkForestCreature
from Dragon import Dragon
from Beast import Beast
from Vine import Vine
from Colossus import Colossus
from ShadowBoundBear import ShadowBoundBear
from Spider import Spider
from Ashvine import Ashvine
from Bunny import Bunny


# ---------------------------------------
# [Required] Script information
# ---------------------------------------
ScriptName = "Moonrise"
Website = "https://www.twitch.tv/newtc"
Creator = "Newt"
Version = "1.0.0.0"
Description = "Starts the moonrise event, which attacks the campfire until turned off or a climactic event happens"

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
timerActive = 0

campfireAttackSafetyThreshold = 200 # if there are still shields left, the campfire will not go below this.
shieldHealth = 800
attackerDead = False
rewardMulti = 1.0
rewardMultiCap = 2.0

shieldDir = "D:/Program Files/Streamlabs Chatbot/Services/Twitch/shields.txt"
shieldDamageDir = "D:/Program Files/Streamlabs Chatbot/Services/Twitch/shieldDamage.txt"
campfireDir = "D:/Program Files/Streamlabs Chatbot/Services/Twitch/flame.txt"

attackers = [Vine(60, 1.0, 5, 1.0, 20, 120), # dpm of 5
             Vine(60, 1.0, 5, 1.0, 20, 120),
             Vine(60, 1.0, 5, 1.0, 20, 120),
             Vine(60, 1.0, 5, 1.0, 20, 120),
             Vine(60, 1.0, 5, 1.0, 20, 120),
             Vine(60, 1.0, 5, 1.0, 20, 120),
             Vine(60, 1.0, 5, 1.0, 20, 120),
             Vine(60, 1.0, 5, 1.0, 20, 120),
             Vine(60, 1.0, 5, 1.0, 20, 120),
             Vine(60, 1.0, 5, 1.0, 20, 120),
             Spider(60, 1.0, 15, 1.0, 100, 240), # dpm of 15
             Spider(60, 1.0, 15, 1.0, 100, 240),
             Spider(60, 1.0, 15, 1.0, 100, 240),
             Spider(60, 1.0, 15, 1.0, 100, 240),
             Spider(60, 1.0, 15, 1.0, 100, 240),
             Spider(60, 1.0, 15, 1.0, 100, 240),
             ShadowBoundBear(120, 1.0, 60, 1.0, 300, 300), # dpm of 30
             ShadowBoundBear(120, 1.0, 60, 1.0, 300, 300),
             ShadowBoundBear(120, 1.0, 60, 1.0, 300, 300),
             ShadowBoundBear(120, 1.0, 60, 1.0, 300, 300),
             Beast(120, 1.0, 70, 1.0, 100, 300), # dpm of 35, increases over time
             Beast(120, 1.0, 70, 1.0, 100, 300),
             Colossus(60, 5.0, 700, 1.0, 2000, 1800), # dpm of 140, increases over time
             Colossus(60, 5.0, 700, 1.0, 2000, 1800),
             Dragon(300, 1.0, 1000, 1.0, 2000, 3600), # dpm of 200. Reward increases over time, difficult to kill.
             Ashvine(60, 1.0, 30, 1.0, 60, 50), # dpm of 30. Increases over time, harder to kill over time, reward increases over time.
             Bunny(0,0,0,0,0, 1800)] # unspeakably evil
#attackers = [DarkForestCreature(20, 1.0, 5, 1.0, 20, 60)]
currentAttacker = attackers[0]

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

        else: #set variables if no settings file
            self.Enabled = True
            self.OnlyLive = False
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
    # Globals
    global MySet
    global m_Active
    global timerActive
    global currentAttacker
    timerActive = 0
    m_Active = False
    # Load in saved settings
    MySet = Settings(settingsFile)
    # Set the baseline attacker
    currentAttacker = attackers[0]
    # End of Init
    return


def Execute(data):
    global timerActive
    delay = currentAttacker.getBaseAttackDelay() * currentAttacker.getAttackDelayMulti()
    
    # Parent.SendStreamMessage("Timers active: " + str(timerActive))
    # if there isn't an active timer and the stream is live
    if Parent.IsLive() is True:
        if timerActive < 1:
            if not attackerDead:
                # respond('Starting attack')
                timer = threading.Timer(delay, attack, args=[data])
                timer.start()
                timerActive = timerActive + 1
                # Parent.SendStreamMessage("Timers active: " + str(timerActive))
    return


def Tick():
    return

# ----------------------------------------
# Helper functions
# ----------------------------------------


def attack(data):
    global rewardMulti

    damage = int(currentAttacker.getBaseAttackStrength() * currentAttacker.getAttackStrengthMulti())

    retval = ''
    # open the current shield file
    with io.open(shieldDir, 'r', encoding='utf-8-sig') as file:
        # read the value
        shieldAmount = int(file.read())
    # respond('Shield amount is ' + str(shieldAmount))
    # deal damage to shields are there are still any remaining
    if shieldAmount > 0:
        # open the current shield damage file
        with io.open(shieldDamageDir, 'r', encoding='utf-8-sig') as file:
            # read the value
            # respond('opening shield damage')
            shielddamage = int(file.read())
            # respond('Shield Damage is ' + str(shielddamage))
        # increase the shield damage
        shielddamage += damage
        retval += currentAttacker.getAttack()

        # respond(shielddamage >= shieldHealth)
        # debug output
        # respond(retval)
        # respond('Shield damage is now at ' + str(shielddamage))
        # if the damage exceeded the current shield health
        if shielddamage >= shieldHealth:
            # reduce the number of shields if damage hit a health threshold
            shieldAmount = shieldAmount - 1
            # reset the shield damage value to 0
            shielddamage = 0

            # respond('Just before the write')
            with io.open(shieldDir, 'w', encoding='utf-8-sig') as file:
                # write the newly damaged shield amount
                # respond('Inside the write.')
                file.write(str(shieldAmount))
            retval += ' The shield shudders and falls, splintering across the ground. There are now ' + str(shieldAmount) + ' shields left.'
            rewardMulti = 1.0

        # open and save the new damage
        with io.open(shieldDamageDir, 'w', encoding='utf-8-sig') as file:
            # respond('Shield damage before writing is ' + str(shielddamage))
            # write the value back
            file.write(str(shielddamage))
            # respond('Shield damage after writing is ' + str(shielddamage))

        # respond('Successful write completed. Moving to counterattack.')

        counterAttack(retval)

    else:
        # deal damage to the main campfire if there aren't any shields
        with io.open(campfireDir, 'r', encoding='utf-8-sig') as file:
            # read the value
            campfire = int(file.read())
        campfire = int(campfire - damage)
        # open and save the new damage
        with io.open(campfireDir, 'w', encoding='utf-8-sig') as file:
            # write the value back
            file.write(str(campfire))

        retval += currentAttacker.getCampfireAttack()

        # if the campfire isn't at 0, counter attack
        if campfire > 0:
            counterAttack(retval)
        # else, begin the fail state
        else:
            enactFailure()


def counterAttack(output):
    retval = output

    global campfireAttackSafetyThreshold
    global timerActive
    global currentAttacker
    global rewardMulti

    # even if it does anything, start the next attack cycle
    timerActive -= 1

    # The the salamander counter attacks if it has the logs to beat the current attacker.
    with io.open(campfireDir, 'r', encoding='utf-8-sig') as file:
        # read the value
        campfire = int(file.read())

    # respond(campfire >= campfireAttackAmount)
    if campfire >= currentAttacker.getHealth():
        # open the current shield file
        with io.open(shieldDir, 'r', encoding='utf-8-sig') as file:
            # read the value
            shieldAmount = file.read()

        # The the salamander counter attacks if it has the logs to beat the current attacker.
        if shieldAmount > 0:
            if (currentAttacker.getHealth() + campfireAttackSafetyThreshold) <= campfire:
                # kill the attacker
                retval += ' Flame roars from the Campfire, incinerating the attacker instantly.'
                with io.open(campfireDir, 'r', encoding='utf-8-sig') as file:
                    # read the value
                    campfire = int(file.read())
                campfire = campfire - currentAttacker.getHealth()
                # open and save the new damage
                with io.open(campfireDir, 'w', encoding='utf-8-sig') as file:
                    # write the value back
                    file.write(str(campfire))
                killAttacker()
                retval += ' Combo counter is at ' + str(rewardMulti)
        # if there are no shields left, ignore the safety threshold
        else:
            if currentAttacker.getHealth() < campfire:
                # kill the attacker
                retval += ' Flame roars from the Campfire, incinerating the attacker instantly.'
                killAttacker()
                retval += ' Combo counter is at ' + str(rewardMulti)
    respond(retval)


# sets the values of the new attacker
def setNewAttacker(attacker):
    # anti-Malarthi globals
    global currentAttacker
    global attackerDead

    respond(attacker.getSpawnMessage())
    currentAttacker = attacker
    attackerDead = False


def killAttacker():
    # currentAttacker
    global attackerDead
    global rewardMulti
    reward = currentAttacker.getReward()
    attackerDead = True
    attacker = attackers[Parent.GetRandom(0,len(attackers))]

    # if rewardMulti < rewardMultiCap:
    rewardMulti += 0.1

    timer = threading.Timer(int(reward * rewardMulti), setNewAttacker, args=[attacker])
    timer.start()

def respond(output):
    retVal = output
    Parent.SendStreamMessage(str(retVal))


# what happens if the fire goes out?
def enactFailure():
    respond("""
            With a last gasp, the central bonfire consumes all of the remaining logs in the entire Campgrounds and fizzles out.
            In darkness, a pregnant silence falls. 
            One second. Two seconds. 
            Then Soil screams. 
            Moonflowers erupt from the ashes, then the dirt around the ashes. 
            In seconds, the darkness is obliterated by death's light. 
            The space around Soil ripples. 
            A silver orb shines between her horns, and a kopesh of moonlight is embraced in her hands. 
            Soraviel, Moon Goddess of Death and Rebirth, makes her presence known. 
            """)