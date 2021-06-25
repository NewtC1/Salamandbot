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

#---------------------------------------
# [Required] Script information
#---------------------------------------
ScriptName = "Festival"
Website = "https://www.twitch.tv/newtc"
Creator = "Newt"
Version = "1.0.0.0"
Description = "Allows users to select stories for me to tell"

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
story_file = os.path.join(os.path.dirname(__file__), "stories.json")
pending_file = os.path.join(os.path.dirname(__file__), "pending.json")

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
            self.Command = "!stories"
            self.SubmissionRewards = "100"

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

class Story:
    StoryInfo = ""
    StoryValue = 0
    StoryContributor = ""

    def __init__(self, info, contributor):
        self.StoryInfo = info
        self.StoryContributor = contributor

    def get_story_info(self):
        return self.StoryInfo

    def set_story_info(self, info):
        self.StoryInfo = info

    def get_value(self):
        return self.StoryValue

    def set_value(self, value):
        self.StoryValue = value

    def get_contributor(self):
        return self.StoryContributor

    def set_contributor(self, contributor):
        self.StoryContributor = contributor


class NewtClass:
    NewtClass = True
    NewtStreamerLevel = 5

#---------------------------------------
# [Required] functions
#---------------------------------------
def Init():
    """Required tick function"""
    # Globals
    global MySet
    global m_Active
    global selected_stories
    global story_timer
    global last_removed_story
    m_Active = False
    selected_stories = []
    story_timer = time.time() + 5400
    last_removed_story = {}
    # story_timer += time.time() + 600
    # Load in saved settings
    MySet = Settings(settingsFile)

    if not os.path.exists(story_file):
        Parent.SendStreamMessage("No story file found. Creating a new one.")
        data = {}
        with codecs.open(story_file, encoding='utf-8-sig', mode='w+') as f:
            json.dump(data, f, encoding='utf-8-sig', indent=2)

    if not os.path.exists(pending_file):
        Parent.SendStreamMessage("No pending file found. Creating a new one.")
        data = {}
        with codecs.open(pending_file, encoding='utf-8-sig', mode='w+') as f:
            json.dump(data, f, encoding='utf-8-sig', indent=2)

    # convert_to_new_format()

    # End of Init
    return


def Execute(data):
    """Required Execute function"""

    roll_permissions = ["subscriber", "moderator", "vip", "vip+"]


    retVal = ''
    global selected_stories
    global story_timer

    if data.IsChatMessage():
        if data.GetParam(0).lower() == MySet.Command.lower() or data.GetParam(0).lower() == "!story":

            # parse the input to something usable by the script
            data_input = data.Message
            data_input = data_input.split()
            data_input = data_input[2:]
            title = ' '.join(data_input)
            data_input = '_'.join(data_input).lower()

            # two word commands
            if data.GetParamCount() == 2:
                if data.GetParam(1).lower() == "display":
                    respond(data, display_story_list())
                if data.GetParam(1).lower() == "selected":
                    respond(data, parse_selected_stories())
                if data.GetParam(1).lower() == "roll":
                    if Parent.HasPermission(data.User,"user_specific", "newtc"):
                        if len(selected_stories) > 0:
                            roll_story()
                            story_timer = time.time() + 3600
                        else:
                            roll_unselected_story()
                if data.GetParam(1).lower() == "pending":
                    respond(data, display_pending_list())
                if data.GetParam(1).lower() == "links":
                    respond(data, display_pending_links())

            # single word commands
            if data.GetParamCount() == 1:
                respond(data, display_story_list())

            # variable length commands
            if data.GetParamCount() > 1:
                if data.GetParam(1).lower() == "info":
                    respond(data, "Info for " + title + ": " + story_info(data_input))
                if data.GetParam(1).lower() == "select":
                    story_added = select_story(data_input, selected_stories, data.UserName)
                    if (story_added == True):
                        respond(data, "Added " + title + " to the next story spin.")
                    elif (story_added == False):
                        respond(data, "That story is already in the next story spin.")
                if data.GetParam(1).lower() == "add":
                    # get the final value and save is as the link
                    length = data.GetParamCount()
                    info = data.GetParam(length - 1)

                    # build the name
                    name = []
                    for param in range(2, length-1):
                        name.append(data.GetParam(param))
                    data_input = '_'.join(name)

                    # save the contributor
                    contributor = data.UserName.lower()

                    if data_input:
                        add_story(data_input, info, contributor)
                if data.GetParam(1).lower() == ("remove" or "subtract"):
                    remove_story(data_input)
                if data.GetParam(1).lower() == "restore":
                    re_add(data_input)
                if data.GetParam(1).lower() == "approve":
                    approve_story(data_input)

        if data.GetParam(0).lower()[0] == '!':
            if data.GetParam(0).lower()[1:] in load_story_list():
                respond(data, load_story_list()[data.GetParam(0).lower()[1:]])
    return

