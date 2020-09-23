#!/usr/bin/python
# -*- coding: utf-8 -*-
# pylint: disable=invalid-name
"""Allows users to vote on options created by the !addvoteoptions command using currency."""
import json
import os, os.path
import operator
import time
import re
import codecs
import glob
import shutil
from io import open

#---------------------------------------
# [Required] Script information
#---------------------------------------
ScriptName = "Vote"
Website = "https://www.twitch.tv/newtc"
Creator = "Newt"
Version = "1.1.0"
Description = "Allows users to vote on options created by the !addvoteoptions command using currency."

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
        # set variables if no settings file
        else:
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
            self.PointName = "points"
            self.SilentAdds = True
            self.CheckOptionsCommand = "!checkoptions"

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
    global active_continuous_adds
    global vote_location
    active_continuous_adds = dict()
    cooldownList = dict()
    m_Active = False
    # Load in saved settings
    MySet = Settings(settingsFile)

    # make the vote location if it doesn't exist
    vote_location = os.path.join(os.path.dirname(__file__), '..\\..\\Twitch\\Votes\\')
    if not os.path.exists(vote_location):
        os.mkdir(os.path.join(os.getcwd(), vote_location))

    if not os.path.exists(os.path.join(vote_location, 'Default')):
        default = os.path.join(vote_location, 'Default')
        os.mkdir(default)

        try:
            # move the previous options that were in vote into the new default folder.
            for option in os.listdir(vote_location):
                # Parent.SendStreamMessage(option)
                if os.path.isfile(os.path.join(vote_location, option)) and option != "active.txt":
                    os.rename(os.path.join(vote_location, option), os.path.join(default, option))

        except WindowsError as e:
            Parent.SendStreamMessage(str(e))

    if not os.path.exists(os.path.join(vote_location, 'active.txt')):
        with open(os.path.join(vote_location, 'active.txt'), 'w+') as active:
            active.write("Default")


    # End of Init
    return


