from DarkForestCreature import DarkForestCreature


class Ashvine(DarkForestCreature):

    def __init__(self, delay, delayMulti, attack, attackMulti, health, reward):
        DarkForestCreature.__init__(self, delay, delayMulti, attack, attackMulti, health, reward)


    def getAttack(self):
        self.setHealth(int(self.getHealth()*1.3))
        self.setReward(self.getReward() + 60)
        self.setAttackStrengthMulti(self.getAttackStrengthMulti()+0.5)
        retval = 'Attaching itself to the trees, the Ashvine contracts, pulling at the shields from all sides.'
        return retval

    def getCampfireAttack(self):
        self.setHealth(self.getHealth()*2)
        self.setReward(self.getReward() + 60)
        self.setAttackStrengthMulti(self.getAttackStrengthMulti()+0.5)
        retval = 'Growing through the dirt, the vines sprout underneath the central fire, throwing out ' + str(int(self.baseAttackStrength * self.attackStrengthMulti)) + ' logs into the surrounding Forest. But this time, the vines don\'t go away.'
        return retval

    def getSpawnMessage(self):
        retval = 'An unusual sound emanates from the Forest... some sort of elastic?'
        return retval