#Test File: BattleTemplate

import random, json, pprint
import Util
from Util import loadObject          

class Army:

    def __init__(self, morale, lines, unitDict, combatWidth = 0, status = "Fighting"):
        self.morale = morale
        self.lines = Util.CenteredTierList(combatWidth)
        self.status = status
        self.reserves = []
        for line in lines:
            lineList = []
            
            for unit in line:
                size = int(unit.split(':')[2])
                unitType = unit.split(':')[0]
                unitName = unit.split(':')[1]
                
                if (unitType == "Artillery"): maxUnitSize = 5
                else: maxUnitSize = 1000
                
                numUnits = int(size/maxUnitSize)
                
                blueprint = unitDict[unitType][unitName].copy()
                blueprint["name"] = unitName
                blueprint["status"] = status
                blueprint["morale"] = self.morale
                blueprint["__class__"] = unitType
                blueprint["__module__"] = "LandCombat"
                if (numUnits):
                    reserve = size - numUnits*maxUnitSize
                    
                else:
                    numUnits = 1
                    reserve = 0
                    
                for num in range(numUnits):
                    blueprint["size"] = (size - reserve)/numUnits
                    lineList.append(loadObject(blueprint.copy()))
                    
            self.lines.addTier(lineList)
    
    def size(self):
        return sum(self.results().values())
        
    def results(self):
        rtnDict = {"Morale": self.morale}
        for line in self.lines.tiers:
            for division in line:
                if (division.name not in rtnDict.keys()):
                    rtnDict[division.name] = 0
                    
                rtnDict[division.name] += division.size
        return rtnDict
                
    #Run through each combat phase, having this army attack the enemy for each phase
    def combat(self, enemy, defenseModifier, attackModifier):
        for i in range(10):
            #print(f"Phase {i}:")
            self.attack(enemy, defenseModifier, attackModifier)
            enemy.defend(self, defenseModifier, attackModifier)
            self.refresh("Attacking")
            enemy.refresh("Defending")
            
            if (self.morale < 25): 
                return("Defeat")
            
            elif (enemy.morale < 25):
                return("Victory")
                
        return("Inconclusive")
        
    def refresh(self, newStatus):
        numUnits = 1
        moraleSum = 0
        for lineNum in range(len(self.lines.tiers)):
            line = self.lines.tiers[lineNum]
            
            for divisionNum in range(len(line)):
                division = line[divisionNum]
                numUnits += 1
                
                if(division.morale >= 25):
                    division.status = newStatus
                    moraleSum += division.morale
                else:
                    line[divisionNum] = None
                    
        self.morale = int(moraleSum/numUnits)
        #Removes any lines if they are filled with None
        self.lines.trim()
    
    #One phase of combat    
    def attack(self, enemy, defenseModifier, attackModifier):
        #Goes through each line in this friendly army, front to back
        for lineNum in range(len(self.lines.tiers)):
            #This is the battle line we are iterating through
            line = self.lines.tiers[lineNum]
            
            #Goes through each division in this friendly line
            for divisionNum in range(len(line)):
                #This is the division that will be ordered to attack
                division = line[divisionNum]
                
                if (division == None): continue
                
                #sightLineNum is the position of the enemy tier list showing all of the divisions right in front of this one
                sightLineNum = int(len(line)/2) - len(line) + divisionNum
                
                #Choose this division's target. We are starting from right in front of the division we chose, so 0 will be passed as the original divisionDistance (distance from the starting division index).
                self.chooseTarget(division, sightLineNum, lineNum, enemy, defenseModifier, attackModifier)
    
    #Chooses a target for a division to attack.
    def chooseTarget(self, division, sightLineNum, lineNum, enemy, defenseModifier, attackModifier):
        #sightLine is the enemy tier list showing all of the divisions right in front of this one
        sightLine = enemy.lines[sightLineNum]
        if (all(item is None for item in sightLine)): #If all is none in this sightLine, attack the closest enemy flank
            if (sightLineNum < 0):
                division.attack(enemy.lines.tiers[0][0], 1, 1, defenseModifier, attackModifier)
            else:
                division.attack(enemy.lines.tiers[0][0], 1, 1, defenseModifier, attackModifier)
        
        else:
            #Goes from front to back in the sideline
            for depth in range(len(sightLine)):
                #If the distance is too great, end the loop
                if ((depth + lineNum + 1) > division.range):
                    #print(f"None in range: {sightLine[depth]} at range {depth} + {lineNum} + 1 = {depth + lineNum + 1}\n")
                    #if (division.__class__.__name__ == "Artillery"): print(f"Artillery! {depth + lineNum + 1}, {division.range}")
                    return False
               
                #If this is an empty division, skip it
                if (sightLine[depth] == None):
                    continue
                    
                #print(f"{division} vs. {sightLine[depth]}\n")
                division.attack(sightLine[depth], depth + lineNum + 1, defenseModifier, attackModifier)
                return True
    
    def defend(self, enemy, defenseModifier, attackModifier):
        #Goes through each line in this friendly army, front to back
        for lineNum in range(len(enemy.lines.tiers)):
            #This is the battle line we are iterating through
            line = enemy.lines.tiers[lineNum]
            
            #Goes through each division in this friendly line
            for divisionNum in range(len(line)):
                #This is the division that will be ordered to attack
                division = line[divisionNum]
                
                if ((division == None) or (division.status in ("Has Fought", "Has Been Attacked"))): continue
                
                #sightLineNum is the position of the enemy tier list showing all of the divisions right in front of this one
                sightLineNum = int(len(line)/2) - len(line) + divisionNum
                
                #Choose this division's target. We are starting from right in front of the division we chose, so 0 will be passed as the original divisionDistance (distance from the starting division index).
                enemy.chooseTarget(division, sightLineNum, lineNum, enemy, attackModifier, defenseModifier)
    