def Execute(data):
    """Required Execute function"""
    global cooldownList
    retVal = ''
    looped = False
    addAmount = 0

    # does nothing if the stream isn't live with the "OnlyLive" setting ticked
    if MySet.OnlyLive and (Parent.IsLive() is False):
        return

    # addvoteoption
    if Parent.HasPermission(data.User, "Caster", "") and data.GetParam(0).lower() == "!addvoteoption":
        # getting game name!
        data_input = data.Message

        if '"' in data_input:
            pattern = '"(.+)"\s*(\d*)'
            respond(data, data_input)
            match = re.search(pattern, data_input)
            game = match.group(1)
            vote_value = match.group(2)
            if not vote_value:
                vote_value = 0
        else:
            data_input = data_input.split(" ")
            vote_value = data.GetParam(data.GetParamCount()-1)

            # decides how to handle the final parameter.
            try:
                vote_value = int(vote_value)
                data_input = data_input[1:-1]
            except ValueError as e:
                vote_value = 0
                data_input = data_input[1:]

            data_input = ' '.join(data_input)
            game = data_input
        with open(os.path.join(get_active_vote_location(), game+'.txt'), 'w+') as new_option:
            # write the last value entered in
            try:
                new_option.write(str(vote_value))
            except IOError as e:
                Parent.SendStreamMessage(str(e))

        if os.path.exists(os.path.join(get_active_vote_location(), game+'.txt')):
            respond(data, 'Successfully created the option %s!' % game)
        else:
            respond(data, "Could not find the file: " + get_active_vote_location()+game+'.txt')

    # deletevoteoption
    if Parent.HasPermission(data.User, "Caster", "") and data.GetParam(0).lower() == "!deletevoteoption":
        # getting game name
        data_input = data.Message
        data_input = data_input.split(" ")
        data_input = data_input[1:]
        data_input = ' '.join(data_input)
        game = data_input
        try:
            os.remove(os.path.join(get_active_vote_location(), game+".txt"))
        except IOError as e:
            Parent.SendStreamMessage("That vote doesn't exist.")
        except WindowsError as e:
            Parent.SendStreamMessage(str(e))

        if not os.path.exists(os.path.join(get_active_vote_location(), game+'.txt')):
            respond(data, 'Successfully deleted the option %s!' % game)
        else:
            respond(data, 'Something went wrong. Let Newt know!')

    # setvoteprofile
    if Parent.HasPermission(data.User, "Caster", "") and data.GetParam(0).lower() == "!setvoteprofile":
        set_active_vote_location(data.GetParam(1).lower())
        retVal += "The campfires shift and blur. A new set of campfires fades into existence."
        respond(data, retVal)

    # deletevoteprofile
    if Parent.HasPermission(data.User, "Caster", "") and data.GetParam(0).lower() == "!deletevoteprofile":
        delete_vote_location(data.GetParam(1).lower())
        retVal += "The old campfire blurs and disappears in front of you. It is no more."
        respond(data, retVal)

    # showvoteprofile
    if data.GetParam(0).lower() == "!showvoteprofile":
        vote_dir = os.path.join(os.path.dirname(__file__), '..\\..\\Twitch\\Votes\\')
        for each in os.listdir(vote_dir):
            if each != "active.txt":
                retVal += each + ', '

        retVal = retVal[:-2]
        respond(data, retVal)

    # !checkoptions
    if data.IsChatMessage() and data.GetParam(0).lower() == MySet.CheckOptionsCommand:
        checkoptions(data)
        return

     # vote
    if data.IsChatMessage() and data.GetParam(0).lower() == MySet.Command.lower():
        if data.GetParamCount() < 2:
            retVal += 'Missing the correct number of parameters. Correct usage is !vote <game> <number of %ss>' \
                      % MySet.PointName
            respond(data, retVal)
            return

        if data.GetParamCount() == 2 and data.GetParam(1).lower() == 'stop':
            if data.UserName.lower() not in active_continuous_adds.keys():
                retVal = 'There is nothing to stop adding to.'
                Parent.SendStreamMessage(retVal)
                return
            else:
                del active_continuous_adds[data.User]
                retVal = 'You have been removed from the continuous add list.'
                Parent.SendStreamMessage(retVal)
                return

        if data.UserName.lower() not in cooldownList.keys() or \
                (data.GetParam(2).lower() == 'stop' or data.GetParam(2).lower() == 'all'):

            # getting game name
            data_input = data.Message
            data_input = data_input.split(" ")
            data_input = data_input[1:-1]
            data_input = ' '.join(data_input)
            game = data_input

            # gets the amount
            data_input = data.Message
            data_input = data_input.split()
            amount = data_input[len(data_input)-1].lower()

            # security checking for data values
            target = security_check(game)

            # check if the file exists
            if not os.path.exists(os.path.join(get_active_vote_location(), target + '.txt')):
                retVal += 'That %s does not exist yet. Recommend it to me instead and I may add it. '%MySet.ResultName
                respond(data, retVal)
                return

            # check if the user is 5attempting to do a !vote <name> all
            if amount.lower() == 'all' and MySet.continuousVoting:
                new_data = (data.User.lower(), target, amount.lower())
                # only add anything if the user isn't on the cooldown list.
                if data.UserName.lower() not in cooldownList.keys():
                    addAmount = min(Parent.GetPoints(data.User), MySet.voteMaximum)
                    if data.User not in active_continuous_adds:
                        active_continuous_adds[data.User.lower()] = new_data
                        retVal += 'You have been added to the continuous add list and are now adding ' + \
                                   MySet.PointName + 's until you run out. '
                        # Parent.SendStreamMessage(response)
                else:
                    # if the user isn't in the add list, add it and add the data
                    if data.User not in active_continuous_adds:
                        active_continuous_adds[data.User.lower()] = new_data
                        response = 'You have been added to the continuous add list and are now adding ' + \
                                   MySet.PointName + 's until you run out. '
                        Parent.SendStreamMessage(response)
                        return
                    #
                    else:
                        active_continuous_adds[data.User.lower()] = new_data
                        response = 'You are already in the the active list. Type "!vote stop" at any time to stop adding. '
                        Parent.SendStreamMessage(response)
                        return

            # check if the user is attempting to stop adding logs automatically
            elif amount == 'stop' and MySet.continuousVoting:
                if data.User in active_continuous_adds:
                    retVal += 'You have been removed from the continuous add list for '+str(target)+' '+str(data.User)
                    Parent.SendStreamWhisper(data.User, retVal)
                    del active_continuous_adds[data.User]
                    return
                else:
                    retVal += 'You aren\'t on the continuous add list.'
                    respond(data, retVal)
                    return

            # add amount
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
                if data.User in active_continuous_adds:
                    del active_continuous_adds[data.User]
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
                seconds_to_completion = int(((addAmount-float(MySet.voteMaximum))/float(MySet.voteMaximum))*int(MySet.cooldownTime))
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
                if data.User not in active_continuous_adds:
                    # store the new data as a tuple for another function to deal with.
                    new_data = (data.User.lower(), target, int(amount) - addAmount)
                    active_continuous_adds[data.User.lower()] = new_data
                    # send users a message to inform them how long logs will add for.
                    if hours_to_completion != 0:
                        retVal += ("You have been added to the continuous add list. " +
                                   MySet.PointName.capitalize() + ' will continue to add for ' +
                                   str(hours_to_completion) + ' hours and ' +
                                   str(minutes_to_completion) + ' minutes and ' +
                                   str(seconds_to_completion) +
                                   ' seconds. Type "!vote stop" to stop voting on this choice. ')
                    elif minutes_to_completion != 0:
                        retVal += ("You have been added to the continuous add list. " +
                                   MySet.PointName.capitalize() + 's will continue to add for ' +
                                   str(minutes_to_completion) + ' minutes and ' +
                                   str(seconds_to_completion) +
                                   ' seconds. Type "!vote stop" to stop voting on this choice. ')
                    else:
                        retVal += ("You have been added to the continuous add list. " +
                                   MySet.PointName.capitalize() + 's will continue to add for ' +
                                   str(seconds_to_completion) +
                                   ' seconds. Type "!vote stop" to stop voting on this choice. ')
            # check the amount is above 0.
            if addAmount <= 0:
                # if they're in the auto add list, remove them from that list
                if data.User in active_continuous_adds:
                    del active_continuous_adds[data.User]
                    retVal += data.User + ' if you got this message, you ran out of ' + MySet.PointName + \
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
                cooldown = addAmount * (float(MySet.cooldownTime)/float(MySet.voteMaximum))
            # add a user to a dictionary when they use the command.
            cooldownList[data.UserName.lower()] = time.time(), cooldown
            
        else:
            # Output the cooldown message
            if data.UserName.lower() in cooldownList.keys():
                seconds_to_wait = get_cooldown(data.User)
                retVal += "You have to wait " + str(int(seconds_to_wait)) + ' more seconds before you can add ' + \
                          MySet.PointName + 's again.'
                respond(data, retVal)
                return

        # sends the final message
        if not looped and not MySet.SilentAdds:
            respond(data, retVal)

    # debug section
    if data.IsChatMessage() and data.GetParam(0).lower() == '!debug':
        if data.GetParam(1) == 'get_cooldown' and MySet.get_cooldown == True:
            retVal = get_cooldown(data.GetParam(2))
            Parent.SendStreamMessage(str(retVal))
        # if data.GetParam(1) == 'get_remaining' and MySet.get_remaining == True:
        #     retVal =

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

        if each.lower() in active_continuous_adds:
            del cooldownList[each]
            # if the users are still present in the viewer list, continue removing logs.
            if each.lower() in set(Parent.GetViewerList()):
                if active_continuous_adds[each.lower()][2] > 0:
                    addUntilDone(active_continuous_adds[each.lower()][0],
                                 active_continuous_adds[each.lower()][1],
                                 active_continuous_adds[each.lower()][2])

            # if the user isn't present
            else:
                Parent.SendStreamWhisper(each.lower(),
                                        'You have been removed from the continuous add list due to leaving the stream.')
            # del activeContinuousAdds[each]
        else:
            del cooldownList[each]

    return

