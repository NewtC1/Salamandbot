import random

from DarkForestCreature import DarkForestCreature


class Imp(DarkForestCreature):

    riddles = {"What is Zephnos known for eating?": "The Moon",
               "What is the only friendly dark forest creature?": "The Ants",
               "The Ants gave Howie a sculpture of what?": "The Salamander",
               "Soil was born in what?": "Silver",
               "What was the first color Zephnos saw?": "Purple",
               "What really controls the Dark Forest?": "The Salamanderflame",
               "Who killed Zephnos?": "Bjorn",
               # "What are the names of the bear cubs Bjorn adopted?": "Villi and Ve",
               # "What is the first law of the Dark Forest?": "Do not enter the light of the campgrounds",
               # "What is the second law of the Dark Forest?": "Do not attempt to leave the Dark Forest",
               # "What is the third law of the Dark Forest?": "Kill any human who enters the Dark Forest",
               "Soil is who's daughter?": "Zephnos",
               }
    riddle = ""

    def __init__(self, delay=600, health=0, reward=0, inc_resist=1000):
        """
        Imps do not attack. They ask a question and if the answer is correct they incinerate themselves. Their reward or
        punishment is given later on, and is not specified when they are defeated.
        """
        DarkForestCreature.__init__(self, delay=delay, health=health, reward=reward, incineration_resist=inc_resist)
        self.set_riddle()

    def set_riddle(self):
        """
        Sets the riddle and reward and returns the reward phrase.
        Possible reward phrases include:
            "aegis" = add shield
            "Yanaviel" = restore
            "Soraviel" = kill creature
            "aggression" = attack
            "growth" = buff creature
            "decay" = splinter creature
            "dragon" = double base reward
        :return:
        """
        riddles_fix = self.riddles.keys()*2
        self.riddle = random.choice(riddles_fix)

        return

    def getAttack(self):
        """
        Returns the attack phrase. In this case the imp just asks the riddle.
        :return:
        """
        retval = "Oblivious to the fire trying to destroy it, " \
                 "the tiny creature chokes out a question between giggles: \"" + self.riddle + "\""

        return retval

    def check_answer(self, answer):
        """
        :param answer: The answer given in chat.
        :return:
        """
        good_phrases = ["aegis", "Yanaviel", "Soraviel", "decay", "dragon"]*2
        bad_phrases = ["aggression", "growth"]*2

        if answer.lower() in self.riddles[self.riddle].lower():
            return random.choice(good_phrases)
        else:
            return random.choice(bad_phrases)

    def getSpawnMessage(self):
        ret_val = 'An imp appears. It chortles to itself. "No, no, let me think about it. ' \
                  'I have a question somewhere..." ' \
                  'It spins in its indestructible bubble, paying no mind to the fires trying to send it home.'
        return ret_val