#!/usr/bin/python
# -*- coding: utf-8 -*-
# pylint: disable=invalid-name
"""Allows users to vote on options created by the !addvoteoptions command using currency."""
import json
import os, os.path
import operator
import time
import codecs
from io import open

#---------------------------------------
# [Required] Script information
#---------------------------------------
ScriptName = "Vote"
Website = "https://www.twitch.tv/newtc"
Creator = "Newt"
Version = "1.1.0"
Description = "Allows users to vote on options created by the !addvoteoptions command using currency."

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
            self.Command = "!vote"
            self.AntiSnipe = False
            self.cooldownTime = 600
            self.voteMaximum = 100
            self.dynamicCooldown = False
            self.continuousVoting = False
            self.christmas = False
            self.get_cooldown = False
            self.PointsName = "points"
            self.SilentAdds = True
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
    global cooldownList
    global activeContinuousAdds
    activeContinuousAdds = dict()
    cooldownList = dict()
    m_Active = False
    # Load in saved settings
    MySet = Settings(settingsFile)

    # End of Init
    return


def Execute(data):
    """Required Execute function"""
    global cooldownList
    voteLocation = os.path.join(os.path.dirname(__file__), '../../Twitch/Votes/')
    retVal = ''
    looped = False
    addAmount = 0
    if data.User in activeContinuousAdds:
        looped = True

    # does nothing if the stream isn't live with the "OnlyLive" setting ticked
    if MySet.OnlyLive and (Parent.IsLive() is False):
        return

    if data.IsChatMessage() and data.GetParam(0).lower() == MySet.Command.lower():
        if data.GetParamCount() == 2 and data.GetParam(1).lower() == 'stop':
            if data.UserName.lower() not in activeContinuousAdds.keys():
                retVal = 'There is nothing to stop adding to.'
                Parent.SendStreamMessage(data.User, retVal)
                return
            else:
                del activeContinuousAdds[data.User]
                retVal = 'You have been removed from the continuous add list.'
                Parent.SendStreamWhisper(data.User, retVal)
                return

        if (data.GetParamCount() > 2) and ((data.UserName.lower() not in cooldownList.keys())
                                            or (data.GetParam(2).lower() == 'stop'
                                            or data.GetParam(2).lower() == 'all')):

            data_input = data.Message
            data_input = data_input.split(" ")
            data_input = data_input[1:-1]
            data_input = ' '.join(data_input)
            game = data_input

            # gets the last element of the array
            data_input = data.Message
            data_input = data_input.split()
            amount = data_input[len(data_input)-1].lower()

            # security checking for data values
            target = security_check(game)

            # check if the file exists
            if not os.path.exists(voteLocation + target + '.txt'):
                retVal += 'That %s does not exist yet. Recommend it to me instead and I may add it. '%MySet.ResultName
                respond(data, retVal)
                return

            # check if the user is 5attempting to do a !vote <name> all
            if amount.lower() == 'all' and MySet.continuousVoting:
                # only add anything if the user isn't on the cooldown list.
                if data.UserName.lower() not in cooldownList.keys():
                    addAmount = min(Parent.GetPoints(data.User), MySet.voteMaximum)
                    if data.User not in activeContinuousAdds:
                        activeContinuousAdds[data.User.lower()] = data
                        response = 'You have been added to the continuous add list and are now adding ' + \
                                   MySet.PointName + 's until you run out. '
                        Parent.SendStreamWhisper(data.User, response)
                else:
                    # if the user isn't in the add list, add it and add the data
                    if data.User not in activeContinuousAdds:
                        activeContinuousAdds[data.User.lower()] = data
                        response = 'You have been added to the continuous add list and are now adding ' + \
                                   MySet.PointName + 's until you run out. '
                        Parent.SendStreamWhisper(data.User, response)
                        return
                    else:
                        activeContinuousAdds[data.User.lower()] = data
                        response = 'You are already in the the active list. Type "!vote stop" at any time to stop adding. '
                        Parent.SendStreamWhisper(data.User, response)
                        return

            # check if the user is attempting to stop adding logs automatically
            elif amount == 'stop' and MySet.continuousVoting:
                if data.User in activeContinuousAdds:
                    retVal += 'You have been removed from the continuous add list for '+str(game)+' '+str(data.User)
                    Parent.SendStreamWhisper(data.User, retVal)
                    del activeContinuousAdds[data.User]
                    return
                else:
                    retVal += 'You aren\'t on the continuous add list.'
                    respond(data, retVal)
                    return
            else:
                # verify the amount to add is actually an integer
                try:
                    addAmount = int(amount)
                except ValueError as ve:
                    retVal += 'That isn\'t an integer. Please vote using an integer.'
                    respond(data, retVal)
                    return

            # check the amount is not higher than the user can add.
            if addAmount > Parent.GetPoints(data.User):
                retVal += 'Your %s pales in comparison to the amount you wish to add, %s. You only have %s. Wait to gather more.'\
                          %(MySet.ResultName, data.User, str(Parent.GetPoints(data.User)))
                respond(data, retVal)

                # if they're in the auto add list, remove them from that list
                if data.User in activeContinuousAdds:
                    del activeContinuousAdds[data.User]
                return

            # if users can add all the time, then ignore cooldowns and just add it
            if not MySet.AntiSnipe and addAmount >= 0:
                # get the number of points afterwards
                result = add_to_campfire(data.User, target, addAmount)
                retVal += "%s added %i to %s's %s. There are now %i %ss in the %s. " % (
                data.User, addAmount, target, MySet.ResultName, result, MySet.PointName, MySet.ResultName)
                respond(data, retVal)
                return


            # If the user tries to add more than the set maximum, change the amount to add to be that maximum.
            if addAmount > int(MySet.voteMaximum):
                # get the number of seconds this will take to finish
                seconds_to_completion = (addAmount-int(MySet.voteMaximum))/int(MySet.voteMaximum)*int(MySet.cooldownTime)
                minutes_to_completion = 0
                hours_to_completion = 0
                if seconds_to_completion > 60:
                    minutes_to_completion = seconds_to_completion/60
                    seconds_to_completion = seconds_to_completion%60
                if minutes_to_completion > 60:
                    hours_to_completion = minutes_to_completion/60
                    minutes_to_completion = minutes_to_completion%60
                retVal += 'Currently the maximum number of %ss is %s. Removing this amount from your pool. '\
                          %(MySet.PointName, MySet.voteMaximum)

                addAmount = int(MySet.voteMaximum)
                # add users to the continuous add list and create a separate dictionary that keeps track of their cap
                if data.User not in activeContinuousAdds:
                    # store the new data as a tuple for another function to deal with.
                    newData = (data.User.lower(), game, int(amount) - addAmount)
                    activeContinuousAdds[data.User.lower()] = newData
                    addAmount/int(MySet.voteMaximum)
                    # send users a message to inform them how long logs will add for.
                    if hours_to_completion != 0:
                        Parent.SendStreamMessage("You have been added to the continuous add list. " +
                                                MySet.PointName.capitalize() + ' will continue to add for ' +
                                                str(hours_to_completion) + ' hours and ' +
                                                str(minutes_to_completion) + ' minutes and ' +
                                                str(seconds_to_completion) +
                                                ' seconds. Type "!vote stop" to stop voting on this choice.')
                    elif minutes_to_completion != 0:
                        Parent.SendStreamMessage("You have been added to the continuous add list. " +
                                                MySet.PointName.capitalize() + 's will continue to add for ' +
                                                str(minutes_to_completion) + ' minutes and ' +
                                                str(seconds_to_completion) +
                                                ' seconds. Type "!vote stop" to stop voting on this choice.')
                    else:
                        Parent.SendStreamMessage("You have been added to the continuous add list. " +
                                                MySet.PointName.capitalize() + 's will continue to add for ' +
                                                str(seconds_to_completion) +
                                                ' seconds. Type "!vote stop" to stop voting on this choice.')

            # check the amount is above 0.
            if addAmount <= 0:
                # if they're in the auto add list, remove them from that list
                if data.User in activeContinuousAdds:
                    del activeContinuousAdds[data.User]
                    retVal += ' If you got this message, you ran out of ' + MySet.PointName + \
                              's and have been removed from auto add.'
                else:
                    retVal = '%s, %i is less than or equal to 0. Please offer at least one %ss.' \
                             % (data.User, addAmount, MySet.PointName)

                respond(data, retVal)
                return

            # add it to the campfire
            result = add_to_campfire(data.User, target, addAmount)

            # output the result to the user
            retVal += "%s added %i to %s's %s. There are now %i %ss in the %s. "\
                      %(data.User, addAmount, target, MySet.ResultName, result, MySet.PointName, MySet.ResultName)

            cooldown = MySet.cooldownTime
            # set the cooldown and save it
            if MySet.dynamicCooldown:
                cooldown = addAmount * (int(MySet.cooldownTime)/int(MySet.voteMaximum))
            # add a user to a dictionary when they use the command.
            cooldownList[data.UserName.lower()] = time.time(), cooldown
            
        else:
            # Output the cooldown message
            if data.UserName.lower() in cooldownList.keys():
                seconds_to_wait = get_cooldown(data.User)
                retVal += "You have to wait " + str(int(seconds_to_wait)) + ' more seconds before you can add ' + \
                          MySet.PointName + 's again.'
            else:
                retVal += 'Missing the correct number of parameters. Correct usage is !vote <game> <number of %ss>'\
                          % MySet.PointName
                
        # sends the final message
        if not looped and not MySet.SilentAdds:
            respond(data, retVal)

    # debug section
    if data.IsChatMessage() and data.GetParam(0).lower() == '!debug':
        if data.GetParam(1) == 'get_cooldown' and MySet.get_cooldown == True:
            retVal = get_cooldown(data.GetParam(2))
            Parent.SendStreamMessage(str(retVal))

    return

