
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

def getTrajectory(snakeCoordsList):
    if len(snakeCoordsList) < 2:
        return('up')
    xh = snakeCoordsList[0][0]
    yh = snakeCoordsList[0][1]
    x1 = snakeCoordsList[1][0]
    y1 = snakeCoordsList[1][1]
    if(xh > x1):
        return('right')
    elif(xh < x1):
        return('left')
    elif(yh > y1):
        return('down')
    else:
        return('up')
    
    