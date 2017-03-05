import bottle
import os
import random
from grid import Grid
from gridhelper import *
from snakestuff import *
from taunt import *
from decisionGrid import *

#Auto Deployed at http://jerksnake.herokuapp.com

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

# if none of these are options then don't change direction...gonna die
defensiveMovePriorityList = [WALL, ME_SNAKE, OTHER_SNAKE, OTHER_HEAD, ORTHAGONAL_HEAD, DIAGONAL_HEAD, EAT_THIS_HEAD, OPEN_SPACE, FOOD] #, TARGET]


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



def getDesiredDirection(trajectory):
    # determine goal here!
    return(trajectory)
    

def priority(energy, heads):
    otherSnakeCloser = False
    ourCoord = heads[0]

    #THE NEAREST FOOD COORD TO HEAD MUST BE KNOWN!
    foodCoord = [0,0]
    movesToFood = distance(ourCoord, foodCoord)
    for enemyHead in range(1,len(heads)-1):
        #need a function to check distance between points
        if distance(enemyHead,foodCoord) < movesToFood:
            otherSnakeCloser = True
            break
        print('which head is closest to the food?')

    priority = {}
    if energy <= HUNGRYAT:
        priority.append({'hunger':nearestFood(headLocation)})
    else:
        priority = 'jerk'
    return priority

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



@bottle.route('/static/<path:path>')
def static(path):
    return bottle.static_file(path, root='static/')


@bottle.post('/start')
def start():
    data = bottle.request.json

    print("\nSNAKE START!")
    for k,v in data.iteritems():
        print("{}={}".format(k,v))
    print("SNAKE INFO:")


    game_id = data['game_id']
    board_width = data['width']
    board_height = data['height']

    head_url = '%s://%s/static/jerk.png' % (
        bottle.request.urlparts.scheme,
        bottle.request.urlparts.netloc
    )

    # TODO: Do things with data

    return {
        'color': nastyColour(),
        'taunt': '{} ({}x{})'.format(game_id, board_width, board_height),
        'head_url': head_url,
        'name': 'JerkSnake'
    }


@bottle.post('/move')
def move():
    data = bottle.request.json
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

    #desire = priority(energy, heads)


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
    # take a list of desired directions in from the goal algorithm
    # use current trajectory for now...
    ################################################################
    directionsToOurGoal = [ourTrajectory]


    # Get an ordered list of directions to try
    #directionsToTry = getDirectionsToTry(directionsToOurGoal)
    desiredTraj = desiredTrajectory(ourSnake, enemySnakes, data['food'], ourSnakeObj['health_points'])
    
    directionsToTry = getDirectionsToTry(desiredTraj)
    
    print("directions to try are = {}".format(directionsToTry))
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
    
    
    if(ourMove == None):
        print("Can't go anywhere! Maintain current trajectory")
        ourMove = ourTrajectory
    
    
#     directions = []
#     if(safetyCheck(grid, [head[0]-1,head[1]]) == True):
#         print("x-1,y = {}".format(grid.get([head[0]-1,head[1]])))
#         directions.append('left')
#     if(safetyCheck(grid, [head[0]+1,head[1]]) == True):
#         print("x+1,y = {}".format(grid.get([head[0]+1,head[1]])))
#         directions.append('right')
#     if(safetyCheck(grid, [head[0],head[1]+1]) == True):
#         print("x,y+1 = {}".format(grid.get([head[0],head[1]+1])))
#         directions.append('down')
#     if(safetyCheck(grid, [head[0],head[1]-1]) == True):
#         print("x,y-1 = {}".format(grid.get([head[0],head[1]-1])))
#         directions.append('up')

    #calculate area available to move from a point
        #if area == totalboardspace-sumOfAllSnakes
            #continue



    # inspect surroundings for bad moves
        #avoid locations with pointed corners
    # if nearest snake to nearest food go for the food
    # if snake head nearer than food go toward sweet spots until hungry
        # sweet spots are [0,2],[0,-2],[2,0],[-2,0],[1,1],[-1,1],[-1,-1],[1,-1]
    #

    # see if it's ok to keep going the direction we are going
#     if(ourTrajectory in directions):
#         ourMove = ourTrajectory
#     elif len(directions) == 0:
#         ourMove = ourTrajectory
#     else:
#         ourMove = random.choice(directions)
        
        
    print("Our move is = {}".format(ourMove))


    return {
        'move': ourMove,
        'taunt': 'battlesnake-python!'
    }


# Expose WSGI app (so gunicorn can find it)
application = bottle.default_app()
if __name__ == '__main__':
    bottle.run(application, host=os.getenv('IP', '0.0.0.0'), port=os.getenv('PORT', '8080'))
