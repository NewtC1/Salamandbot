from DarkForestCreature import DarkForestCreature
import random

# Thunderjaw(1, 1.0, 5, 1.0, 600, 50)


class Thunderjaw(DarkForestCreature):

    numberOfDelayedAttacks = 0
    DelayAttackTimer = 200
    DelayAttackDamage = 50
    UsedCharge = False
    PlasmaCannonCounter = 6
    WeaponSystem = 'stomp'

    def __init__(self, delay=50, delayMulti=2.0, attack=50, attackMulti=1.0, health=800, reward=2700,
                 incineration_resist=3):
        DarkForestCreature.__init__(self, delay, delayMulti, attack, attackMulti, health, reward, incineration_resist)
        self.setStomp()

    def getAttack(self):
        """Returns the attack message"""
        attacks = [self.setStomp, self.setTailSweep, self.setDiskLauncher, self.setPlasmaCannon, self.setCharge]
        retval = ''
        if not self.UsedCharge:
            if self.WeaponSystem == 'stomp':
                retval += 'The warmachine stomps its foot down and roars, challenging any who hear it. '
                attacks = [self.setCharge, self.setTailSweep, self.setDiskLauncher, self.setPlasmaCannon]
            if self.WeaponSystem == 'tail':
                retval += 'Winding up, the Thunderjaw suddenly pirouettes, ' \
                         'bringing its bladed tail crashing into the sturdy trees.'
                attacks = [self.setStomp, self.setDiskLauncher, self.setPlasmaCannon, self.setCharge]
            if self.WeaponSystem == 'disk launcher':
                retval += 'The automaton plants its feet and a winding sound spews from the disk launchers on its back. ' \
                         'Four disks launch from the cannons and hover in the air above the Campgrounds, ' \
                         'raining down explosives onto the shielded shelter.'
                attacks = [self.setPlasmaCannon, self.setStomp, self.setTailSweep, self.setCharge]
            if self.WeaponSystem == 'plasma cannon':
                retval += '*plink*'
                self.PlasmaCannonCounter -= 1
            if self.WeaponSystem == 'charge':
                retval += 'The beast takes a step back, then charges toward the Campgrounds, ' \
                         'slamming its armored hide into the shields.'
                self.UsedCharge = True
                attacks = [self.setStomp, self.setTailSweep, self.setDiskLauncher, self.setPlasmaCannon]

            if self.numberOfDelayedAttacks > 0:
                self.numberOfDelayedAttacks -= 1
                self.setBaseAttackStrength(self.getBaseAttackStrength() + (self.DelayAttackDamage*self.numberOfDelayedAttacks))
                retval += ' The disks fire rockets down at the shields. ' \
                          'One of them is engulfed in flames and falls to the ground, smoking.'

            if self.WeaponSystem == 'plasma cannon' and self.PlasmaCannonCounter > 0:
                self.setPlasmaCannon()
            else:
                random.choice(attacks)()

            if self.PlasmaCannonCounter == 0:
                retval += ' The plasma cannons overheat and stop firing.'
                self.PlasmaCannonCounter = 6
        else:
            retval += 'The Thunderjaw stops to recover from its charge.'
            self.UsedCharge = False
            attacks = [self.setStomp, self.setTailSweep, self.setDiskLauncher, self.setPlasmaCannon]
            random.choice(attacks)()

        # set the next weapon
        return retval

    def getCampfireAttack(self):
        # set the next weapon
        return self.getAttack()

    def getSpawnMessage(self):
        retval = 'Crashing through the trees, a gargantuan machine stampedes towards the light. ' \
                 'Armored with alloys and armed with fire, it seeks only one thing: The destruction of the Campgrounds.'
        return retval

    def setDiskLauncher(self):
        """Launch 4 disks into the air which do small damage over time,
        decreasing by one every time the Thunderjaw attacks."""
        self.numberOfDelayedAttacks = 4
        self.WeaponSystem = 'disk launcher'
        self.setBaseAttackStrength(0)
        self.setBaseAttackDelay(50)

    def setPlasmaCannon(self):
        """Sets a very low cooldown repeated attack that does low damage."""
        self.setBaseAttackDelay(5)
        self.setBaseAttackStrength(20)
        self.WeaponSystem = 'plasma cannon'

    def setCharge(self):
        """Deals huge damage, but puts a cooldown on the next attack"""
        self.setBaseAttackStrength(800)
        self.setBaseAttackDelay(100)
        self.WeaponSystem = 'charge'

    # Quick, light. Closest to a basic attack.
    def setStomp(self):
        self.setBaseAttackStrength(50)
        self.setAttackStrengthMulti(self.getAttackStrengthMulti() + 0.1)
        self.setBaseAttackDelay(50)
        self.WeaponSystem = 'stomp'

    # Deals heavy damage, no cool down, resets attack multiplier
    def setTailSweep(self):
        self.setBaseAttackStrength(500)
        self.setAttackStrengthMulti(1.0)
        self.setBaseAttackDelay(50)
        self.WeaponSystem = 'tail'
