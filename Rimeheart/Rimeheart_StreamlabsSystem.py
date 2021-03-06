#!/usr/bin/python
# -*- coding: utf-8 -*-
# pylint: disable=invalid-name
"""Let viewers pay currency to boost currency payouts
for everyone in chat for x seconds"""
import json
import os, os.path
import codecs
from time import time

# ---------------------------------------
# [Required] Script information
# ---------------------------------------
ScriptName = "Rimeheart"
Website = "https://www.twitch.tv/newtc"
Creator = "Newt"
Version = "1.0.0.0"
Description = "Enables the Rimeheart event, which runs constant giveaways."

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
keys_file = os.path.join(os.path.dirname(__file__), "keys.txt")
current_giveaway = os.path.join(os.path.dirname(__file__), "giveaway.json")


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
    global giveaway

    # Load in saved settings
    MySet = Settings(settingsFile)

    if not os.path.exists(current_giveaway):
        giveaway = select_new_game()
        with open(current_giveaway, "w+") as f:
            json.dump(giveaway, f, encoding='utf-8-sig', indent=4)
    else:
        with open(current_giveaway, "r") as f:
            giveaway = json.load(f)
            update_start_time()

    # End of Init
    return


def Execute(data):
    global giveaway
    global MySet
    global send_user_display
    global send_user_id
    """Required Execute function, run whenever a user says anything."""

    send_user_id = parse_origin(data)[0]
    send_user_display = parse_origin(data)[1]

    # Parent.Log("Rimeheart IsLive", "IsLive: " + str(Parent.IsLive()))
    if not Parent.IsLive() and MySet.OnlyLive:
        return

    if data.GetParam(0) == MySet.RaffleCommand:
        if data.GetParamCount() < 2:
            buy_raffle(send_user_id)
        else:
            try:
                buy_raffle(send_user_id, int(data.GetParam(1)))
            except ValueError as e:
                Parent.SendStreamMessage("Sorry, but " + data.GetParam(1) + " is not an integer.")

    if data.GetParam(0) == MySet.GameCommand:
        game = giveaway["game"]
        Parent.SendStreamMessage("The current raffle target is: " + game + ". !raffle to enter.")

    if Parent.HasPermission(data.User, "Caster", ""):
        if data.GetParam(0) == "!skip":
            select_new_game()

        if data.GetParam(0) == "!roll":
            select_raffle_winner()

    return


def Tick():
    """Required tick function, run whenever possible."""
    global MySet

    time_between_raffles = int(MySet.Duration)  # default to 30 minutes

    if MySet.OnlyLive and not Parent.IsLive():
        return

    if time() - get_start_time() > time_between_raffles:
        select_raffle_winner()
        select_new_game()

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


def select_new_game():
    """ Returns a new dictionary with the game information. """
    global giveaway

    Parent.SendStreamMessage(
        "Selecting another game for raffle. " + MySet.RaffleCommand +
        " to enter, 100 logs each. Raffles last 30 minutes.")

    # select the next key
    with open(keys_file, "r") as f:
        file_data = f.readlines()

        # get the first line
        line = file_data[0].strip("\n")

        # get the game name and key
        game = " ".join(line.split(" ")[0:-1])
        key = line.split(" ")[-1]

    # delete the key that was chosen
    with open(keys_file, "w+") as f:
        count = 0
        # skip the first line, write the rest.
        for line in file_data:
            if count == 0:
                count += 1
                continue

            f.write(line)

    giveaway = {
        "game": game,
        "key": key,
        "raffle": {},
        "start_time": time()
    }

    Parent.SendStreamMessage("The next game up for raffle is " + game)
    update_json()

    return giveaway


def buy_raffle(user, amount=1):
    global giveaway

    if amount*100 > Parent.GetPoints(user):
        Parent.SendStreamMessage("You don't have enough " + MySet.PointsName + " for that.")
        return False

    Parent.RemovePoints(user, user, amount * 100)
    add_to_givers(user, amount * 100)
    if user.lower() in giveaway["raffle"].keys():
        giveaway["raffle"][user.lower()] += amount
    else:
        giveaway["raffle"][user.lower()] = amount
    Parent.SendStreamMessage(send_user_display + " just bought " + str(amount) + " raffle tickets.")
    update_json()

    return True


def select_raffle_winner():
    global giveaway

    # generates the list by adding the user to the raffle once per each of their tickets.
    raffle = []
    for user in giveaway["raffle"].keys():
        for i in range(giveaway["raffle"][user]):
            raffle.append(user)

    Parent.Log("Rimeheart", str(raffle))

    if raffle:
        winner = raffle[Parent.GetRandom(0, len(raffle))]

        Parent.SendStreamMessage("Congratulations %s! You won a copy of %s! Check your whispers in a "
                                 "few moments for the key." % (winner, giveaway["game"]))
        Parent.SendStreamWhisper(winner, "Here is your key for %s: %s" % (giveaway["game"], giveaway["key"]))
        return winner
    else:
        Parent.SendStreamMessage("No entries for %s? We'll return it to the list." % giveaway["game"])
        with open(keys_file, "a+") as f:
            f.write("\n" + giveaway["game"] + " " + giveaway["key"])

        return None


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


def update_start_time():
    giveaway["start_time"] = time()
    update_json()


def get_start_time():
    global giveaway
    return giveaway["start_time"]


def update_json():
    global giveaway

    with open(current_giveaway, "w+") as f:
        json.dump(giveaway, f, indent=4)


def parse_origin(data):
    sender_user_id = ""
    sender_user_display = ""
    if data.IsFromTwitch():
        sender_user_id = data.UserName.lower()
        sender_user_display = data.UserName
    elif data.IsFromYoutube():
        sender_user_id = data.User
        sender_user_display = data.UserName

    return sender_user_id, sender_user_display
