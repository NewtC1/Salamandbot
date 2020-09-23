from DarkForestCreature import DarkForestCreature
import time
import random

class Thunderjaw(DarkForestCreature):

    numberOfDelayedAttacks = 0
    DelayAttackTimer = 200
    DelayAttackDamage = 50
    UsedCharge = False
    PlasmaCannonCounter = 6
    WeaponSystem = 'stomp'

    def __init__(self, delay, delayMulti, attack, attackMulti, health, reward):
        DarkForestCreature.__init__(self, delay, delayMulti, attack, attackMulti, health, reward)
        self.setStomp()


    def getAttack(self):
        retval = ''
        if self.WeaponSystem == 'stomp':
            retval = 'The warmachine stomps its foot down and roars, challenging any who hear it.'
        if self.WeaponSystem == 'tail':
            retval = 'Winding up, the Thunderjaw suddenly pirouettes, bringing its bladed tail crashing into the sturdy trees.'
        if self.WeaponSystem == 'disk launcher':
            retval = 'The automaton plants its feet and a winding sound spews from the disk launchers on its back. Four disks launch from the cannons and hover in the air above the Campgrounds, raining down explosives onto the shielded shelter.'
        if self.WeaponSystem == 'plasma cannon':
            retval = '*plink*'
            self.PlasmaCannonCounter -= 1
        if self.WeaponSystem == 'charge':
            retval = 'The beast takes a step back, then charges toward the Campgrounds, slamming its armored hide into the shields.'

        if self.numberOfDelayedAttacks > 0:
            self.numberOfDelayedAttacks -= 1
            self.setBaseAttackStrength(self.getBaseAttackStrength() + (self.DelayAttackDamage*self.numberOfDelayedAttacks))
            retval += ' The disks fire rockets down at the shields. One of them is engulfed in flames and falls to the ground, smoking.'

        weapon = random.randint(1,5)

        if self.WeaponSystem == 'plasma cannon' and self.PlasmaCannonCounter > 0:
            self.setPlasmaCannon()
        else:
            self.selectWeapon()

        if self.PlasmaCannonCounter == 0:
            retval += ' The plasma cannons overheat and stop firing.'
            self.PlasmaCannonCounter = 6

        # set the next weapon
        return retval


    def getCampfireAttack(self):
        retval = ''
        if self.WeaponSystem == 'stomp':
            retval = 'The warmachine stomps its foot down and roars, challenging any who hear it.'
        if self.WeaponSystem == 'tail':
            retval = 'Winding up, the Thunderjaw suddenly pirouettes, bringing its bladed tail crashing into the sturdy trees.'
        if self.WeaponSystem == 'disc launcher':
            retval = 'The automaton plants its feet and a winding sound spews from the disk launchers on its back. Four disks launch from the cannons and hover in the air above the Campgrounds, raining down explosives onto the shielded shelter.'
        if self.WeaponSystem == 'plasma cannon':
            retval = '*plink*'
            self.PlasmaCannonCounter -= 1
        if self.WeaponSystem == 'charge':
            retval = 'The beast takes a step back, then charges toward the Campgrounds, slamming its armored hide into the shields.'
        return retval


    def getSpawnMessage(self):
        retval = 'Crashing through the trees, a gargantuan machine stampedes towards the light. Armored with alloys and armed with fire, it seeks only one thing: The destruction of the Campgrounds.'
        return retval


    # Launch 4 disks into the air which do small damage over time, decreasing by one every time the Thunderjaw attacks.
    def setDiskLauncher(self):
        self.numberOfDelayedAttacks = 4
        self.WeaponSystem = 'disk launcher'
        self.setBaseAttackStrength(0)

    def setPlasmaCannon(self):
        self.setBaseAttackDelay(5)
        self.setBaseAttackStrength(20)
        self.WeaponSystem = 'plasma cannon'

    # Deals huge damage, but puts a cooldown on the next attack.
    def setCharge(self):
        self.setBaseAttackStrength(800)
        self.UsedCharge = True
        self.WeaponSystem = 'charge'

    # Quick, light. Closest to a basic attack.
    def setStomp(self):
        self.setBaseAttackStrength(50)
        self.setAttackStrengthMulti(self.getAttackStrengthMulti() + 0.1)
        self.setBaseAttackDelay(50)
        self.WeaponSystem = 'stomp'

    # Deels heavy damage, no cooldwon,
    def setTailSweep(self):
        self.setBaseAttackStrength(500)
        self.setAttackStrengthMulti(1.0)
        self.WeaponSystem = 'tail'

    def selectWeapon(self):
        if weapon == 1:
            self.setStomp()
        if weapon == 2:
            self.setTailSweep()
        if weapon == 3:
            self.setDiskLauncher()
        if weapon == 4:
            self.setPlasmaCannon()
        if weapon == 5:
            self.setCharge()