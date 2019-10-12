from DarkForestCreature import DarkForestCreature

class Beast(DarkForestCreature):

    def __init__(self, delay, delayMulti, attack, attackMulti, health, reward):
        DarkForestCreature.__init__(self, delay, delayMulti, attack, attackMulti, health, reward)

    def getAttack(self):
        retval = 'The slavering beast claws at the shield, dealing ' + str(int(self.baseAttackStrength * self.attackStrengthMulti)) + ' damage.'
        return retval

    def getCampfireAttack(self):
        self.setAttackStrengthMulti(self.getAttackStrengthMulti() + 0.5)
        retval = 'With a howl of triumph, the beast slashes at the Salamander, knocking away ' + str(int(self.baseAttackStrength * self.attackStrengthMulti)) + ' logs from fire.'
        return retval

    def getSpawnMessage(self):
        retval = 'A howl echoes through the forest. An attack is coming.'
        return retval