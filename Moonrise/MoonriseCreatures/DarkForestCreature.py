class DarkForestCreature:
    baseAttackDelay = 600
    attackDelayMulti = 1.0
    baseAttackStrength = 60
    attackStrengthMulti = 1.0
    health = 600
    reward = 600
    name = 'name'
    spawnMesage = ''

    def __init__(self, delay=600, delay_multi=1.0, attack=60, attack_multi=1.0, health=600, reward=600,
                 incineration_resist=0):
        self.baseAttackDelay = delay
        self.attackDelayMulti = delay_multi
        self.baseAttackStrength = attack
        self.attackStrengthMulti = attack_multi
        self.health = health
        self.reward = reward
        self.incineration_resist = incineration_resist

    def getBaseAttackDelay(self):
        return self.baseAttackDelay

    def getAttackDelayMulti(self):
        return self.attackDelayMulti

    def getBaseAttackStrength(self):
        return self.baseAttackStrength

    def getAttackStrengthMulti(self):
        return self.attackStrengthMulti

    def getHealth(self):
        return self.health

    def getReward(self):
        return self.reward

    def getName(self):
        return self.name

    def setBaseAttackDelay(self, delay):
        self.baseAttackDelay = delay

    def setAttackDelayMulti(self, multi):
        self.attackDelayMulti = multi

    def setBaseAttackStrength(self,attack):
        self.baseAttackStrength = attack

    def setAttackStrengthMulti(self, multi):
        self.attackStrengthMulti = multi

    def setHealth(self, health):
        self.health = health

    def setReward(self, reward):
        self.reward = reward

    def getAttack(self):
        retval = self.name + ' attacks the shield for ' + str(int(self.baseAttackStrength * self.attackStrengthMulti)) + '.'
        return retval

    def getCampfireAttack(self):
        retval = 'The shadowy critter takes a single stab at the fire before retreating. It does ' + str(int(self.baseAttackStrength * self.attackStrengthMulti)) + ' damage to the fire.'
        return retval

    def getSpawnMessage(self):
        retval = self.spawnMesage
        return retval

    def GetIncResist(self):
        return self.incineration_resist

    def SetIncResist(self, new_value):
        self.incineration_resist = new_value

    def UseSpecialAbility(self):
        return ""