def Tick():
    """Required tick function"""
    removals = []
    global cooldownList
    # if you're on the cooldown list
    for x in cooldownList:
        # if dynamic cooldown is enabled
        if MySet.dynamicCooldown:
            if time.time() - cooldownList[x][1] > cooldownList[x][0]:
                removals.append(x)
        elif time.time() - float(MySet.cooldownTime) > cooldownList[x][0]:
            removals.append(x)
    
    # remove the people who have had their cooldowns time out.
    for each in removals:
        # if it's in the list of continues adds, resubmit the command that started it.

        if each.lower() in activeContinuousAdds:
            del cooldownList[each]
            # if the users are still present in the viewer list, continue removing logs.
            if each.lower() in set(Parent.GetViewerList()):
                data = activeContinuousAdds[each.lower()]

                # if it's a tuple, it's only in the list due to add until amount
                if type(data) == tuple:
                    addUntilDone(activeContinuousAdds[each.lower()][0],
                                 activeContinuousAdds[each.lower()][1],
                                 activeContinuousAdds[each.lower()][2])
                else:
                    amount = activeContinuousAdds[each.lower()].GetParam(2).lower()
                    target = activeContinuousAdds[each.lower()].GetParam(1).lower()
                    if amount == 'all':
                        Execute(activeContinuousAdds[each.lower()])
                    else:
                        addUntilDone(each.lower(), target, int(amount))

            # if the user isn't present
            else:
                Parent.SendStreamWhisper(each.lower(),
                                        'You have been removed from the continuous add list due to leaving the stream.')
            # del activeContinuousAdds[each]
        else:
            del cooldownList[each]

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

