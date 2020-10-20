from DarkForestCreature import DarkForestCreature

class SpiderQueen(DarkForestCreature):
    """
    The spider queen is a boss that surrounds herself in an ever replenishing swarm of spiders. The longer she's left
    alive, the more spiders she can spawn, and the harder it is for the fire to kill her.
    """

    def __init__(self, delay=40, delayMulti=1.0, attack=25, attackMulti=4.0, health=500, reward=2700,
                 incineration_resist=4):
        DarkForestCreature.__init__(self, delay, delayMulti, attack, attackMulti, health, reward, incineration_resist)
        self.spiders_count = 4

    def getAttack(self):
        retval = 'The spider queen webs up another chunk of shielding, yanking at it. The tree barely holds itself ' \
                 'in the ground, but you see its roots emerging. '
        if self.spiders_count > 0:
            retval += str(self.incineration_resist) + ' spiders follow their mother into the attack. One of them blocks the' \
                                                'fire\'s attack.'

        return retval

    def getCampfireAttack(self):
        retval = 'The queen doesn\'t even bother to attack. Swarms of spiders pull logs from the fire,' \
                 ' rapidly reducing its size.'
        return retval

    def getSpawnMessage(self):
        retval = 'The ever-present spider chitters increase in volume. Something answers their calls. Something big, ' \
                 'hungry, and angry.'
        return retval

    def get_spider_count(self):
        return self.spiders_count

    def set_spider_count(self, number):
        self.spiders_count = number

    def UseSpecialAbility(self):

        # set the spider count to match incineration resist
        return_value = "The spider queen calls more spiders to her side."
        self.incineration_resist += 1
        self.attackStrengthMulti = float(self.incineration_resist)

        return return_value
