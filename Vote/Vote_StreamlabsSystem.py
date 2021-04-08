#!/usr/bin/python
# -*- coding: utf-8 -*-
# pylint: disable=invalid-name
"""Allows users to vote on options created by the !addvoteoptions command using currency."""
import json
import os, os.path
import operator
import time
import datetime
import re
import codecs
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
shieldsFile = os.path.join(os.path.dirname(__file__), '../../Twitch/shields.txt')
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
            self.Decay = False
            self.Decay_Days = 7
            self.Decay_Amount = 1

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
    global cooldown_list
    global active_continuous_adds
    global vote_location
    global stream_is_live
    active_continuous_adds = dict()
    cooldown_list = dict()
    m_Active = False
    # Load in saved settings
    MySet = Settings(settingsFile)
    stream_is_live = Parent.IsLive()

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

    # generates the vote.json from pre-existing votes at the start.
    if not os.path.exists(os.path.join(vote_location, 'vote.json')):
        os.system("python " + os.path.join(os.path.dirname(__file__), 'json_converter.py'))

    # decay
    if MySet.Decay:
        if stream_is_live:
            decay()

    Parent.Log("Vote Initialization","Creating backup vote list.")
    if not os.path.exists("Backups"):
        os.mkdir("Backups")
    Parent.Log("Vote Initialization", "Backup created in: " + os.getcwd())
    shutil.copyfile(os.path.join(vote_location, 'vote.json'), "Backups\\Logs_" + str(time.time()) + ".json")

    # End of Init
    return


