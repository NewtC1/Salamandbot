from DarkForestCreature import DarkForestCreature


class ShadowBoundBear(DarkForestCreature):

    def __init__(self, delay, delayMulti, attack, attackMulti, health, reward):
        DarkForestCreature.__init__(self, delay, delayMulti, attack, attackMulti, health, reward)


    def getAttack(self):
        retval = 'Darkness rippling over it\'s thick muscles, the bear stands and rends its foot long claws through the shield\'s thick bark.'
        return retval

    def getCampfireAttack(self):
        retval = 'The shadowy ursa takes a swipe at the fire, seemingly unnaffected by the flames. It knocks out ' + str(int(self.baseAttackStrength * self.attackStrengthMulti)) + ' logs.'
        return retval

    def getSpawnMessage(self):
        retval = 'Padding through the forest, the sound of a bear reaches the fire. Its roars sound oddly hollow.'
        return retval