def security_check(input):
    target = input
    if '\\' in target:
        target = target.split('\\')[-1]
    if '/' in target:
        target = target.split('/')[-1]
    return target


# helper function that seperates values from the data Datatype
def addUntilDone(user, targetgame, amount):
    voteLocation = '../../Twitch/Votes/'

    global activeContinuousAdds
    # if the amount left is less than the voteMaximum, vote with the rest of it and remove the user from the list.
    if amount < int(MySet.voteMaximum):
        addAmount = amount
        targetAmount = 0
        del activeContinuousAdds[user]
        Parent.SendStreamWhisper(user, 'You have been removed from the continuous add list. You may now vote again normally.')
    else:
        addAmount = int(MySet.voteMaximum)
        targetAmount = amount - int(MySet.voteMaximum)

    add_to_campfire(user, targetgame, addAmount)

    if not MySet.SilentAdds:
        # send the stream response
        Parent.SendStreamMessage('%s added %i %ss to the %s of %s.'
                                 %(user, addAmount, MySet.PointName, MySet.ResultName, targetgame))
    # if there's more to add, adjust the data value and add it back in
    if targetAmount != 0:
        newData = (user, targetgame, targetAmount)
        activeContinuousAdds[user] = newData

        cooldown = MySet.cooldownTime
        # set the cooldown and save it
        if MySet.dynamicCooldown:
            cooldown = addAmount * (int(MySet.cooldownTime) / int(MySet.voteMaximum))
        # add a user to a dictionary when they use the command.
        cooldownList[user.lower()] = time.time(), cooldown


def add_to_campfire(user, targetgame, amount):
    voteLocation = os.path.join(os.path.dirname(__file__), '../../Twitch/Votes/')
    with open(voteLocation + targetgame + '.txt', 'r', encoding='utf-8-sig') as vote:
        voteData = int(vote.read().decode('utf-8-sig'))
    voteData += amount
    with open(voteLocation + targetgame + '.txt', 'w') as vote:
        vote.write(str(voteData))
    Parent.RemovePoints(user, user, amount)

    if (MySet.christmas == True):
        add_to_givers(user, amount)

    return voteData


def add_to_givers(user, amount):
    giverLocation = os.path.join(os.path.dirname(__file__), '../../Twitch/Givers/' + user)

    if not (os.path.exists(giverLocation + '.txt')):
        return
    with open(giverLocation + '.txt', 'r', encoding='utf-8-sig') as vote:
        voteData = int(vote.read().decode('utf-8-sig'))
    voteData += amount
    with open(giverLocation + '.txt', 'w') as vote:
        vote.write(str(voteData))


def get_cooldown(user):
    global cooldownList

    # if the user isn't on cooldown, return 0
    if user.lower() not in cooldownList.keys():
        return 0.0

    # how long has it been since we voted?
    time_since_vote = (time.time() - cooldownList[user.lower()][0])

    # returns how much time is left
    if MySet.dynamicCooldown:
        return cooldownList[user.lower()][1] - time_since_vote
    else:
        return float(MySet.cooldownTime) - time_since_vote