def Tick():
    """Required tick function"""
    global story_timer
    # roll a new story every 3 hours
    if time.time() > story_timer:
        if len(selected_stories) > 0:
            roll_story()

        # else:
        #    roll_unselected_story()

        story_timer = time.time() + 3600

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


def load_story_list():
    """Returns a the list of counters as a settings object"""
    with codecs.open(story_file, encoding='utf-8-sig', mode='r') as f:
        data = json.load(f, encoding='utf-8-sig')

    return data


def load_pending_list():
    """Returns a the list of counters as a settings object"""
    with codecs.open(pending_file, encoding='utf-8-sig', mode='r') as f:
        data = json.load(f, encoding='utf-8-sig')

    return data

# display all available stories
def display_story_list():
    data = load_story_list()
    retval = ''
    for key in data.keys():
        upper = ''
        # uppercase every first letter
        for word in key.split("_"):
            output = word.replace(word[0], word[0].upper(), 1)
            upper += output + " "

        # get rid of the last space
        upper = upper[:-1]
        retval += upper + ', '

    retval = retval.replace('_', ' ')
    retval = retval[:-2]

    return retval


# display all available stories
def display_pending_list():
    data = load_pending_list()
    retval = ''
    for key in data.keys():
        upper = ''
        # uppercase every first letter
        for word in key.split("_"):
            output = word.replace(word[0], word[0].upper(), 1)
            upper += output + " "

        # get rid of the last space
        upper = upper[:-1]
        retval += upper + ', '

    retval = retval.replace('_', ' ')
    retval = retval[:-2]

    return retval


def display_pending_links():
    data = load_pending_list()
    retval = ''
    for key in data.keys():
        output = key + ": " + data[key]["info"]

        # get rid of the last space
        output = output[:-1]
        retval += output + ' , '

    retval = retval[:-1]

    return retval


def parse_selected_stories():
    # returns a list of selected stories

    global selected_stories
    retval = ''
    if len(selected_stories) != 0:
        for stories in selected_stories:
            upper = ''
            # uppercase every first letter
            for word in stories.split("_"):
                output = word.replace(word[0], word[0].upper(), 1)
                upper += output + " "

            # get rid of the last space
            upper = upper[:-1]
            retval += upper + ', '

        retval = retval.replace('_', ' ')
        retval = retval[:-2]
    else:
        retval = "There are no stories selected! Please select one."

    return retval

# returns the story info
def story_info(story):
    data = load_story_list()
    if story.lower() in data:
        return data[story.lower()]["info"]
    else:
        return "The story " + story + " is not in the story selection yet. Send me a link and I can add it."

# parses the story's name into an easily readable string
def story_name(story):
    data = load_story_list()
    if story.lower() in data.keys():
        upper = ''
        for word in story.split("_"):
            output = word.replace(word[0], word[0].upper(), 1)
            upper += output + " "

        upper = upper[:-1]

        return upper
    else:
        return ""

# select a story
def select_story(story, selected_stories, user):
    global story_timer

    data = load_story_list()
    if story.lower() in data.keys():
        if story.lower() not in selected_stories:
            selected_stories.append(story.lower())
            story_timer = time.time() + 1800
            if data[story.lower()]["contributor"] != user.lower():
                # add more points each time anyone other than the user selects it
                data[story.lower()]["value"] += 50
            with codecs.open(story_file, encoding='utf-8-sig', mode='w+') as f:
                json.dump(data, f, encoding='utf-8-sig', indent=2)
            return True
        else:
            return False

