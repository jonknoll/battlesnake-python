
def getMySnakeObj(data):
    myId = data['you']

    # fill with the living snakes
    for snake in data['snakes']:
        theId = snake['id']
        if(theId == myId):
            return(snake)
        
def getOurSnakeCoords(data):
    myId = data['you']
    for snake in data['snakes']:
        id = snake['id']
        if(id == myId):
            return(snake['coords'])

def getHeadCoord(snakeCoordsList):
    return(snakeCoordsList[0])