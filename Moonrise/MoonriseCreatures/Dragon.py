from DarkForestCreature import DarkForestCreature
# Dragon(300, 1.0, 1000, 1.0, 2000, 3600),  # dpm of 200. Reward increases over time, difficult to kill.


class Dragon(DarkForestCreature):

    def __init__(self, delay=300, delayMulti=1.0, attack=800, attackMulti=1.0, health=900, reward=3600,
                 incineration_resist=2):
        DarkForestCreature.__init__(self, delay, delayMulti, attack, attackMulti, health, reward, incineration_resist)

    def getAttack(self):
        self.setReward(self.getReward() + 300)
        retval = 'Coiling around the shield, the dragon vomits green wildfire onto the wooden barrier.'
        return retval

    def getCampfireAttack(self):
        self.setReward(self.getReward() + 600)
        retval = 'The dragon\'s spiked tail sweeps across the fire, battering the Salamander into the ash. The massive attack knocks ' + str(int(self.baseAttackStrength * self.attackStrengthMulti)) + ' logs out of the fire.'
        return retval

    def getSpawnMessage(self):
        retval = 'A hissing emanates from deep in the forest. Something big is coming.'
        return retval