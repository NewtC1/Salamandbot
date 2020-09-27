from DarkForestCreature import DarkForestCreature
"""Bunny(0,0,0,0,0, 1800)] # unspeakably evil"""


class Bunny(DarkForestCreature):

    def __init__(self, delay=0, delayMulti=0, attack=0, attackMulti=0, health=0, reward=100):
        DarkForestCreature.__init__(self, delay, delayMulti, attack, attackMulti, health, reward)


    def getAttack(self):
        retval = 'A most dangerous beast prowls outside the shields, too terrifying to even speak of. It\'s foot long teeth lust for your throats.'
        return retval

    def getCampfireAttack(self):
        retval = 'The vile creature yawns and curls up next to the fire.'
        return retval

    def getSpawnMessage(self):
        retval = 'A vicious beast comes towards the fire, filled with unspeakable evilness. It\'s eyes filled with hatred, and it\'s nose twitching in anger, it stalks ever closer.'
        return retval