def Execute(data):
    """Required Execute function"""
    global cooldown_list
    return_value = ''
    sender_user_id = ""
    sender_user_display = ""
    if data.IsFromTwitch():
        sender_user_id = data.UserName.lower()
        sender_user_display = data.UserName
    elif data.IsFromYoutube() or data.IsFromDiscord():
        sender_user_id = data.User
        sender_user_display = data.UserName


    # does nothing if the stream isn't live with the "OnlyLive" setting ticked
    if MySet.OnlyLive and (Parent.IsLive() is False):
        return

    # addvoteoption
    if Parent.HasPermission(sender_user_id, "Caster", "") and data.GetParam(0).lower() == "!addvoteoption":
        # getting game name!
        data_input = data.Message

        if '"' in data_input:
            pattern = '"(.+)"\s*(\d*)'
            # respond(data, data_input)
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

        add_vote_option(game, vote_value)
        vote_data = get_vote_data()
        if game in vote_data["Profiles"][get_active_profile()].keys():
            respond(data, 'Successfully created the option %s!' % game)
        else:
            respond(data, "Something went wrong. Let Newt know!")

    # deletevoteoption
    if Parent.HasPermission(sender_user_id, "Caster", "") and data.GetParam(0).lower() == "!deletevoteoption":
        # getting game name
        data_input = data.Message
        data_input = data_input.split(" ")
        data_input = data_input[1:]
        data_input = ' '.join(data_input)
        game = data_input

        vote_data = get_vote_data()
        del vote_data["Profiles"][get_active_profile()][game]
        update_vote_data(vote_data)
        if game in vote_data["Profiles"][get_active_profile()].keys():
            respond(data, 'Successfully deleted the option %s!' % game)
        else:
            respond(data, 'Something went wrong. Let Newt know!')

    # setvoteprofile
    if Parent.HasPermission(sender_user_id, "Caster", "") and data.GetParam(0).lower() == "!setvoteprofile":
        set_active_vote_profile(data.GetParam(1))
        return_value += "The campfires shift and blur. A new set of campfires fades into existence."
        respond(data, return_value)

    # deletevoteprofile
    if Parent.HasPermission(sender_user_id, "Caster", "") and data.GetParam(0).lower() == "!deletevoteprofile":
        delete_vote_location(data.GetParam(1).lower())
        return_value += "The old campfire blurs and disappears in front of you. It is no more."
        respond(data, return_value)

    # showvoteprofile
    if data.GetParam(0).lower() == ("!showvoteprofile" or "!showvoteprofiles" or "!displayvoteprofile"):
        vote_data = get_vote_data()
        for profile in vote_data["Profiles"].keys():
            return_value += profile + ', '

        return_value = return_value[:-2]
        respond(data, return_value)

    # !checkoptions
    if data.IsChatMessage() and data.GetParam(0).lower() == MySet.CheckOptionsCommand:
        check_options(data)
        return

    # !whittle
    if data.IsChatMessage() and data.GetParam(0).lower() == "!whittle":
        return

    # vote
    if data.IsChatMessage() and data.GetParam(0).lower() == MySet.Command.lower():
        if data.GetParamCount() < 2:
            return_value += 'Missing the correct number of parameters. Correct usage is !vote <game> <number of %ss>' \
                      % MySet.PointName
            respond(data, return_value)
            return

        if data.GetParamCount() == 2 and data.GetParam(1).lower() == 'stop':
            if sender_user_id not in active_continuous_adds.keys():
                return_value = 'There is nothing to stop adding to.'
                Parent.SendStreamMessage(return_value)
                return
            else:
                del active_continuous_adds[sender_user_id]
                return_value = 'You have been removed from the continuous add list.'
                Parent.SendStreamMessage(return_value)
                return

        # getting game name
        data_input = data.Message
        data_input = data_input.split(" ")
        data_input = data_input[1:-1]
        data_input = ' '.join(data_input)
        game = data_input

        # gets the amounts
        data_input = data.Message
        data_input = data_input.split()
        amount = data_input[len(data_input)-1].lower()

        if sender_user_id not in cooldown_list.keys() or \
                (amount.lower() == 'stop' or amount.lower() == 'all'):

            # security checking for data values
            target = security_check(game)

            # check if the file exists
            if not target:
                return_value += 'That %s does not exist yet. Try using woodchips to add it.'%MySet.ResultName
                respond(data, return_value)
                return

            # check if the sender_user_id is 5attempting to do a !vote <name> all
            if amount.lower() == 'all':
                Parent.Log("Vote all", "Adding all logs.")
                new_data = (sender_user_id, target, amount.lower())
                # only add anything if the sender_user_id isn't on the cooldown list.
                if sender_user_id not in cooldown_list.keys():
                    add_amount = min(Parent.GetPoints(sender_user_id), MySet.voteMaximum)
                    if sender_user_id not in active_continuous_adds:
                        active_continuous_adds[sender_user_id] = new_data
                        return_value += 'You have been added to the continuous add list and are now adding ' + \
                                   MySet.PointName + 's until you run out. '
                else:
                    # if the sender_user_id isn't in the add list, add it and add the data
                    if sender_user_id not in active_continuous_adds:
                        active_continuous_adds[sender_user_id] = new_data
                        response = 'You have been added to the continuous add list and are now adding ' + \
                                   MySet.PointName + 's until you run out. '
                        Parent.SendStreamMessage(response)
                        return
                    else:
                        active_continuous_adds[sender_user_id] = new_data
                        response = 'You are already in the the active list. Type "!vote stop" at any time to stop adding. '
                        Parent.SendStreamMessage(response)
                        return

            # check if the sender_user_id is attempting to stop adding logs automatically
            elif amount == 'stop' and MySet.continuousVoting:
                if sender_user_id in active_continuous_adds:
                    return_value += 'You have been removed from the continuous add list for '+str(target)+' '+str(sender_user_display)
                    Parent.SendStreamWhisper(sender_user_id, return_value)
                    del active_continuous_adds[sender_user_id]
                    return
                else:
                    return_value += 'You aren\'t on the continuous add list.'
                    respond(data, return_value)
                    return

            # add amount
            else:
                # verify the amount to add is actually an integer
                try:
                    add_amount = int(amount)
                except ValueError as ve:
                    return_value += 'That isn\'t an integer. Please vote using an integer.'
                    respond(data, return_value)
                    return

             # check the amount is not higher than the sender_user_id can add.
            if add_amount > Parent.GetPoints(sender_user_id):
                return_value += 'Your %s pales in comparison to the amount you wish to add, %s. You only have %s. Wait to gather more.'\
                          %(MySet.ResultName, sender_user_display, str(Parent.GetPoints(sender_user_id)))
                respond(data, return_value)

                # if they're in the auto add list, remove them from that list
                if sender_user_id in active_continuous_adds:
                    del active_continuous_adds[sender_user_id]
                return

            # if users can add all the time, then ignore cooldowns and just add it
            if not MySet.AntiSnipe and add_amount >= 0:
                # get the number of points afterwards
                result = add_to_campfire(sender_user_id, target, add_amount)
                return_value += "%s added %i to %s's %s. There are now %i %ss in the %s. " % (
                sender_user_display, add_amount, target, MySet.ResultName, result, MySet.PointName, MySet.ResultName)
                respond(data, return_value)
                return

            # If the sender_user_id tries to add more than the set maximum, change the amount to add to be that maximum.
            if add_amount > int(MySet.voteMaximum):
                # get the number of seconds this will take to finish
                seconds_to_completion = int(((add_amount-float(MySet.voteMaximum))/float(MySet.voteMaximum))*int(MySet.cooldownTime))
                minutes_to_completion = 0
                hours_to_completion = 0
                if seconds_to_completion > 60:
                    minutes_to_completion = seconds_to_completion/60
                    seconds_to_completion = seconds_to_completion%60
                if minutes_to_completion > 60:
                    hours_to_completion = minutes_to_completion/60
                    minutes_to_completion = minutes_to_completion%60

                return_value += 'Currently the maximum number of %ss is %s. Removing this amount from your pool. '\
                          %(MySet.PointName, MySet.voteMaximum)

                add_amount = int(MySet.voteMaximum)
                # add users to the continuous add list and create a separate dictionary that keeps track of their cap
                if sender_user_id not in active_continuous_adds:
                    # store the new data as a tuple for another function to deal with.
                    new_data = (sender_user_id, target, int(amount) - add_amount)
                    active_continuous_adds[sender_user_id] = new_data
                    # send users a message to inform them how long logs will add for.
                    if hours_to_completion != 0:
                        return_value += ("You have been added to the continuous add list. " +
                                   MySet.PointName.capitalize() + ' will continue to add for ' +
                                   str(hours_to_completion) + ' hours and ' +
                                   str(minutes_to_completion) + ' minutes and ' +
                                   str(seconds_to_completion) +
                                   ' seconds. Type "!vote stop" to stop voting on this choice. ')
                    elif minutes_to_completion != 0:
                        return_value += ("You have been added to the continuous add list. " +
                                   MySet.PointName.capitalize() + 's will continue to add for ' +
                                   str(minutes_to_completion) + ' minutes and ' +
                                   str(seconds_to_completion) +
                                   ' seconds. Type "!vote stop" to stop voting on this choice. ')
                    else:
                        return_value += ("You have been added to the continuous add list. " +
                                   MySet.PointName.capitalize() + 's will continue to add for ' +
                                   str(seconds_to_completion) +
                                   ' seconds. Type "!vote stop" to stop voting on this choice. ')
            # check the amount is above 0.
            if add_amount <= 0:
                # if they're in the auto add list, remove them from that list
                if sender_user_id in active_continuous_adds:
                    del active_continuous_adds[sender_user_id]
                    return_value += sender_user_display + ' if you got this message, you ran out of ' + MySet.PointName + \
                              's and have been removed from auto add.'
                else:
                    return_value = '%s, %i is less than or equal to 0. Please offer at least one %ss.' \
                             % (sender_user_id, add_amount, MySet.PointName)

                respond(data, return_value)
                return

            # add it to the campfire
            result = add_to_campfire(sender_user_id, target, add_amount)

            # output the result to the sender_user_id
            return_value += "%s added %i to %s's %s. There are now %i %ss in the %s. "\
                      %(sender_user_display, add_amount, target, MySet.ResultName, result, MySet.PointName, MySet.ResultName)

            cooldown = MySet.cooldownTime
            # set the cooldown and save it
            if MySet.dynamicCooldown:
                cooldown = add_amount * (float(MySet.cooldownTime)/float(MySet.voteMaximum))
            # add a sender_user_id to a dictionary when they use the command.
            cooldown_list[sender_user_id] = time.time(), cooldown
            
        else:
            # Output the cooldown message
            if sender_user_id in cooldown_list.keys():
                seconds_to_wait = get_cooldown(sender_user_id)
                return_value += "You have to wait " + str(int(seconds_to_wait)) + ' more seconds before you can add ' + \
                          MySet.PointName + 's again.'
                respond(data, return_value)
                return

        # sends the final message
        if not MySet.SilentAdds:
            respond(data, return_value)

    # debug section
    if data.IsChatMessage() and data.GetParam(0).lower() == '!debug':
        if data.GetParam(1) == 'get_cooldown' and MySet.get_cooldown == True:
            return_value = get_cooldown(data.GetParam(2))
            Parent.SendStreamMessage(str(return_value))
        if data.GetParam(1) == 'get_live':
            return_value = str(get_stream_is_live())
            Parent.SendStreamMessage("Stream is live: " + return_value)
            Parent.SendStreamMessage("Stream isLive function: " + str(Parent.IsLive()))

    return


