from grid import Grid


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
    


# Values to put in grid, priorities TBD
OPEN_SPACE = '.'
ME_SNAKE = '#'
ME_HEAD = '@'
WALL = -1
FOOD = 'F'
OTHER_SNAKE = 'o'
OTHER_HEAD = 'H'
EAT_THIS_HEAD = '$'
ORTHAGONAL_HEAD = '+'
DIAGONAL_HEAD = '-'
CLOSE_TO_WALL = '?'
TAIL = 'T'

TARGET = 'T'

#at what point
HUNGRYAT = 50;

def build_grid(data):
    """
    Fill the grid in layers from the most harmless thing to the most
    dangerous thing. Upper layers can overwrite lower layers. Numbers indicate
    same layer.
    
    0-CLOSE_TO_WALL
    0.5-FOOD
    1-DIAGONAL_HEAD -- not bothering with this now
    1-ORTHAGONAL_HEAD
    2-ME_HEAD
    2-EAT_THIS_HEAD
    2-OTHER_HEAD
    3-OTHER_SNAKE
    3-ME_SNAKE
    """
    height = data['height']
    width = data['width']
    myId = data['you']
    mySnakeObj = getMySnakeObj(data)

    grid = Grid(width, height, OPEN_SPACE)
    
    # 0-CLOSE_TO_WALL
    for x in range(width):
        grid.set([x,0], CLOSE_TO_WALL)
        grid.set([x,height-1], CLOSE_TO_WALL)
    for y in range(height):
        grid.set([0,y], CLOSE_TO_WALL)
        grid.set([width-1,y], CLOSE_TO_WALL)
        
    # 0.5-FOOD
    grid.setList(data['food'], FOOD)
        

    # 1-ORTHAGONAL_HEAD positions
    for snake in data['snakes']:
        snakeCoords = snake['coords']
        head = snakeCoords[0]
        orthList = grid.getOrthagonal(head)
        
        # Determine the kind of snake we're looking at
        if(snake['id'] == myId):
            snakeHeadType = ME_HEAD
        else:
            if(len(snakeCoords) >= len(mySnakeObj['coords'])):
                snakeHeadType = OTHER_HEAD
            else:
                # snake is shorter than us, eat this head!
                snakeHeadType = EAT_THIS_HEAD
        
        # put a safety around the other snake heads in the positions the
        # snake may travel to next (orthagonal positions)
        if(snakeHeadType == OTHER_HEAD):
            grid.setList(orthList, ORTHAGONAL_HEAD)
        elif(snakeHeadType == EAT_THIS_HEAD):
            # Speacial case. This is the head of a snake that is smaller than
            # us. Therefore we are not afraid to hit it head on. Hitting its
            # head from the side can cause death because it might turn away,
            # but head on is safe, so only populate a safety in the blocks
            # that are not directly in front of the snake's mouth.
            traj = getTrajectory(snake['coords'])
            trajCoord = dirToCoord(head, traj)
            for coord in orthList:
                if(coord != trajCoord):
                    grid.set(coord, ORTHAGONAL_HEAD)
    
    
    # 2-ME_HEAD, EAT_THIS_HEAD, OTHER_HEAD
    for snake in data['snakes']:
        snakeCoords = snake['coords']
        head = snakeCoords[0]
        
        # Determine the kind of snake we're looking at
        if(snake['id'] == myId):
            snakeHeadType = ME_HEAD
        else:
            if(len(snakeCoords) >= len(mySnakeObj['coords'])):
                snakeHeadType = OTHER_HEAD
            else:
                # snake is shorter than us, eat this head!
                snakeHeadType = EAT_THIS_HEAD
        grid.set(head, snakeHeadType)
    
    
    # Snake bodies (only put down the coordinates after the head)
    for snake in data['snakes']:
        snakeCoords = snake['coords']
        if(snake['id'] == myId):
            # remove head (already populated) AND remove tail because
            # moving into the space our tail occupies is OK
            newSnakeCoords = snakeCoords[1:]
            newSnakeCoords = newSnakeCoords[:-1]
            grid.setList(newSnakeCoords, ME_SNAKE)
        else:
            newSnakeCoords = snakeCoords[1:]
            grid.setList(newSnakeCoords, OTHER_SNAKE)
            # mark the tail as a potential move
            grid.set(snakeCoords[-1], TAIL)

    return(grid)


#looks at what is in the spot and determines if safe to move there
def safetyCheck(grid, coord):
    whatIsHere = grid.get(coord)
    if(whatIsHere in [OPEN_SPACE, FOOD, DIAGONAL_HEAD]):
        return('OK')
    elif(whatIsHere in [ORTHAGONAL_HEAD, CLOSE_TO_WALL]):
        return('CAUTION')
    elif(whatIsHere in [EAT_THIS_HEAD, TAIL]):
        return('DANGER')
    else:
        return('NO')

