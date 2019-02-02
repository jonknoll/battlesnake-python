# Move Request Simplifier -- Jon Knoll (C)2019
# This converts the BattleSnake move request from the 2019 format to a simpler
# format to work with (similar to the 2017 API)
# There's nothing special about this code so it is free to use.

# The 2019 format is a dictionary with the following format:
# {
# "game": {
   # "id": "game-id-string"
# },
# "turn": 4,
# "board": {
   # "height": 15,
   # "width": 15,
   # "food": [
      # {
         # "x": 1,
         # "y": 3
      # }
   # ],
   # "snakes": [
   # {
      # "id": "snake-id-string",
      # "name": "Sneky Snek",
      # "health": 90,
      # "body": [
         # {
            # "x": 1,
            # "y": 3
         # }
      # ]
   # }
   # ]
# },
# "you": {
   # "id": "snake-id-string",
   # "name": "Sneky Snek",
   # "health": 90,
   # "body": [
   # {
      # "x": 1,
      # "y": 3
   # }
   # ]
# }
# }

# The simplified object is a dictionary with the following format:
# {
# "game": <game-id-string>,
# "turn": <turn_number>,
# "height": <board height>,
# "width": <board width>,
# "food": [(x1,y1), (x2,y2), etc...]
# "snakes": [{
#   "id": "snake-id-string",
#   "name": "Sneky Snek",
#   "health": 90,
#   "body": [(x1,y1), (x2,y2), etc...]
# }, etc..
# ]
# "you": <id>
# }


def simplify(data):
    """
    Convert the 2019 JSON blob into a few simple structures
    """
    simpleDict = {}
    for key, val in data.items():
        if key == "game":
            simpleDict["game"] = val["id"]
      
        if key == "turn":
            simpleDict["turn"] = val
      
        if key == "board":
            simpleDict['height'] = val["height"]
            simpleDict['width'] = val["width"]
            simpleDict['food'] = convertCoordList(val["food"])
            simpleDict['snakes'] = convertSnakeList(val['snakes'])
            
        if key == "you":
            simpleDict["you"] = val["id"]

    return(simpleDict)


def convertPoint(coordDict):
    return (coordDict["x"], coordDict["y"])


def convertCoordList(obj):
    myList = []
    for coordDict in list(obj):
        myList.append(convertPoint(coordDict))
    return myList


def convertSnake(obj):
    snakeDict = {}
    snakeDict['id'] = obj['id']
    snakeDict['name'] = obj['name']
    snakeDict['health'] = obj['health']
    snakeDict['body'] = convertCoordList(obj['body'])
    return snakeDict

def convertSnakeList(obj):
    myList = []
    for snakeDict in list(obj):
        myList.append(convertSnake(snakeDict))
    return myList