def Tick():
    """Required tick function"""
    removals = []
    global cooldown_list
    global stream_is_live
    # if you're on the cooldown list
    for x in cooldown_list:
        # if dynamic cooldown is enabled
        if MySet.dynamicCooldown:
            if time.time() - cooldown_list[x][1] > cooldown_list[x][0]:
                removals.append(x)
        elif time.time() - float(MySet.cooldownTime) > cooldown_list[x][0]:
            removals.append(x)
    
    # remove the people who have had their cooldowns time out.
    for each in removals:
        # if it's in the list of continues adds, resubmit the command that started it.

        if each.lower() in active_continuous_adds:
            del cooldown_list[each]
            # if the users are still present in the viewer list, continue removing logs.
            if each.lower() in set(Parent.GetViewerList()):
                if active_continuous_adds[each.lower()][2] > 0:
                    add_until_done(active_continuous_adds[each.lower()][0], active_continuous_adds[each.lower()][1],
                                   active_continuous_adds[each.lower()][2])

            # if the user isn't present
            else:
                Parent.SendStreamWhisper(each.lower(),
                                         'You have been removed from the continuous add list due to leaving '
                                         'the stream.')
        else:
            del cooldown_list[each]

    # decay
    if MySet.Decay:
        if stream_is_live == False and Parent.IsLive():
            stream_is_live = True
            decay()

        if stream_is_live == True and Parent.IsLive() == False:
            stream_is_live = False

    return


