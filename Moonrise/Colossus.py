from DarkForestCreature import DarkForestCreature


class Colossus(DarkForestCreature):

    def __init__(self, delay, delayMulti, attack, attackMulti, health, reward):
        DarkForestCreature.__init__(self, delay, delayMulti, attack, attackMulti, health, reward)
        self.speed_cap = 1.0


    def getAttack(self):
        if self.speed_cap < self.getAttackDelayMulti():
            self.setAttackDelayMulti(self.getAttackDelayMulti()-0.5)
        retval = 'The colossus\' long arms raise high, then smash hard onto the oaken dome.'
        return retval

    def getCampfireAttack(self):
        if self.speed_cap < self.getAttackDelayMulti():
            self.setAttackDelayMulti(self.getAttackDelayMulti()-0.5)
        retval = 'A huge slam hits the Campground, scattering embers and sparks everywhere. ' \
                 'The Colossus quickly raises it\'s arms for another attack.'
        return retval

    def getSpawnMessage(self):
        retval = 'Massive footsteps echo through the trees. Something ancient this way comes.'
        return retval