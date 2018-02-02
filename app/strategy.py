import random
from grid import Grid
from gridhelper import *
from snakestuff import *



def executeStrategy(data):
    board = buildGrid(data)
    ourSnakeObj = getMySnakeObj(data)
    ourSnake = getOurSnakeCoords(data)
    head = getHeadCoord(ourSnake)
    ourTrajectory = getTrajectory(ourSnake)
    enemySnakes = getOtherSnakeCoordsList(data)

    board.printGrid()
    
    directions = ['up', 'down', 'left', 'right']
    ourMove = random.choice(directions)
    
    
    print("Our move is {}".format(ourMove))
    return(ourMove)



# Values to put in grid, priorities TBD
OPEN_SPACE = '.'
ME_SNAKE = '#'
ME_HEAD = '@'
ME_TAIL = '~'
WALL = -1
FOOD = '*'
#OTHER_SNAKE = 'o'
EATABLE_HEAD = 'o'
#EAT_THIS_HEAD = '$'
#ORTHOGONAL_HEAD = '+'
#DIAGONAL_HEAD = '-'
#CLOSE_TO_WALL = '?'
#TAIL = 'T'

NO_GO = 'X'
MAYBE_GO = 'x'

def buildGrid(data):
    """
    Each grid element is a tuple of data about that space:
    element0 -- friendly symbol that represents what is at this location.
    element1 -- num moves to get here, 0 if this space cannot be occupied
    element2 -- direction you would turn to get here, this is very useful at the
        end when you need to make a move based on your goal
    
    Fill the grid in layers from the most harmless thing to the most
    dangerous thing. Upper layers can overwrite lower layers. Numbers indicate
    same layer.
    """

    height = data['height']
    width = data['width']
    myId = data['you']
    mySnakeObj = getMySnakeObj(data)

    grid = Grid(width, height, OPEN_SPACE)
        
    # Food
    grid.setList(data['food'], FOOD)

    # Snake bodies
    for snake in data['snakes']:
        if(snake['id'] == myId):
            grid.setList(snake['coords'], ME_SNAKE)
            grid.set(snake['coords'][0], ME_HEAD)
            grid.set(snake['coords'][-1], ME_TAIL)
        else:
            # other snake bodies are always no-go
            if(len(snake['coords']) >= len(mySnakeObj['coords'])):
                # put a danger zone around the head of larger snake
                orthList = grid.getOrthagonal(snake['coords'][0])
                grid.setList(orthList, MAYBE_GO)
            else:
                # snake is shorter than us, eat this head!
                grid.set(snake['coords'][0], EATABLE_HEAD)
            # mark the tail as a potential move
            grid.set(snake['coords'][-1], MAYBE_GO)
        # rest of body is no-go
        grid.setList(snake['coords'][1:-1], NO_GO)

    return(grid)
