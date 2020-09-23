Hello! Welcome to the readme.

This script pack is intended for use with the Streamlabs Chatbot, formerly known as Ankhbot.

Installing the pack:
1. Follow the instructions to setup python for Streamlabs Chatbot.
2. Unzip the this folder into the StreamlabsChatbot/Services/Scripts directory.
3. Move all of the individual script folders to the Scripts directory. For example, the Votes script should be in this path: Streamlabs Chatbot\Services\Scripts\Vote.
4. Open the bot and switch to the Scripts section.
5. Enable the script by clicking the check mark on the right side of the script.
6. Click the script itself and set any settings you want.

Modules:
    Vote
    This is the biggest module, and includes the following commands:
        !vote
        Allows users to vote on a vote option. Comes with several options that can be modified in settings. By default
        votes with no cooldown.

        !checkoptions
        Displays all vote options in the current vote profile in a sorted list from highest to lowest.

        !addvoteoption
        Adds a vote option to the current profile. Vote options can be created with two different syntaxes:
            !addvoteoption A game name [optional value]
            !addvoteoption "A game name ending in a number 2" [optional value]
        Options ending in a number must be enclosed with double quotes.

        !deletevoteoption
        Deletes the vote option if it exists. Must be in the current vote profile.

        !setvoteprofile
        Sets the vote profile to the listed value or creates a new one if it doesn't exist.

        !deletevoteprofile
        Deletes the listed vote profile, along with any vote options within it.

        !showvoteprofile
        Displays a list of all existing vote profiles.

    Counter
    An alternative to the built in counter system. Allows chat members to make and maintain their own counters.
        !counter add [name]
        Adds the counter option.

        !counter remove [name]
        Deletes the counter option (by setting it to 0.)

        +[name] [amount]
        Increments by the amount, or one if not provided.

        -[name] [amount]
        Decrements by the amount, or one if not provided.

        ![name]
        Displays the amount that counter currently has.

    Points
    Displays the current user's point value.