def check_options(data):
    """Required Execute function"""
    return_value = ''
    votes = get_vote_data()
    active = get_active_profile()
    options = {}

    # build a dictionary of values out of the options
    for option in votes["Profiles"][active]:
        options[option] = get_vote_option_value(option)

    if not len(options.keys()):
        respond(data, "There's nothing in this profile. Add options with !addvoteoption.")
        return

    # sort by the keys https://stackoverflow.com/questions/613183/how-do-i-sort-a-dictionary-by-value
    sorted_files = sorted(options.items(), key=operator.itemgetter(1))

    # add all sorted values to retval and return.
    for x, y in reversed(sorted_files):
        return_value += str(x)

        # if the value is higher than 0, add the value
        if options[x] > 0:
            return_value += '('+str(y)+' '+MySet.PointName+'s)'

        return_value += ', '

    return_value = return_value[:-2]

    # sends the final message
    respond(data, return_value)

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
            Parent.SendStreamWhisper(data.User, retVal)
        else:
            Parent.SendStreamMessage(str(retVal))


def security_check(input):
    data = get_vote_data()
    data_key_list = data["Profiles"][get_active_profile()].keys()
    lower_key_list = [key.lower() for key in data_key_list]
    comparison_key_list = dict(zip(lower_key_list, data_key_list))
    Parent.Log("comparison check", "Comparison list: " + str(comparison_key_list.keys()))
    Parent.Log("comparison check", "Results list: " + str(comparison_key_list.values()))
    Parent.Log("comparison check", "Input: " + input.lower())

    if input.lower() in comparison_key_list.keys():
        Parent.Log("comparison check", "Match found: " + comparison_key_list[input.lower()])
        return comparison_key_list[input.lower()]
    else:
        return None


