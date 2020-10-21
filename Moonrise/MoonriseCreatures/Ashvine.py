from DarkForestCreature import DarkForestCreature

"""Ashvine(60, 1.0, 30, 1.0, 60, 50), # dpm of 30."""


class Ashvine(DarkForestCreature):

    def __init__(self, delay=60, delayMulti=1.0, attack=30, attackMulti=1.0, health=60, reward=50,
                 incineration_resist=8):
        DarkForestCreature.__init__(self, delay, delayMulti, attack, attackMulti, health, reward, incineration_resist)

    def getAttack(self):
        retval = 'Attaching itself to the trees, the Ashvine contracts, pulling at the shields from all sides.'
        return retval

    def getCampfireAttack(self):
        self.setHealth(self.getHealth()*2)
        self.setReward(self.getReward() + 60)
        self.setAttackStrengthMulti(self.getAttackStrengthMulti()+0.5)
        retval = 'Growing through the dirt, the vines sprout underneath the central fire, throwing out ' + \
                 str(int(self.baseAttackStrength * self.attackStrengthMulti)) + \
                 ' logs into the surrounding Forest. But this time, the vines don\'t go away.'
        return retval

    def getSpawnMessage(self):
        retval = 'A column of smoke can be seen deep in the woods, even against the inky night sky. A purple glow' \
                 'answers the Campgrounds. A Cinder lurks in the darkness.'
        return retval

    def UseSpecialAbility(self):
        self.setHealth(int(self.getHealth()*2))
        self.setReward(self.getReward() + 60)
        self.setAttackStrengthMulti(self.getAttackStrengthMulti()+0.5)
        return "The Ashvine covers more of the Forest around the fire."
