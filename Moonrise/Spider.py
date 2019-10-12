from DarkForestCreature import DarkForestCreature


class Spider(DarkForestCreature):

    def __init__(self, delay, delayMulti, attack, attackMulti, health, reward):
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