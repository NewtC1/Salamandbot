from DarkForestCreature import DarkForestCreature

"""Spider(60, 1.0, 15, 1.0, 100, 240), # dpm of 15"""

class Spider(DarkForestCreature):

    def __init__(self, delay=60, delayMulti=1.0, attack=15, attackMulti=1.0, health=100, reward=240):
        DarkForestCreature.__init__(self, delay, delayMulti, attack, attackMulti, health, reward)

    def getAttack(self):
        retval = 'Attaching powerful strands of silk to the shields, the spider pulls at the stubby trees, tearing chunks of wood out of them.'
        return retval

    def getCampfireAttack(self):
        retval = 'The spider strikes at the logs in the fire with a sticky strand of silk, managing to pull out ' + str(int(self.baseAttackStrength * self.attackStrengthMulti)) + ' logs.'
        return retval

    def getSpawnMessage(self):
        retval = 'A chittering sounds from the treetop. The spiders have come to pay their due.'
        return retval