#!/usr/bin/python
# -*- coding: utf-8 -*-
# pylint: disable=invalid-name
"""Let viewers pay currency to boost currency payouts
for everyone in chat for x seconds"""
import json
import os, os.path
import codecs
import time
import sys
import re
import datetime
import shutil

sys.path.append(os.path.dirname(__file__))
import redeemable
import community_challenge


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
vote_location = os.path.join(os.path.dirname(__file__), '..\\..\\Twitch\\Votes\\')


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
    global Data
    global DisplayCount
    # Load in saved settings
    MySet = Settings(settingsFile)
    LastPayout = time.time()
    DisplayCount = 3

    if not os.path.exists(points_json):
        with open(points_json, "w+") as f:
            base_file = {
                "Users": {

                },
                "challenges": {

                }
            }

            result = json.dumps(base_file, f, encoding="utf-8-sig", indent=4)
            f.write(result)

    data = load_points()

    # create the challenges if it doesn't already exist.
    if "challenges" not in data.keys():
        data["challenges"] = {}
        update_points(data)

    Parent.Log("Woodchips Initialization", "Creating backup points list.")
    if not os.path.exists("Backups"):
        os.mkdir("Backups")
    Parent.Log("Woodchips Initialization", "Backup created in: " + os.getcwd())
    shutil.copyfile(os.path.join(points_json), "Backups\\Woodchips_" + str(time.time()) + ".json")

    # End of Init
    return


def Execute(data):
    """Required Execute function, run whenever a user says anything."""

    sender_user_id = ""
    sender_user_display = ""
    if data.IsFromTwitch():
        sender_user_id = data.UserName.lower()
        sender_user_display = data.UserName
    elif data.IsFromYoutube() or data.IsFromDiscord():
        sender_user_id = data.User
        sender_user_display = data.UserName

    # redeemables
    redeemables = {
        "recap": redeemable.Redeemable("recap", "Recap that story Newt!", -200, data.User.lower()),
        "drink": redeemable.Redeemable("drink", "Take a drink!", -500, data.User.lower()),
        "pet": redeemable.Redeemable("pet", "Pet that cat!", -600, data.User.lower()),
        "story": redeemable.Redeemable("story", "Story time!", -1000, data.User.lower()),
        "break": redeemable.Redeemable("break", "Time to hit the road.", -3000, data.User.lower())
    }

    if data.IsChatMessage():
        # moved here for the sake of readability. Also resolves an error related to these options not existing before now.
        if data.GetParamCount() >= 3:
            args = " ".join(data.Message.split(" ")[2:])
            redeemables["add"] = redeemable.Redeemable("add", "Adding your game to the list!", -20000,
                                                       data.User.lower(), add_to_votes, args)
            redeemables["move"] = redeemable.Redeemable("move", "Moving " + args + " to the top of the list!", -30000,
                                                        data.User.lower(), move_option_to_top, args)
            redeemables["top"] = redeemable.Redeemable("top", "Adding and moving " + args + " to the top of the list!",
                                                       -45000,
                                                       data.User.lower(), create_and_move, args)

        # !woodchips
        if data.GetParam(0) == MySet.CheckCommand:
            respond(data, "/me You have " + str(get_points(data.User)) + " woodchips.")

        # !redeem
        if data.GetParam(0).lower() == MySet.RedeemCommand and data.GetParam(1).lower() in redeemables.keys():
            if data.GetParamCount() == 2:
                if redeemables[data.GetParam(1).lower()].redeem():
                    Parent.SendStreamMessage(redeemables[data.GetParam(1).lower()].description)
                else:
                    respond(data, "/me You don't have enough woodchips for that.")
            if data.GetParamCount() >= 3:
                if redeemables[data.GetParam(1).lower()].redeem():
                    Parent.SendStreamMessage(redeemables[data.GetParam(1).lower()].description)
                else:
                    respond(data, "/me You don't have enough woodchips for that.")

        # !community
        if data.GetParam(0).lower() == "!community":

            # Test script: !community create "Test Event" 02-01-2021 10000
            if data.Message == "!community example":
                respond(data, "!community create \"Test Event\" 02-01-2021 10000")

            # options
            if data.Message == "!community options":
                message = "/me Here are the currently available events: "

                for challenge in load_points()["challenges"].keys():
                    message += challenge + "({}/{}), ".format(
                        str(load_points()["challenges"][challenge]["current count"]),
                        str(load_points()["challenges"][challenge]["success count"]))
                message = message[:-2]
                respond(data, message)
                return

            # create
            if Parent.HasPermission(sender_user_id, "Caster", ""):
                match = re.search("!community\screate\s\"(.+)\"\s(\d{2}-\d{2}-\d{4})\s(\d+)", data.Message)
                # Parent.Log("Community", "Searching for a match in {}".format(data.Message))
                if match is not None:
                    name = match.group(1)
                    date = match.group(2)
                    try:
                        completion_amount = int(match.group(3))
                    except ValueError as e:
                        respond(data, "/me Look, you have to use an integer. "
                                                 "{} is not that.".format(match.group(3)))
                        return

                    if community_challenge.CommunityChallenge(name, date, completion_amount).save_to_file():
                        respond(data, "/me Successfully created \"{}\" community event.".format(name))
                    else:
                        respond(data, "/me Failed to create \"{}\" community event.".format(name))

            # stoke
            stoke_match = re.search("!community stoke ((\w+\s){1,})(\d+)", data.Message)
            if stoke_match is not None:
                amount = 0
                try:
                    amount = int(stoke_match.group(3))
                except ValueError as e:
                    respond(data, "/me {} is not an integer.".format(stoke_match.group(1)))
                    return

                # modify the user's points
                if not change_points(data.User.lower(), amount*-1):
                    respond(data, "/me You don't have enough woodchips for that. Stick around to earn more.")
                    return

                challenge_name = stoke_match.group(1)[0:-1]

                points_data = load_points()
                if challenge_name in points_data["challenges"].keys():
                    current_points = points_data["challenges"][challenge_name]["current count"]
                    success_points = points_data["challenges"][challenge_name]["success count"]

                    points_data["challenges"][challenge_name]["current count"] += amount
                    percent = (float(points_data["challenges"][challenge_name]["current count"])/float(success_points))*100
                    respond(data, "/me Stoked the community challenge \"{}\" with {} more woodchips. Challenge is now at {}%".format(
                        challenge_name, amount, percent))

                    if current_points >= \
                            success_points:
                        respond(data, "/me Challenge \"{}\" successfully completed!".format(challenge_name))
                        del points_data["challenges"][challenge_name]
                        Parent.Log("Community", "Removed the community challenge \"{}\" due to completing.".format(challenge_name))
                else:
                    respond(data, "/me That challenge doesn't exist.")

                update_points(points_data)

    return