# helper function that seperates values from the data Datatype
def add_until_done(user, targetgame, amount):

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
                cooldown = add_amount * (float(MySet.cooldownTime)/float(MySet.voteMaximum))
            # add a user to a dictionary when they use the command.
            cooldown_list[user.lower()] = time.time(), cooldown
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
            cooldown = add_amount * (float(MySet.cooldownTime)/float(MySet.voteMaximum))
        # add a user to a dictionary when they use the command.

        if not add_amount == 0:
            cooldown_list[user.lower()] = time.time(), cooldown
        else:
            Parent.SendStreamMessage(user + " you have run out of logs!")


def add_to_campfire(user, targetgame, amount):
    vote_data = get_vote_data()
    Parent.Log("Add_To_Campfire", "Loading the following data: "+ str(vote_data))
    vote_data["Profiles"][get_active_profile()][targetgame]["vote value"] += int(amount)
    Parent.Log("Add_To_Campfire", "User " + user + " attempting to add " + str(amount) + " to " + targetgame)

    # adds a user to the tracking information for that vote if they haven't already voted on that game
    if user in vote_data["Profiles"][get_active_profile()][targetgame]["votes list"].keys():
        vote_data["Profiles"][get_active_profile()][targetgame]["votes list"][user] += int(amount)
    else:
        Parent.Log("Add_To_Campfire", "Adding a new user to the votes list.")
        vote_data["Profiles"][get_active_profile()][targetgame]["votes list"][user] = int(amount)
    vote_data["Profiles"][get_active_profile()][targetgame]["last added"] = time.time()
    Parent.Log("Add_To_Campfire", "vote_data dictionary updated.")
    update_vote_data(vote_data)
    Parent.RemovePoints(user, user, amount)

    Parent.Log("Add_To_Campfire", "Attempting to update christmas settings.")
    if MySet.christmas:
        add_to_givers(user, amount)
    Parent.Log("Add_To_Campfire", "Updated Christmas settings successfully.")

    Parent.Log("Add_To_Campfire", "Add completed successfully.")
    return get_vote_option_value(targetgame)


def add_to_givers(user, amount):
    giverLocation = os.path.join(os.path.dirname(__file__), '../../Twitch/Givers/', user.lower()+".txt")
    Parent.Log("add_to_givers", "Giver exists: " + str(os.path.exists(giverLocation)))
    Parent.Log("add_to_givers", "Giver path: " + str(giverLocation))
    if os.path.exists(giverLocation):
        with open(giverLocation, 'r') as vote:
            voteData = int(vote.read().decode('utf-8-sig'))
        voteData += amount
        with open(giverLocation, 'w+') as vote:
            vote.write(str(voteData))
    else:
        with open(giverLocation, 'w+') as vote:
            vote.write(str(amount))


def get_active_profile():
    global vote_location
    data = get_vote_data()
    return data["Active Profile"]


def set_active_vote_profile(profile):
    """Sets the active vote profile by changing the text file in the vote directory. Makes a new vote profile
    if it doesn't exist yet."""
    global vote_location
    data = get_vote_data()

    # if the new location doesn't exist, create it
    data["Active Profile"] = profile
    if profile not in data["Profiles"].keys():
        data["Profiles"][profile] = {}

    update_vote_data(data)


def delete_vote_location(profile):
    """Deletes the target vote profile completely."""
    global vote_location
    target_location = profile
    data = get_vote_data()
    active = get_active_profile()

    # clear the vote location if it's currently active
    if active == profile:
        data["Active Profile"] = "Default"

    # delete the profile
    del data["Profiles"][profile]

    update_vote_data(data)


def get_cooldown(user):
    global cooldown_list

    # if the user isn't on cooldown, return 0
    if user.lower() not in cooldown_list.keys():
        return 0.0

    # how long has it been since we voted?
    time_since_vote = (time.time() - cooldown_list[user.lower()][0])

    # returns how much time is left
    if MySet.dynamicCooldown:
        return cooldown_list[user.lower()][1] - time_since_vote
    else:
        return float(MySet.cooldownTime) - time_since_vote

