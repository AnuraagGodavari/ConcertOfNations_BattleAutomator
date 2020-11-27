import LandCombat, json, traceback, pprint, Util, sys

testing = False

with open(f"Units.json", "r") as inFile:
    unitDict = json.load(inFile)

k = 1
while k > 0:
    k = 0
    #mainFileName = input("Please input the file you want read containing all the battle file names!\n")
    mainFileName = "TestBattles/Orders"

    try:
        mainFile = open(f"{mainFileName}.txt", 'r')
        
    except:
        print(f"Could not open {mainFileName}.txt!")
        end = input("\nPress ENTER to end program\n")
        exit()

    results = open(f"{mainFileName} results.txt", 'w')
        
    for fileName in mainFile:

        if ('\n' in fileName): fileName = fileName[:-1]
        
        if ("TEST:" in fileName): 
            fileName = fileName[5:]
            testing = True
            
        else: testing = False

        try:
        
            with open(f"{fileName}.json", 'r') as inFile:
                battleInfo = json.load(inFile)
                
        except:
            print(f"ERROR READING \"{fileName}.json\"!")
            pprint.pprint(traceback.format_exception(type(error), error, error.__traceback__))
            
            results.write(f"ERROR READING \"{fileName}.json\"!\n")
            results.write(str(traceback.format_exception(type(error), error, error.__traceback__)))
            continue

        try:
            combatWidth = battleInfo["Battle Settings"]["Combat Width"]
            defenseModifier = battleInfo["Battle Settings"]["Total Defense Modifier"]
            attackModifier = battleInfo["Battle Settings"]["Total Attack Modifier"]
            attackerSize = defenderSize = atkMorale = defMorale = 0

            attacker = LandCombat.Army(battleInfo["Attacker"]["Morale"], battleInfo["Attacker"]["Lines"], unitDict, combatWidth, "Attacking") #Creates attacking army object
            defender = LandCombat.Army(battleInfo["Defender"]["Morale"], battleInfo["Defender"]["Lines"], unitDict, combatWidth, "Defending") #Creates defending army object
            
        except:
            print(f"ERROR CREATING ARMIES OR READING \"{fileName}\"!")
            
            pprint.pprint(traceback.format_exception(type(error), error, error.__traceback__))
            
            results.write(f"ERROR CREATING ARMIES OR READING \"{fileName}\"!\n")
            results.write(str(traceback.format_exception(type(error), error, error.__traceback__)))
            continue
            
        try:
        
            if (testing):
                
                battleResults = f"\"{fileName}\" TEST Results:\n--------\n"
                
                avgAttack = {}
                avgDefend = {}
                
                attackerStart = attacker.results()
                defenderStart = defender.results()
                
                for i in range(100):
                
                    combatWidth = battleInfo["Battle Settings"]["Combat Width"]
                    defenseModifier = battleInfo["Battle Settings"]["Total Defense Modifier"]
                    attackModifier = battleInfo["Battle Settings"]["Total Attack Modifier"]
                    attackerSize = defenderSize = atkMorale = defMorale = 0

                    attacker = LandCombat.Army(battleInfo["Attacker"]["Morale"], battleInfo["Attacker"]["Lines"], unitDict, combatWidth, "Attacking") #Creates attacking army object
                    defender = LandCombat.Army(battleInfo["Defender"]["Morale"], battleInfo["Defender"]["Lines"], unitDict, combatWidth, "Defending") #Creates defending army object
                
                    attacker.combat(defender, defenseModifier, attackModifier)
                    
                    armyResults = attacker.results()
                    
                    for thing in armyResults:
                    
                        if thing not in avgAttack.keys(): avgAttack[thing] = 0
                        
                        avgAttack[thing] += armyResults[thing]
                        
                    armyResults = defender.results()
                    
                    for thing in armyResults:
                    
                        if thing not in avgDefend.keys(): avgDefend[thing] = 0
                        
                        avgDefend[thing] += armyResults[thing]
                    
                for avgDict in (avgAttack, avgDefend):
                    for thing in avgDict: avgDict[thing] /= 100
                    
                    if (avgDict == avgAttack): 
                    
                        battleResults += "Attacking Army Average Results:\n"
                        armyResults = avgAttack
                        armyInitial = attackerStart
                        
                    else: 
                        battleResults += "Defending Army Average Results:\n"
                        armyResults = avgDefend
                        armyInitial = defenderStart
                    
                    for thing in armyResults.keys():
                        battleResults += thing + ": " + str(armyResults[thing]) + " / " + str(armyInitial[thing]) + '\n'
                    
                    battleResults += '\n'
                    
                results.write(battleResults)
                    
            
            else:
                attacker.combat(defender, defenseModifier, attackModifier)
                
                battleResults = f"\"{fileName}\" Results:\n--------\n"
                
                for army in (attacker, defender):
                    armyResults = army.results()
                    
                    if (army == attacker): battleResults += "Attacking Army:\n"
                    else: battleResults += "Defending Army:\n"
                    
                    for thing in armyResults.keys():
                        battleResults += thing + ": " + str(armyResults[thing]) + '\n'
                    
                    battleResults += '\n'
                    
                results.write(battleResults)
            
        except Exception as error:
        
            pprint.pprint(traceback.format_exception(type(error), error, error.__traceback__))
            
            results.write(f"ERROR CREATING ARMIES OR READING \"{fileName}\"!\n")
            results.write(str(traceback.format_exception(type(error), error, error.__traceback__)))
        
            print(f"ERROR PERFORMING COMBAT BETWEEN ARMIES IN \"{fileName}.json\"!")
            results.write(f"ERROR PERFORMING COMBAT BETWEEN ARMIES IN \"{fileName}.json\"!\n")
            
            '''if testing: 
                mainFile.close()
                results.close()
                sys.exit()'''
            
            continue

    mainFile.close()
    results.close()
    
