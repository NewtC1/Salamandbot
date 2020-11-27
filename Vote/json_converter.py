from json import dump
from os import listdir, path, chmod

vote_dir = '..\\..\\Twitch\\Votes\\'
json_file = {}
for each in listdir(vote_dir):
    json_file[each] = {}
    if path.isdir(path.join(vote_dir, each)):
        for sub_file in listdir(path.join(vote_dir, each)):
            vote_file_dir = path.join(vote_dir, each, sub_file)
            name = sub_file.split('.')[0]
            print(each)

            if name != "votes":
                with open(vote_file_dir, 'r') as logpile:
                    # [vote_value, votes_list, suggestion(contributor_name),length_of_game, last_added]
                    json_file[each][name] = {"vote value": int(logpile.read()),
                                       "votes list": {},
                                       "contributor": "",
                                       "length of game": 0,
                                       "last added": 0}

        print json_file

        # chmod(path.join(vote_dir, each), stat.S_IWRITE)
        with open(path.join(vote_dir, "vote.json"), "w+") as vote_json:
            dump(json_file, vote_json, encoding='utf-8-sig', indent=2)

