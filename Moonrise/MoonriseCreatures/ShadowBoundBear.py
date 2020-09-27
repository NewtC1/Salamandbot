from DarkForestCreature import DarkForestCreature


"""ShadowBoundBear(120, 1.0, 60, 1.0, 300, 300), # dpm of 30"""
class ShadowBoundBear(DarkForestCreature):

    def __init__(self, delay=120, delayMulti=1.0, attack=60, attackMulti=1.0, health=300, reward=300):
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