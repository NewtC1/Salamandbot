from json import dump
from os import listdir, path

vote_dir = '..\\..\\Twitch\\Votes\\'

# get the currently active profile and record it in the json
with open(path.join(vote_dir, "active.txt"), "r") as reader:
    active = reader.read()
json_file = {
    "Active Profile": active,
    "Profiles": {}}
for profile in listdir(vote_dir):
    if path.isdir(path.join(vote_dir, profile)):
        json_file["Profiles"][profile] = {}
        for sub_file in listdir(path.join(vote_dir, profile)):
            vote_file_dir = path.join(vote_dir, profile, sub_file)
            name = sub_file.split('.')[0].lower()

            if name != "votes":
                with open(vote_file_dir, 'r') as logpile:
                    # [vote_value, votes_list, suggestion(contributor_name),length_of_game, last_added]
                    json_file["Profiles"][profile][name] = {"vote value": int(logpile.read()),
                                       "votes list": {},
                                       "contributor": "",
                                       "length of game": 0,
                                       "last added": 0}

        print json_file

        # chmod(path.join(vote_dir, each), stat.S_IWRITE)
        with open(path.join(vote_dir, "vote.json"), 'w+') as vote_json:
            dump(json_file, vote_json, encoding='utf-8-sig', indent=2)