def Tick():
    """Required tick function, run whenever possible."""
    global MySet
    global LastPayout
    global DisplayCount

    if DisplayCount > 2:
        DisplayCount = 0
        message = "/me Here are the currently available events: "

        for challenge in load_points()["challenges"].keys():
            message += challenge + "({}/{}), ".format(
                str(load_points()["challenges"][challenge]["current count"]),
                str(load_points()["challenges"][challenge]["success count"]))
        message = message[:-2]
        Parent.SendStreamMessage(message)

    # if the last payout was more than the interval's time ago, payout now.
    if time.time() - LastPayout > int(MySet.PayoutInterval) and Parent.IsLive():
        Parent.Log("Woodchips", "Tick")
        for viewer in set(Parent.GetViewerList()):
            change_points(viewer, int(MySet.PayoutRate))

        LastPayout = time.time()
        DisplayCount += 1

    # load in the list of challenges
    points_data = load_points()

    for challenge in points_data["challenges"].keys():
        # month = int(data["challenges"][challenge]["end date"].split('-')[0])
        # day = int(data["challenges"][challenge]["end date"].split('-')[1])
        # year = int(data["challenges"][challenge]["end date"].split('-')[2])
        # Parent.SendStreamMessage("{}-{}-{}".format(month, day, year))
        # end_date = datetime.date(year, month, day)
        end_date = datetime.datetime.strptime(points_data["challenges"][challenge]["end date"], "%m-%d-%Y")
        if end_date < datetime.datetime.now():
            Parent.SendStreamMessage("/me Oh no, the \"{}\" community challenge was failed!".format(challenge))
            del points_data["challenges"][challenge]
            Parent.Log("Community", "Removed the community challenge \"{}\" due to running out of time.".format(challenge))
            update_points(points_data)

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


def select_story():
    Parent.SendStreamMessage("!story roll")

# ======================== Vote Functions ==========================
def get_active_profile():
    global vote_location
    data = get_vote_data()
    return data["Active Profile"]


def update_vote_data(data):
    Parent.Log("update_vote_data", "Adding the following Data structure: " + str(data))
    with codecs.open(os.path.join(vote_location, "vote.json"), mode='w+') as f:
        output = json.dumps(data, f, indent=2, encoding='utf-8-sig')
        f.write(output)
    Parent.Log("update_vote_data", "Updated the file successfully.")

    return output


def get_vote_data():
    with codecs.open(os.path.join(vote_location, "vote.json"), encoding='utf-8-sig', mode='r') as f:
        vote_data = json.load(f, encoding='utf-8-sig')

    return vote_data


def add_to_votes(option):
    data = get_vote_data()
    data["Profiles"][get_active_profile()][option] = {"vote value": 0,
                                                      "votes list": {},
                                                      "contributor": "",
                                                      "length of game": 0,
                                                      "last added": time.time()}
    vote_data = update_vote_data(data)
    return vote_data


def move_option_to_top(option):
    data = get_vote_data()

    values = list(data["Profiles"][get_active_profile()][vote]["vote value"] for vote in data["Profiles"][get_active_profile()].keys())
    top_value = max(values)

    data["Profiles"][get_active_profile()][option]["vote value"] = top_value
    update_vote_data(data)


def create_and_move(option):
    add_to_votes(option)
    move