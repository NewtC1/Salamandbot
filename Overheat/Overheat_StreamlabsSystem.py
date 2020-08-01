#!/usr/bin/python
# -*- coding: utf-8 -*-
# pylint: disable=invalid-name
"""Let viewers pay currency to boost currency payouts
for everyone in chat for x seconds"""
import json
import os, os.path
import time
import codecs
from math import ceil

# ---------------------------------------
# [Required] Script information
# ---------------------------------------
ScriptName = "Overheat"
Website = "https://www.twitch.tv/newtc"
Creator = "Newt"
Version = "2.0.0.0"
Description = "Causes the campgrounds setup to overheat, pulling logs at random into the main campfire"

# ---------------------------------------
# Versions
# ---------------------------------------
"""
1.0.0.0 - Initial release
2.0.0.0 - Rebalanced the shields, added explosions, added crits. Tweaked values.
"""
# ---------------------------------------
# Variables
# ---------------------------------------
settingsFile = os.path.join(os.path.dirname(__file__), "settings.json")
queued_crits = 0

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

        else: # set variables if no settings file
            self.Enabled = True
            self.OnlyLive = False
            self.Command = "!overheat"

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
    global shield_directory
    global previous_time
    previous_time = time.clock()
    # Load in saved settings
    MySet = Settings(settingsFile)

    # End of Init
    return


def Execute(data):
    global previous_time
    global MySet
    global queued_crits

    # directories
    campfire_directory = MySet.CampfireDir

    # threshold values
    shield_threshold = int(MySet.ShieldThreshold)
    safety_threshold = int(MySet.SafetyThreshold)
    explosion_threshold = int(MySet.ExplosionThreshold)

    # number of seconds to multiply by
    time_multiplier = int(MySet.DelayMultiplier)

    # attack values
    min_range = int(MySet.MinimumAttack)
    max_range = int(MySet.MaximumAttack)
    shields = get_shields()
    attack_damage = int(Parent.GetRandom(min_range, max_range))  # randomly generate how much to damage the target by
    adjusted_attack_damage = attack_damage - shields
    time_delay = adjusted_attack_damage*time_multiplier
    base_critical_chance = int(MySet.CritChance)

    # if only live is enable, do not run offline
    if MySet.OnlyLive and not Parent.IsLive():
        return

    if int(time.clock() - previous_time) > time_delay:
        if MySet.CritEnabled:
            crit = Parent.GetRandom(0, 100)

            if queued_crits:
                crit = crit - 20 # this increases the chance of a crit by 20%
                queued_crits = queued_crits - 1
        else:
            crit = 101

        if adjusted_attack_damage > 0:
            if crit < base_critical_chance:
                feed(adjusted_attack_damage, data, True)
            else:
                feed(adjusted_attack_damage, data, False)

        previous_time = time.clock()

        creation_fluff = ["Flames scorch the ground around the central bonfire as a twisted " +
                          "tree emerges from it, curling protectively around the Campgrounds.",
                          "Another shield tree ascends, its branches meshing with the ones already around it.",
                          "The Salamander hisses as the purple flames are hidden deeper inside the branches of another "
                          "shield tree."]
        if MySet.Explosions:
            if shield_threshold + safety_threshold < get_campfire() < \
                    ((explosion_threshold - get_shields()) + safety_threshold):

                set_campfire(get_campfire() - shield_threshold)
                set_shields(get_shields()+1)

                Parent.SendStreamMessage(creation_fluff[Parent.GetRandom(0,len(creation_fluff))])

            # if explosions are turned on
            elif get_campfire() >= ((explosion_threshold - get_shields()) + safety_threshold):
                blast_size = get_campfire()/2
                blast_damage = int(blast_size/200)
                if blast_damage > get_shields():
                    blast_damage = get_shields()

                explosion_fluff = ["The Salamander hisses and begins to glow white-hot. "
                                   "The sparks crackle from its spines as a massive explosion ripples"
                                   " out from the Campgrounds. "+str(blast_damage)+" shields were lost in the blast.",
                                   "A blast of heat ripples across the Campgrounds, followed by a much "
                                   "stronger blast of flame. "+str(blast_damage)+" shields were lost in the damage.",
                                   "A pulse of flame ignites several of the trees around the Campfire. The Salamander "
                                   "giggles maliciously, all kindness has left its eyes. "+str(blast_damage)+" shield trees were lost in"
                                   "the blast."]

                Parent.SendStreamMessage(str(explosion_fluff[Parent.GetRandom(0,len(explosion_fluff))]))
                set_shields(get_shields() - blast_damage)
                set_campfire(int(get_campfire()*0.25))
                queued_crits = queued_crits + blast_damage

        else:
            if safety_threshold < get_campfire() - shield_threshold:

                set_campfire(get_campfire() - shield_threshold)
                set_shields(get_shields()+1)

                Parent.SendStreamMessage(creation_fluff[Parent.GetRandom(0,len(creation_fluff))])

    return