class Division:
    def __init__(self, name, size, morale, range, fire, cover, charge, shock, isMelee, status = "Fighting"):
        self.size = size
        self.name = name
        self.morale = morale
        self.range = range
        self.fire = fire
        self.cover = cover
        self.charge = charge
        self.shock = shock
        self.isMelee = isMelee
        self.status = status
    
    #Attacks another division, dealing and taking damage
    def attack(self, enemy, distance, flankingBonus = 0, defenseModifier = 0, attackModifier = 0):
        #The dice roll for the attack
        friendlyRoll = random.randint(1 + attackModifier, 5)
        #The dice roll for the defenders
        enemyRoll = random.randint(1 + defenseModifier, 5)
        
        #If it is a ranged attack:
        if ((distance > 1) or (not self.isMelee)):
            friendlyRoll = max(1, friendlyRoll + max(0, self.fire - enemy.cover) - defenseModifier + attackModifier)
            
            damageDone = (enemy.size * (friendlyRoll/100))
            
            enemy.morale *= ((enemy.size - damageDone)/max(1, enemy.size))
            enemy.morale = int(enemy.morale)
            
            enemy.size -= int(damageDone)
            
            self.status = "Has Fought"
        
        #If it is a melee attack:
        else:
            friendlyRoll += max(0, self.charge - enemy.shock) + attackModifier
            enemyRoll += max(0, enemy.shock - self.charge) + defenseModifier
            
            damageDone = max(1, (enemy.size * (friendlyRoll/100)))
            damageTaken = max(1, (self.size * (enemyRoll/100)))
            
            self.morale *= ((self.size - damageTaken)/max(1, self.size)) / max(0.25 * damageTaken / damageDone, 1)
            self.morale = int(self.morale)
            
            enemy.morale *= ((enemy.size - damageDone)/max(1, enemy.size)) / max(0.25 * damageDone / damageTaken, 1)
            enemy.morale = int(enemy.morale)
            
            enemy.size -= int(damageDone)
            self.size -= int(damageTaken)
            
            self.status = "Has Fought"
            enemy.status = "Has Been Attacked"
            
            #FOR TESTING
            '''
            print(f"Attacker ({self.name}) Size: {self.size}, Morale: {self.morale}")
            print(f"Defender ({enemy.name}) Size: {enemy.size}, Morale: {enemy.morale}")
            print()
            '''
    
    def __str__(self):
        return str(self.size) + " " + str(self.name) + ": " + self.status
        
class Infantry(Division):
    def __init__(self, name, size, morale, range, fire, cover, charge, shock, isMelee, status = "Fighting"):
        Division.__init__(self, name, size, morale, range, fire, cover, charge, shock, isMelee, status)
        
class Cavalry(Division):
    def __init__(self, name, size, morale, range, fire, cover, charge, shock, status = "Fighting"):
        Division.__init__(self, name, size, morale, range, fire, cover, charge, shock, True, status)
        
class Artillery(Division):
    def __init__(self, name, size, morale, range, firingSpeed, force, status = "Fighting"):
        Division.__init__(self, name, size, morale, range, 0, 0, 0, 0, False, status)
        self.firingSpeed = firingSpeed
        self.force = force
        
    def attack(self, enemy, distance, flankingBonus = 0, defenseModifier = 0, attackModifier = 0):
        #The dice roll for the attack
        friendlyRoll = max(1, random.randint(1, self.force*10) + max(0, self.force - enemy.cover) + flankingBonus - int(defenseModifier/2) + attackModifier)
        
        damageDone = ((enemy.size * (friendlyRoll/100)) * (1 + self.firingSpeed/10) * (self.size/100))*100
        
        enemy.morale *= ((enemy.size - damageDone)/max(1, enemy.size))
        enemy.morale = int(enemy.morale)
        
        enemy.size -= int(damageDone)
        
        self.status = "Has Fought"

#test("BattleTest1")

def test(fileName = "BattleTemplate"):
    print("TEST RUN")

    with open(f"Units.json", "r") as inFile:
        unitDict = json.load(inFile)

    with open(f"{fileName}.json", "r") as inFile:
        battleInfo = json.load(inFile)
        
    combatWidth = battleInfo["Battle Settings"]["Combat Width"]
    defenseModifier = battleInfo["Battle Settings"]["Total Defense Modifier"]
    attackerSize = defenderSize = atkMorale = defMorale = 0
    
    attacker = Army(battleInfo["Attacker"]["Morale"], battleInfo["Attacker"]["Lines"], unitDict, combatWidth, "Attacking") #Creates attacking army object
    defender = Army(battleInfo["Defender"]["Morale"], battleInfo["Defender"]["Lines"], unitDict, combatWidth, "Defending") #Creates defending army object
    
    attacker.combat(defender, defenseModifier)
    
    print("Attacking Army Sample:")
    print(attacker.results())
    
    print("Defending Army Sample:")
    print(defender.results())

#Bottom





























#Bottom 2 Electic Boogaloo