def checkoptions(data):
    """Required Execute function"""
    retVal = ''
    files = {}

    if not get_active_vote_location():
        Parent.SendStreamMessage("Please create the Vote directory.")
        return

    try:
        if len(os.listdir(get_active_vote_location())):
            for filename in os.listdir(get_active_vote_location()):
                #Load in all the file information we need
                with open(os.path.join(get_active_vote_location(), filename), 'r', encoding='utf-8-sig') as f:
                    fileValue = int(f.read())

                    changed_name = filename.split('\\', 1)[-1].split('.')[0]
                    files[changed_name] = fileValue
        else:
            respond(data, "There's nothing in this profile. Add options with !addvoteoption.")
    except WindowsError as e:
        Parent.SendStreamMessage(str(e))

    # sort by the keys https://stackoverflow.com/questions/613183/how-do-i-sort-a-dictionary-by-value
    sorted_files = sorted(files.items(), key=operator.itemgetter(1))

    # add all sorted values to retval and return.
    for x, y in reversed(sorted_files):
        retVal += str(x)

        # if the value is higher than 0, add the value
        if (files[x] > 0):
            retVal += '('+str(y)+' '+MySet.PointName+')'

        retVal += ', '

    retVal = retVal[:-2]

    #sends the final message
    respond(data, retVal)

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

    global active_continuous_adds
    # if the amount left is less than the voteMaximum, vote with the rest of it and remove the user from the list.
    if type(amount) == int:
        if amount < int(MySet.voteMaximum):
            add_amount = amount
            target_amount = 0
            del active_continuous_adds[user]
            Parent.SendStreamWhisper(user, 'You have been removed from the continuous add list. '
                                           'You may now vote again normally.')
        else:
            add_amount = int(MySet.voteMaximum)
            target_amount = amount - int(MySet.voteMaximum)

        add_to_campfire(user, targetgame, add_amount)

        if not MySet.SilentAdds:
            # send the stream response
            Parent.SendStreamWhisper(user, '%s added %i %ss to the %s of %s.'
                                     %(user, add_amount, MySet.PointName, MySet.ResultName, targetgame))
        # if there's more to add, adjust the data value and add it back in
        if target_amount != 0:
            newData = (user, targetgame, target_amount)
            active_continuous_adds[user] = newData

            cooldown = MySet.cooldownTime
            # set the cooldown and save it
            if MySet.dynamicCooldown:
                cooldown = add_amount * (int(MySet.cooldownTime) / int(MySet.voteMaximum))
            # add a user to a dictionary when they use the command.
            cooldownList[user.lower()] = time.time(), cooldown
    elif type(amount) == str:   # This is the ALL vote option
        add_amount = Parent.GetPoints(user)
        if int(MySet.voteMaximum) < add_amount:
            add_amount = int(MySet.voteMaximum)

        add_to_campfire(user, targetgame, add_amount)

        if not MySet.SilentAdds:
            # send the stream response
            Parent.SendStreamWhisper(user, '%s added %i %ss to the %s of %s.'
                                     % (user, add_amount, MySet.PointName, MySet.ResultName, targetgame))

        newData = (user, targetgame, amount)
        active_continuous_adds[user] = newData

        cooldown = MySet.cooldownTime
        # set the cooldown and save it
        if MySet.dynamicCooldown:
            cooldown = add_amount * (int(MySet.cooldownTime) / int(MySet.voteMaximum))
        # add a user to a dictionary when they use the command.

        if not add_amount == 0:
            cooldownList[user.lower()] = time.time(), cooldown
        else:
            Parent.SendStreamMessage(user + " you have run out of logs!")


