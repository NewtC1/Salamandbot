#!/usr/bin/python
# -*- coding: utf-8 -*-
# pylint: disable=invalid-name
"""Let viewers pay currency to boost currency payouts
for everyone in chat for x seconds"""
import json
import os
import os.path
import codecs
import sys
from time import time
from io import open

sys.path.append(os.path.dirname(__file__))
from Dragon import Dragon
from Beast import Beast
from Vine import Vine
from Colossus import Colossus
from ShadowBoundBear import ShadowBoundBear
from Spider import Spider
from Ashvine import Ashvine
from Bunny import Bunny
from Thunderjaw import Thunderjaw


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
previous_time = 0

campfireAttackSafetyThreshold = 200 # if there are still shields left, the campfire will not go below this.
shieldHealth = 1000
attackerDead = False
reward_multi = 1.0
rewardMultiCap = 2.0
delay = 0

shield_directory = os.path.join(os.path.dirname(__file__), "..\\..\\Twitch\\shields.txt")
shield_damage_dir = os.path.join(os.path.dirname(__file__), "..\\..\\Twitch\\shieldDamage.txt")
campfire_dir = os.path.join(os.path.dirname(__file__), "..\\..\\Twitch\\flame.txt")

attackers = [Spider(),  # dpm of 15
             ShadowBoundBear(),  # dpm of 30
             Beast(),  # dpm of 35, increases over time
             Colossus(),  # dpm of 140, increases over time
             Dragon(),  # dpm of 200. Reward increases over time, difficult to kill.
             Ashvine(),  # dpm of 30. Increases over time, harder to kill over time, reward increases over time.
             Bunny()] # unspeakably evil

# attackers = [DarkForestCreature(20, 1.0, 5, 1.0, 20, 60)]
# attackers = [Thunderjaw(1, 1.0, 5, 1.0, 600, 50)]
current_attacker = attackers[0]

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
    global previous_time
    global current_attacker
    # Load in saved settings
    MySet = Settings(settingsFile)
    # Set the baseline attacker
    current_attacker = attackers[0]
    # set start values
    previous_time = time()
    delay = current_attacker.getBaseAttackDelay() * current_attacker.getAttackDelayMulti()
    # End of Init
    return


def Execute(data):
    global previous_time
    global attackers
    global attackerDead
    global delay

    # respond("Time until the next attack: " + str(delay - (time()-previous_time)))
    if int(time() - previous_time) > delay:
        # spawn a new attacker if dead
        if attackerDead:
            attacker = attackers[Parent.GetRandom(0, len(attackers))]
            set_new_attacker(attacker)
        else:
            # do an attack action
            attack()
            previous_time = time()

        if not attackerDead:
            delay = current_attacker.getBaseAttackDelay() * current_attacker.getAttackDelayMulti()

    return


def Tick():
    return

# ----------------------------------------
# Helper functions
# ----------------------------------------