def get_stream_is_live():
    global stream_is_live

    return stream_is_live


def get_vote_data():
    with codecs.open(os.path.join(vote_location, "vote.json"), encoding='utf-8-sig', mode='r') as f:
        vote_data = json.load(f, encoding='utf-8-sig')

    return vote_data


def vote_exists(target):
    data = get_vote_data()
    if target in data["Profiles"][get_active_profile()].keys():
        return True
    else:
        return False


def update_vote_data(data):
    # Parent.Log("update_vote_data", "Adding the following Data structure: " + str(data))
    with codecs.open(os.path.join(vote_location, "vote.json"), mode='w+') as f:
        output = json.dumps(data, f, indent=2, encoding='utf-8-sig')
        f.write(output)
    Parent.Log("update_vote_data", "Updated the file successfully.")

    return output


def add_vote_option(option, amount):
    data = get_vote_data()
    data["Profiles"][get_active_profile()][option] = {"vote value": amount,
                                                      "votes list": {},
                                                      "contributor": "",
                                                      "length of game": 0,
                                                      "last added": time.time()}
    vote_data = update_vote_data(data)
    return vote_data


def get_vote_option_value(option):
    global vote_location
    option_value = 0
    data = get_vote_data()
    active = data["Active Profile"]
    if option in data["Profiles"][active].keys():
        option_value = data["Profiles"][active][option]["vote value"]

    return option_value


def decay():

    seconds_in_a_day = 86400
    decay_threshold = int(MySet.Decay_Days)

    last_decay = 0
    if "Last Decay" in get_vote_data().keys():
        last_decay = get_vote_data()["Last Decay"]
    else:
        vote_data = get_vote_data()
        vote_data["Last Decay"] = time.time()
        update_vote_data()

    if time.time() - last_decay > seconds_in_a_day:
        if os.path.exists(shieldsFile):
            with open(shieldsFile, encoding="utf-8-sig", mode="r") as f:
                decay_threshold = int(f.read())
        vote_data = get_vote_data()
        for vote in vote_data["Profiles"][get_active_profile()].keys():
            elapsed_time = time.time() - vote_data["Profiles"][get_active_profile()][vote]["last added"]
            # Parent.Log("Decay", "{} has elapsed {} seconds since the last add.".format(vote, elapsed_time))

            if elapsed_time > (seconds_in_a_day * decay_threshold):

                days_past_threshold = int((elapsed_time - (seconds_in_a_day * decay_threshold))/seconds_in_a_day)
                # Parent.Log("Decay", "{} is {} days past the threshold.".format(vote, days_past_threshold))
                decay_total = int(MySet.Decay_Amount) * days_past_threshold

                new_value = vote_data["Profiles"][get_active_profile()][vote]["vote value"] - decay_total

                vote_data["Profiles"][get_active_profile()][vote]["vote value"] = new_value

                Parent.Log("Decay", "Decaying {} by {}".format(vote, decay_total))

                # checks if the value is less than 0 and corrects it.
                if vote_data["Profiles"][get_active_profile()][vote]["vote value"] < 0:
                    vote_data["Profiles"][get_active_profile()][vote]["vote value"] = 0

                    if get_active_profile() != "decayed":
                        # move it to the stone of stories after it runs out of
                        if "decayed" not in vote_data["Profiles"].keys():
                            vote_data["Profiles"]["decayed"] = {}
                        vote_data["Profiles"]["decayed"][vote] = vote_data["Profiles"][get_active_profile()][vote]
                        del vote_data["Profiles"][get_active_profile()][vote]

        vote_data["Last Decay"] = time.time()
        update_vote_data(vote_data)

def change_points(user, amount):
    points = load_points()

    if user in points["Users"].keys():
        if (points["Users"][user] + amount) < 0:
            return False

    if user in points["Users"].keys():
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
        points = json.dumps(points_data, json_file, encoding="utf-8-sig", indent=4)
        json_file.write(points)

    return points


def get_points(user):
    points = load_points()

    if user in points["Users"].keys():
        return points["Users"][user]
    else:
        return 0