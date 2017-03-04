import bottle
import os
import random
from grid import Grid
from gridhelper import *
from snakestuff import *

#Auto Deployed at http://jerksnake.herokuapp.com

# Values to put in grid, priorities TBD
OPEN_SPACE = '.'
ME_SNAKE = '#'
ME_HEAD = '*'
WALL = -1
FOOD = 'F'
OTHER_SNAKE = 'x'
OTHER_HEAD = '@'
EAT_THIS_HEAD = 'X'
ORTHAGONAL_HEAD = '+'
DIAGONAL_HEAD = '-'

#at what point
HUNGRYAT = 50;

# if none of these are options then don't change direction...gonna die
defensiveMoveList = [OPEN_SPACE, DIAGONAL_HEAD, ORTHAGONAL_HEAD]


def build_grid(data):
    height = data['height']
    width = data['width']
    myId = data['you']
    mySnakeObj = getMySnakeObj(data)

    grid = Grid(width, height, OPEN_SPACE)

    # fill with the living snakes
    for snake in data['snakes']:
        snakeId = snake['id']
        snakeCoords = snake['coords']
        
        # Determine what kind of snake we're looking at
        if(snakeId == myId):
            snakeType = ME_SNAKE
            snakeHeadType = ME_HEAD
        else:
            snakeType = OTHER_SNAKE
            if(len(snakeCoords) >= len(mySnakeObj['coords'])):
                snakeHeadType = OTHER_HEAD
            else:
                # snake is shorter than us, eat this head!
                snakeHeadType = EAT_THIS_HEAD

        # Snake body
        grid.setList(snakeCoords, snakeType)
        head = snakeCoords[0]

        # Snake head
        grid.set(head, snakeHeadType)

        # put a safety around the other snake heads
        if(snakeHeadType == OTHER_HEAD):
            orthList = grid.getOrthagonal(head)
            for coord in orthList:
                if(grid.get(coord) == OPEN_SPACE):
                    grid.set(coord, ORTHAGONAL_HEAD)
            
            diagList = grid.getDiagonal(head)
            for coord in diagList:
                if(grid.get(coord) == OPEN_SPACE):
                    grid.set(coord, DIAGONAL_HEAD)

    # fill with the dead snakes
    #for snake in data['dead_snakes']:
    #    grid.setList(snake['coords'], DEAD_SNAKE)

    # fill with food
    for food in data['food']:
        grid.setList(data['food'], FOOD)

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

def coordToDirection(currentCoord, proposedCoord):
    if((proposedCoord[0] - currentCoord[0]) == 1):
        direction = 'right'
    elif((proposedCoord[0] - currentCoord[0]) == -1):
        direction = 'left'
    elif((proposedCoord[1] - currentCoord[1]) == 1):
        direction = 'up'
    else:
        direction = 'down'
    return(direction)

#looks at what is in the spot and determines if safe to move there
def safetyCheck(grid, coord):
    whatIsHere = grid.get(coord)
    if(whatIsHere in [OPEN_SPACE, FOOD, EAT_THIS_HEAD, DIAGONAL_HEAD, ORTHAGONAL_HEAD]):
        return(True)
    else:
        return(False)




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
        'color': '#800000',
        'taunt': '{} ({}x{})'.format(game_id, board_width, board_height),
        'head_url': head_url,
        'name': 'JerkSnake'
    }


@bottle.post('/move')
def move():
    data = bottle.request.json
    grid = build_grid(data)
    ourSnake = getOurSnakeCoords(data)
    head = getHeadCoord(ourSnake)
    ourTrajectory = getTrajectory(ourSnake)

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

    
    direction = getDesiredDirection(ourTrajectory)
    
    directions = []
    if(safetyCheck(grid, [head[0]-1,head[1]]) == True):
        print("x-1,y = {}".format(grid.get([head[0]-1,head[1]])))
        directions.append('left')
    if(safetyCheck(grid, [head[0]+1,head[1]]) == True):
        print("x+1,y = {}".format(grid.get([head[0]+1,head[1]])))
        directions.append('right')
    if(safetyCheck(grid, [head[0],head[1]+1]) == True):
        print("x,y+1 = {}".format(grid.get([head[0],head[1]+1])))
        directions.append('down')
    if(safetyCheck(grid, [head[0],head[1]-1]) == True):
        print("x,y-1 = {}".format(grid.get([head[0],head[1]-1])))
        directions.append('up')

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
    if(ourTrajectory in directions):
        ourMove = ourTrajectory
    elif len(directions) == 0:
        ourMove = ourTrajectory
    else:
        ourMove = random.choice(directions)
    print("Our move is = {}".format(ourMove))


    return {
        'move': ourMove,
        'taunt': 'battlesnake-python!'
    }


# Expose WSGI app (so gunicorn can find it)
application = bottle.default_app()
if __name__ == '__main__':
    bottle.run(application, host=os.getenv('IP', '0.0.0.0'), port=os.getenv('PORT', '8080'))
