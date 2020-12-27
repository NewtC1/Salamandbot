import json
import os, os.path
import codecs

""" This script is intended to hold many utility functions that other scripts need access to."""

# ============================================ Default Settings ========================================================
vote_location = os.path.join(os.path.dirname(__file__), '..\\..\\Twitch\\Votes\\')


# ============================================ Helper Functions ========================================================
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
    # Parent.Log("update_vote_data", "Updated the file successfully.")

    return output


def get_active_profile():
    data = get_vote_data()
    return data["Active Profile"]