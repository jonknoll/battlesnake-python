
def getMySnakeObj(data):
    myId = data['you']

    # fill with the living snakes
    for snake in data['snakes']:
        theId = snake['id']
        if(theId == myId):
            return(snake)
        
def getOurSnakeCoords(data):
    """
    pass in global data object
    return a list of (x,y) tuples
    """
    myId = data['you']
    for snake in data['snakes']:
        if(snake['id'] == myId):
            return(snake['body'])

def getHeadCoord(snakeCoordsList):
    return(snakeCoordsList[0])

def getTailCoord(snakeCoordsList):
    return(snakeCoordsList[-1])

def getOurSnakeHealth(data):
    return(getMySnakeObj(data)["health"])

def getOtherSnakeList(data):
    myId = data['you']
    snakeList = []
    for snake in data["snakes"]:
        if(snake['id'] != myId):
            snakeList.append(snake)
    return(snakeList)

def getMyName(data):
    for snake in data["snakes"]:
        if data["you"] == snake["id"]:
            return snake["name"]

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

def compareSnake(snakeA, snakeB):
    lenA = len(snakeA['body'])
    lenB = len(snakeB['body'])
    if lenA > lenB:
        return(">")
    elif lenA < lenB:
        return("<")
    else:
        return("=")
    
def snakesLargerThanUs(data):
    ourSnake = getOurSnakeCoords(data)
    otherSnakesList = getOtherSnakeList(data)
    myName = getMyName(data)
    largerSnakes = 0
    for snake in otherSnakesList:
        if len(ourSnake) <= len(snake["body"]) and snake["name"][:7].lower() != myName[:7].lower():
            largerSnakes += 1
    return(largerSnakes)
    