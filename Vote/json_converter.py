from json import load, dump
from os import listdir
import codecs

vote_dir = '../../Twitch/Votes/'
json_file = {}
for each in listdir(vote_dir):
    name = each.split('.')[0]
    print(each)

    if name != "votes":
        with open(vote_dir+each, 'r') as logpile:
            # [vote_value, votes_list, suggestion(contributor_name),length_of_game]
            json_file[name] = {"vote value": int(logpile.read()),
                               "votes list": {},
                               "contributor":"",
                               "length of game": 0}

print json_file

with open(vote_dir+"votes.json", "w+") as vote_json:
    dump(json_file, vote_json, encoding='utf-8-sig', indent=2)