# select a story from chosen stories
def roll_story():
    global selected_stories
    choice = selected_stories[Parent.GetRandom(0, len(selected_stories))]
    retval = "The story that was selected was: " + story_name(choice) + ". You can follow along at " + story_info(choice)
    Parent.SendStreamMessage(retval)
    # reset selected stories
    selected_stories = []
    # payout if the user is in chat
    data = load_story_list()
    if (data[choice.lower()]["contributor"] in Parent.GetViewerList()) and (data[choice]["value"] > 0):
        user = data[choice.lower()]["contributor"]
        value = data[choice.lower()]["value"]
        Parent.AddPoints(user.lower(), user.lower(), value)

    # remove the story we rolled from the list
    remove_story(choice.lower())

    return choice

def roll_unselected_story():
    data = load_story_list()
    stories = data.keys()

    choice = stories[Parent.GetRandom(0, len(stories))]
    retval = "Rolling from the main story list. The story that was selected was: " + story_name(choice) + ". You can follow along at " + story_info(
        choice)
    Parent.SendStreamMessage(retval)

    if (data[choice.lower()]["contributor"] in Parent.GetViewerList()) and (data[choice]["value"] > 0):
        user = data[choice.lower()]["contributor"]
        value = data[choice.lower()]["value"]
        Parent.AddPoints(user.lower(), user.lower(), value)

    remove_story(choice.lower())

    return choice

# add a story
def add_story(story, info, contributor):
    retval = False
    # if the counter already exists
    if story in load_pending_list() or load_story_list():
        Parent.SendStreamMessage("That story already exists.")
    # else if the counter does not exist
    else:
        # add the counter to the counters.json
        counter_list = load_pending_list()
        storyname = story.lower()
        counter_list[storyname] = {}
        counter_list[storyname]["info"] = info
        counter_list[storyname]["contributor"] = contributor
        counter_list[storyname]["value"] = 0

        # give logs to the user who added
        Parent.AddPoints(contributor, contributor, int(MySet.SubmissionReward))

        # save the story
        with codecs.open(pending_file, encoding='utf-8-sig', mode='w+') as f:
            json.dump(counter_list, f, encoding='utf-8-sig', indent=2)
        Parent.SendStreamMessage('Story "' + story_name(story) +
                                 '" successfully created. It has been stored in pending.')

        retval = True

    return retval


def approve_story(story):
    """
    Moves a story from the pending file to the story file.
    :param story: The story to approve.
    :return:
    """

    pending_data = load_pending_list()
    story_to_approve = pending_data[story.lower()]
    del pending_file[story.lower()]

    with codecs.open(pending_file, encoding='utf-8-sig', mode='w+') as f:
        json.dump(pending_data, f, encoding='utf-8-sig', indent=2)

    story_data = load_story_list()
    story_data[story.lower()] = story_to_approve

    # save the story
    with codecs.open(story_file, encoding='utf-8-sig', mode='w+') as f:
        json.dump(story_data, f, encoding='utf-8-sig', indent=2)
    Parent.SendStreamMessage('Story "' + story_name(story) + '" successfully created.')


# remove a story from the list
def remove_story(story):
    global last_removed_story

    data = load_story_list()
    # save the story for restoration if we need to
    last_removed_story[story.lower()] = data[story.lower()]
    del data[story.lower()]
    # update the story file with the removed story
    with codecs.open(story_file, encoding='utf-8-sig', mode='w+') as f:
        json.dump(data, f, encoding='utf-8-sig', indent=2)


def re_add(story):
    story_lower = story.lower()
    global last_removed_story

    if story_lower in last_removed_story.keys():
        # create the new story
        counter_list = load_story_list()
        counter_list[story_lower] = {}
        counter_list[story_lower]["info"] = last_removed_story[story_lower]["info"]
        counter_list[story_lower]["contributor"] = last_removed_story[story_lower]["contributor"]
        counter_list[story_lower]["value"] = last_removed_story[story_lower]["value"]

        # save the story
        with codecs.open(story_file, encoding='utf-8-sig', mode='w+') as f:
            json.dump(counter_list, f, encoding='utf-8-sig', indent=2)
        Parent.SendStreamMessage('Story "' + story_name(story) + '" successfully restored.')

#def convert_to_new_format():
#    data = load_story_list()
#    for each in data.keys():
        # build the new values
#        new_data = {}
#        if type(data[each]) != dict:
#            new_data["info"] = data[each]
#            new_data["contributor"] = ""
#            new_data["value"] = 0
#        if len(new_data.keys()) > 0:
#            data[each] = new_data

#    with codecs.open(story_file, encoding='utf-8-sig', mode='w+') as f:
#        json.dump(data, f, encoding='utf-8-sig')