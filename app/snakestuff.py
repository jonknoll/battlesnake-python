
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
        if(snake['id'] == myId):
            return(snake['coords'])

def getHeadCoord(snakeCoordsList):
    return(snakeCoordsList[0])

def getOtherSnakeCoordsList(data):
    myId = data['you']
    snakeList = []
    for snake in data['snakes']:
        if(snake['id'] != myId):
            snakeList.append(snake['coords'])
    return(snakeList)