def Tick():
    return

# ----------------------------------------
# Helper functions
# ----------------------------------------


def feed(reduce_by, data, is_crit):
    global previous_time
    global MySet
    voteDir = MySet.VoteDir
    campfireDir = MySet.CampfireDir
    retVal = ''
    threshold = 4000
    interval = 10 # for every 10 past threshold, increase the multiplier by 1
    previous_time-=previous_time
    choices = os.listdir(voteDir)
    total_attack= reduce_by

    if is_crit:
        total_attack = total_attack*4

    # add multiple copies of choices with higher values
    for file in os.listdir(voteDir):
        with open(voteDir + file, 'r') as f:
            option = int(f.read().decode('utf-8-sig'))

        if option >= (threshold+interval):
            multiplier = (option-threshold)/interval

            for i in range(multiplier):
                choices.append(file)

    log(choices)

    choice = choices[Parent.GetRandom(0,len(choices))]
    name = choice # choose a random file from within the directory
    game_name = name.split('.')[0]

    with open(voteDir + name, 'r') as file: # open the random file
        filedata = int(file.read().decode('utf-8-sig'))

    # make sure it has enough logs to reduce by that much
    if total_attack > filedata:
        # if a crit occurs, delete the vote option entirely
        if is_crit:
            crit_consume_fluff = ["The flames of the Campgrounds voraciously devour on %s's log pile. " \
                         "When it is done, nothing remains. " \
                         "The story has been consumed entirely."% game_name,
                         "A pillar of flame lances from the center of the Campgrounds to %s's logpile. "
                         "When it is done, not a single splinter remains of the story." % game_name,
                         "The eyes of the Salamander travel to %s's logpile. Seconds later, vines of lilac fire blossom"
                         " forth and enshroud the story. When the smoke clears, nothing remains." % game_name
                         ]
            retVal += crit_consume_fluff[Parent.GetRandom(0,len(crit_consume_fluff))]
            os.remove(voteDir+name)
            set_campfire(get_campfire() + filedata)
        else:
            failure_fluff = ['The questing tendrils of salamander flame pass up ' + game_name + \
                             '; It is too small to sate it\'s appetite.']
            retVal += failure_fluff[Parent.GetRandom(0,len(failure_fluff))]

    else:
        filedata = filedata - total_attack
        if is_crit:
            feed_fluff = ["Purple fire sprouts from the campfire and sweeps between the other fires, "
                          "eventually landing on the fire of " + game_name +
                          ". The pillar of flame rages and incinerates %i "
                          "logs from the that fire." % total_attack,
                          "Fire arches from the central campfire and dives onto " + game_name +
                          ". %i logs are consumed." % total_attack
                          ]
            retVal += feed_fluff[Parent.GetRandom(0,len(feed_fluff))]
        else:
            retVal += 'The salamander flame gorges itself on ' + game_name + '\'s log pile, consuming ' + \
                      str(total_attack) + ' logs. It is sated... for now.'

        # Write the reduced log count to the file.
        with open(voteDir + name, 'w+') as file:
            file.write(str(filedata))

        set_campfire(get_campfire() + total_attack)

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


def get_campfire():
    campfire_directory = os.path.join(os.path.dirname(__file__), '../../Twitch/flame.txt')
    with open(campfire_directory, 'r') as f:
        campfire = int(f.read().decode('utf-8-sig'))

    return campfire


def set_campfire(value):
    campfire_directory = os.path.join(os.path.dirname(__file__), '../../Twitch/flame.txt')
    with open(campfire_directory, 'w+') as f:
        f.write(str(value))


def get_shields():
    shield_directory = os.path.join(os.path.dirname(__file__), '../../Twitch/shields.txt')
    with open(shield_directory, 'r') as f:
        shields = int(f.read().decode('utf-8-sig'))

    return shields


def set_shields(value):
    shield_directory = os.path.join(os.path.dirname(__file__), '../../Twitch/shields.txt')
    with open(shield_directory, 'w+') as f:
        f.write(str(value))


def log(value):
    with open("log.txt", 'w+') as f:
        f.write(str(value))