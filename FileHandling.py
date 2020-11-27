import json, os, inspect, pprint
import Util, GameObjects, FileHandling, Mapping

#General methods

def newGame(gameName, serverID, password, startMonth, startYear, map, gameDict): #Creates a new saveFile
    
    if (map in os.listdir("Maps")) and (gameDict in os.listdir("Dictionaries")): #If the map and gameDict file names lead to existing files
        
        saveGame = GameObjects.SaveGame(gameName, serverID, password, GameObjects.Date(startMonth, startYear), map, gameDict) #Creates a SaveGame object
        
        with open(f"Savegames/{gameName} - {password} - {serverID}.json", 'w') as f: #Saves the SaveGame to a new file
            json.dump(saveObject(saveGame), f, indent = 4)
            
        return saveGame

# getNation(608117738183065641, None, 608113391747465227)
def getNation(nationID, gamePassword, serverID = None):
    if serverID != None:
        saveGame = getSaveGame(serverID)
    else:
        saveGame = getSaveGame(gamePassword)
    nation = loadObject(saveGame["Nations"][str(nationID)])
    return nation

def getSaveGame(ID):
    ID = str(ID)
    for file in os.listdir("Savegames"):
        if ID in file:
            with open(f"Savegames/{file}") as f:
                saveGame = json.load(f)
                return saveGame

#creates an object from a json or python dict
def loadObject(thing):
    
    if isinstance(thing, dict):
        for key in thing.keys():
            thing[key] = loadObject(thing[key])
        return toObject(thing)
    
    elif isinstance(thing, list):
        return list(map(lambda index: loadObject(index), thing))
        
    return thing

    
''' old loadObject
#creates an object from a json or python dict
def loadObject(thing):
    
    newThing = thing
    if isinstance(thing, dict):
        newThing = thing.copy()
        for param in thing.keys(): #For each top-level key in the old dictionary
            newThing[param] = toObject(newThing[param]) #turns into a custom object if possible, returns itself if impossible
            
            if isinstance(newThing[param], dict): #If the key's value is a dictionary
                for key in thing[param].keys(): 
                    if isinstance(newThing[param][key], dict): #If this key's value is a dictionary, try loading it as an object
                        newThing[param][key] = loadObject(newThing[param][key].copy())
                    else:
                        newThing[param][key] = loadObject(newThing[param][key])
            
            elif isinstance(newThing[param], list):
                for i in range(len(thing[param])):
                    newThing[param][i] = loadObject(newThing[param][i])
                    
    return toObject(thing)
'''

#d = saveObject(getNation(608117738183065641, None, 608113391747465227))
def saveObject(thing): #recursively turns a custom object, with object parameters and subparameters, into a dictionary
#used to be: def saveObject(thing, keys = None): 
    rtnDict = {}
    try:
        rtnDict = toDict(thing)
    except:
        if isinstance(thing, dict):
            rtnDict = thing
        elif isinstance(thing, list):
            rtnList = []
            for item in thing:
                rtnList.append(saveObject[item])
            return rtnList
        else:
            return thing
            
    for param in rtnDict.keys(): #For each thing in this new dictionary:
        if isinstance(rtnDict[param], list): #If thing is a list
            temp, rtnDict[param] = rtnDict[param], [] #Makes the list empty and refills it with built-in data types.
            for item in temp:
                rtnDict[param].append(saveObject(item))
        elif isinstance(rtnDict[param], dict): #If thing is a dict
            rtnDict[param] = saveObject(rtnDict[param])
        else:
            try: rtnDict[param] = saveObject(rtnDict[param]) #Tries to saveObject the thing, assuming it is a custom object
            except: pass
    
    return rtnDict

def toDict(thing): #Turns object into dict for json
  
  rtnDict = { #metadata for the dictionary
    "__class__": thing.__class__.__name__,
   "__module__": thing.__module__
  }
  
  rtnDict.update(thing.__dict__) #converts object parameters to a dict, combines with current dict
  
  return rtnDict

def toObject(thing): #Turns dict from json into object

    if (isinstance(thing, dict)):
        if ("__class__" in thing.keys()): #If dictionary and can be converted to non-dict object:
            class_name = thing.pop("__class__")
            module_name = thing.pop("__module__")
            module = __import__(module_name)
            class_ = getattr(module,class_name)
            
            obj = class_(**thing) #generate object
            return obj
        else:
            obj = thing
            return obj
        
    else: #if not a dictionary or is a dictionary but not convertable to non-dict object:
        obj = thing
        return obj

'''

class Territory:
    def __init__(self, name, terrain, claimable, resources, nation = None, projects = None, modifiers = None, coastal = False):


        "Magadha VIII": {
            "__class__": "Vertex",
            "__module__": "__main__",
            "name": "Magadha VIII",
            "coords": [
                350,
                200
            ],
            "edges": {
                "Magadha Star": 0
            },
            "details": {
                "Type": "OtherTerritory",
                "System": "Magadha",
                "Terrain": "Gaseous"
                "Resources": {}
            }
        }
'''