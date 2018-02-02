import random
from grid import Grid
from gridhelper import *
from snakestuff import *



def executeStrategy(data):
    grid = build_grid(data)
    ourSnakeObj = getMySnakeObj(data)
    ourSnake = getOurSnakeCoords(data)
    head = getHeadCoord(ourSnake)
    ourTrajectory = getTrajectory(ourSnake)
    enemySnakes = getOtherSnakeCoordsList(data)

    #This needs to be all snake heads
    #heads = [ourCoord]
    #for each snake head append to heads list
    #energy = data['health_points']


    print("!SNAKE MOVE!")
    print("ourSnake={}".format(ourSnake))
#     for k,v in data.iteritems():
#         print("{}={}".format(k,v))
#     snakedata = data['snakes']
#     for snake in snakedata:
#         print("SNAKE!")
#         for k,v in snake.iteritems():
#             print("{}={}".format(k,v))
#     print("\n\n")
    grid.printGrid('.')
    print("\nWe are at {}".format(head))
    print("our trajectory={}".format(ourTrajectory))

    # TODO: Do things with data

    ################################################################
    # Offense: Take a list of desired directions in from the goal algorithm
    ################################################################
    
    # Simple test goal: keep on our current trajectory
    #desiredTraj = [ourTrajectory]
    
    # Slightly more interesting goal: pick a random direction
    #desiredTraj = random.choice([['up'], ['down'], ['left'], ['right']])

    # Jerk snake goal: go to heads of other snakes, or eat food
    desiredTraj = desiredTrajectory(ourSnake, enemySnakes, data['food'], ourSnakeObj['health_points'])
    
    # Get an ordered list of directions to try
    directionsToTry = getDirectionsToTry(desiredTraj)
    print("directions to try are = {}".format(directionsToTry))
    
    ################################################################
    # Defense: Rank directions in terms of risk, and take the lowest risk move
    ################################################################
    # Check this against our direction algorithm and eliminate invaid
    # directions
    ourMove = None
    ourMoveSafety = None
    for direction in directionsToTry:
        coord = dirToCoord(head, direction)
        result = safetyCheck(grid, coord)
        if(result == 'OK'):
            print("direction {} status {}".format(direction, result))
            ourMove = direction
            ourMoveSafety = result
            # good to go, leave now
            break;
        elif(result == 'CAUTION'):
            print("direction {} status {}".format(direction, result))
            if(ourMoveSafety != 'CAUTION'):
                ourMove = direction
                ourMoveSafety = result
        elif(result == 'DANGER'):
            print("direction {} status {}".format(direction, result))
            if(ourMoveSafety == None):
                ourMove = direction
                ourMoveSafety = result
        else:   # NO
            print("direction {} status {}".format(direction, result))
            # don't even bother suggesting it as a move
            continue            
    
    # No move is valid! We gonna die! Just head straight on.
    if(ourMove == None):
        print("Can't go anywhere! Maintain current trajectory")
        ourMove = ourTrajectory
                
    print("Our move is = {}".format(ourMove))
    return(ourMove)





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






"""
EAT_THIS_HEAD <- this is a vulnerable head go into danger zones
    if a EAT_THIS_HEAD is overlapped by a head we need to pay attention to threat first

head coordinates
food pellets coordinates
energy remaining

next target

how to get there

return desired target coordinate
"""

#at what number does the snake get hungy?
HUNGRYAT = 50;

def howDoIgetThere(me, target):
    directions = []

    myX = me[0]
    myY = me[1]

    targetX = target[0]
    targetY = target[1]

    # my x coordinate is less so go down
    if myX < targetX:
        directions.append('right')
    elif myX > targetX:
        directions.append('left')

    if myY < targetY:
        directions.append('down')
    elif myY > targetY:
        directions.append('up')

    #randomer
    return directions


def desiredTrajectory(mySnake, enemySnakes, food, energy):
    """
    This is the goal algorithm. It looks at us vs enemy snakes, food and
    energy and determines a priority. The general priority is:
    - get in the face of snakes that are smaller than us
    - if the food is <= HUNGRYAT then stop bugging snakes and look for food
    """
    myHead = mySnake[0]
    enemySnakeHeads = []
    for enemySnake in enemySnakes:
        #if the length of the enemy snake is less then good
        if len(enemySnake) < len(mySnake):
            enemySnakeHeads.append(enemySnake[0])

    #am i hungry? If so go to food.
    if energy <= HUNGRYAT:
        #-- Get food code priority -- food
        #get list of food points
        #generate return direction to go toward food
        #you are the food! GET FOOD
        return howDoIgetThere(myHead, closest(myHead, food))
    elif len(enemySnakeHeads) == 0:
        return howDoIgetThere(myHead, closest(myHead, food))
    else:
        #--Find kill point priority -- kill!
        #if distance(me, closest(me,enemySnakeHeads)) == 3:
            #this is close quarters rules. Be sure to be a jerk
            #try to keep the distance at 3
            #if the distance to the snakehead is less than 2 move away
        #    print('close quarters combat')
        #get list of snake heads
        #get closest head
        return howDoIgetThere(myHead, closest(myHead,enemySnakeHeads))

    #me is [x,y] for our head
        #heads is [[x,y],[x,y]]
        #food is [[x,y],[x,y]]
        #energy is an int but has to come from main.py consider adding another param
    # write moves on a 5x5 grid
        # mark sweet spots
        # mark high risk spots
        # mark no entry spots
    #check for triangles of doom
    #determine most threatening move

    return random.choice(['left','right','up','down'])

#def desiredTrajectory(me, heads, food, energy):



def getDirectionsToTry(desiredDir):
    directions = ['up', 'down', 'left', 'right']
    priorityList = []
    priorityList.append(desiredDir[0])
    directions.remove(desiredDir[0])
    
    if(len(desiredDir) > 1):
        priorityList.append(desiredDir[1])
        directions.remove(desiredDir[1])
    else:
        if(desiredDir[0] == 'left') or (desiredDir[0] == 'right'):
            randChoice = random.choice(['up', 'down'])
            priorityList.append(randChoice)
            directions.remove(randChoice)
        else:
            randChoice = random.choice(['left', 'right'])
            priorityList.append(randChoice)
            directions.remove(randChoice)
    randChoice = random.choice(directions)
    priorityList.append(randChoice)
    directions.remove(randChoice)
    priorityList.append(directions[0])
    return(priorityList)




#Supa dank insult
def taunt():

    #List of dank insults
    dankInsults = ['Cant heck this snek',
    'No step on snek',
    'Imma do you a frighten',
    'Am Scary Cober',
    'Dont tread on REEEEE',
    'If your mom was a collection class, her insert method would be private',
    'Your mom was is so fat that she turned a binary tree into a linked list in constant time',
    'They told me to refactor my code, so I will refactor their sneks']

    #Got em!
    return (random.choice(dankInsults))


#Void parameterless function that will print an ugly hex number
#Doing me a hex
def nastyColour():

    #A list of fugly hex colours
    disgustingColours = [ '#00ff00', '#ffff00', '#4a412a', '#00ffff', '#ff0000', '#ff0066', '#ff00ff']

    #Ehmergehd, muh i's
    return (random.choice(disgustingColours))