def add_to_campfire(user, targetgame, amount):
    target_dir = os.path.join(get_active_vote_location(), targetgame + '.txt')
    with open(target_dir, 'r', encoding='utf-8-sig') as vote:
        voteData = int(vote.read().decode('utf-8-sig'))
    voteData += amount
    with open(target_dir, 'w') as vote:
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


def get_active_vote_location():
    vote_location = os.path.join(os.path.dirname(__file__), '..\\..\\Twitch\\Votes\\')
    with open(os.path.join(vote_location,"active.txt"), 'r') as f:
        ret_val = os.path.join(vote_location, f.read())
    return ret_val


def set_active_vote_location(profile):
    """Sets the active vote profile by changing the text file in the vote directory. Makes a new vote profile
    if it doesn't exist yet."""
    vote_location = os.path.join(os.path.dirname(__file__), '..\\..\\Twitch\\Votes\\')
    with open(os.path.join(vote_location, "active.txt"), 'w+') as f:
        f.write(profile)

    # if the new location doesn't exist, create it
    new_location = os.path.join(vote_location, profile)
    if not os.path.exists(new_location):
        os.mkdir(new_location)


def delete_vote_location(profile):
    """Deletes the target vote profile completely."""
    vote_location = os.path.join(os.path.dirname(__file__), '..\\..\\Twitch\\Votes\\')
    target_location = os.path.join(vote_location, profile)

    # clear the vote location if it's currently active
    if get_active_vote_location().split("\\")[-1] == profile.lower():
        with open(os.path.join(vote_location, "active.txt"), 'w+') as f:
            f.write("default")

    try:
        for option in os.listdir(target_location):
            os.remove(os.path.join(target_location, option))
    except WindowsError as e:
        Parent.SendStreamMessage(str(e))

    os.rmdir(target_location)


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