def attack():
    global reward_multi
    global shield_directory
    global shield_damage_dir
    global campfire_dir

    damage = int(current_attacker.getBaseAttackStrength() * current_attacker.getAttackStrengthMulti())

    retval = ''
    # open the current shield file
    with open(shield_directory, 'r', encoding='utf-8-sig') as file:
        # read the value
        shield_amount = int(file.read())
    # deal damage to shields are there are still any remaining
    if shield_amount > 0:
        # open the current shield damage file
        with open(shield_damage_dir, 'r', encoding='utf-8-sig') as file:
            # read the value
            shielddamage = int(file.read())
        # increase the shield damage
        shielddamage += damage
        retval += current_attacker.getAttack()

        # respond(shielddamage >= shieldHealth)
        # debug output
        # respond(retval)
        # respond('Shield damage is now at ' + str(shielddamage))
        # if the damage exceeded the current shield health
        if shielddamage >= shieldHealth:
            # reduce the number of shields if damage hit a health threshold
            shield_amount = shield_amount - 1
            # reset the shield damage value to 0
            shielddamage = 0

            # respond('Just before the write')
            with open(shield_directory, 'w', encoding='utf-8-sig') as file:
                # write the newly damaged shield amount
                # respond('Inside the write.')
                file.write(str(shield_amount))
            retval += ' The shield shudders and falls, splintering across the ground. There are now ' + str(shield_amount) + ' shields left.'
            reward_multi = 1.0

        # open and save the new damage
        with open(shield_damage_dir, 'w', encoding='utf-8-sig') as file:
            # respond('Shield damage before writing is ' + str(shielddamage))
            # write the value back
            file.write(str(shielddamage))
            # respond('Shield damage after writing is ' + str(shielddamage))

        # respond('Successful write completed. Moving to counterattack.')

        counter_attack(retval)

    else:
        # deal damage to the main campfire if there aren't any shields
        with open(campfire_dir, 'r', encoding='utf-8-sig') as file:
            # read the value
            campfire = int(file.read())
        campfire = int(campfire - damage)
        # open and save the new damage
        with open(campfire_dir, 'w', encoding='utf-8-sig') as file:
            # write the value back
            file.write(str(campfire))

        retval += current_attacker.getCampfireAttack()

        # if the campfire isn't at 0, counter attack
        if campfire > 0:
            counter_attack(retval)
        # else, begin the fail state
        else:
            enactFailure()


def counter_attack(output):
    retval = output

    global campfireAttackSafetyThreshold
    global current_attacker
    global reward_multi
    global delay

    # The the salamander counter attacks if it has the logs to beat the current attacker.
    with open(campfire_dir, 'r', encoding='utf-8-sig') as file:
        # read the value
        campfire = int(file.read())

    # respond(campfire >= campfireAttackAmount)
    if campfire >= current_attacker.getHealth():
        # open the current shield file
        with open(shield_directory, 'r', encoding='utf-8-sig') as file:
            # read the value
            shieldAmount = file.read()

        # The the salamander counter attacks if it has the logs to beat the current attacker.
        if shieldAmount > 0:
            if (current_attacker.getHealth() + campfireAttackSafetyThreshold) <= campfire:
                # kill the attacker
                retval += ' Flame roars from the Campfire, incinerating the attacker instantly.'
                with open(campfire_dir, 'r', encoding='utf-8-sig') as file:
                    # read the value
                    campfire = int(file.read())
                campfire = campfire - current_attacker.getHealth()
                # open and save the new damage
                with open(campfire_dir, 'w', encoding='utf-8-sig') as file:
                    # write the value back
                    file.write(str(campfire))
                delay = kill_attacker()
                retval += " The attacker has been slain. You gain " + str(
                    current_attacker.getReward()) + " more seconds until the next attack."
                retval += ' Combo counter is at ' + str(reward_multi)
        # if there are no shields left, ignore the safety threshold
        else:
            if current_attacker.getHealth() < campfire:
                # kill the attacker
                retval += ' Flame roars from the Campfire, incinerating the attacker instantly.'
                delay = kill_attacker()
                retval += " The attacker has been slain. You gain " + str(
                    current_attacker.getReward()) + " more seconds until the next attack."
                retval += ' Combo counter is at ' + str(reward_multi)
    respond(retval)


# sets the values of the new attacker
def set_new_attacker(attacker):
    global current_attacker
    global attackerDead

    respond(attacker.getSpawnMessage())
    current_attacker = attacker
    attackerDead = False


def kill_attacker():
    # currentAttacker
    global attackerDead
    global reward_multi
    global delay

    if reward_multi < rewardMultiCap:
        reward_multi += 0.1

    reward = current_attacker.getReward()*reward_multi
    attackerDead = True

    return reward
    # timer = threading.Timer(int(reward * reward_multi), set_new_attacker, args=[attacker])
    # timer.start()


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
