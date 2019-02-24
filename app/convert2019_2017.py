# Move Request converter -- Jon Knoll (C)2019
# This converts the BattleSnake move request from the 2019 format to the 2017 format
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


def convert(data):
    """
    Convert the 2019 JSON blob into a few simple structures
    """
    convDict = {}
    for key, val in data.items():
        if key == "game":
            convDict["game_id"] = val["id"]
      
        if key == "turn":
            convDict["turn"] = val
      
        if key == "board":
            convDict['height'] = val["height"]
            convDict['width'] = val["width"]
            convDict['food'] = convertCoordList(val["food"])
            convDict['snakes'] = convertSnakeList(val['snakes'])
            
        if key == "you":
            convDict["you"] = val["id"]

    return(convDict)


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
    snakeDict['health_points'] = obj['health']
    snakeDict['coords'] = convertCoordList(obj['body'])
    return snakeDict

def convertSnakeList(obj):
    myList = []
    for snakeDict in list(obj):
        myList.append(convertSnake(snakeDict))
    return myList
