import datetime
import json
import os.path

# directory paths
points_json = os.path.join(os.path.dirname(__file__), "points.json")


class CommunityChallenge():

    def __init__(self, name, end_date, success_count, maximum_input=0):
        self.end_date = end_date
        self.success_count = success_count
        self.maximum_input = maximum_input
        self.name = name
        self.current_count = 0

    def save_to_file(self):

        if os.path.exists(points_json):
            with open(points_json, "r") as f:
                data = json.load(f, encoding="utf-8-sig")
                if "challenges" not in data.keys():
                    data["challenges"] = {}

                data["challenges"][self.name] = {
                    "end date" : self.end_date,
                    "current count": int(self.current_count),
                    "success count": int(self.success_count),
                    "maximum input": self.maximum_input
                }

            with open(points_json, "w+") as f:
                output = json.dumps(data, f, indent=2, encoding='utf-8-sig')
                f.write(output)
            return True
        else:
            return False

    def __add__(self, other):
        if type(other) == int:
            if self.maximum_input > other:
                self.current_count += self.maximum_input
            else:
                self.current_count += other
            self.save_to_file()
        else:
            raise TypeError

    def __sub__(self, other):
        if type(other) == int:
            if self.maximum_input > other:
                self.current_count -= self.maximum_input
            else:
                self.current_count -= other
            self.save_to_file()
        else:
            raise TypeError
