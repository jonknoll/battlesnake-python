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

    board.printGridElement(0)
    
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
FOOD = 'F'
#OTHER_SNAKE = 'o'
EATABLE_HEAD = 'o'
#EAT_THIS_HEAD = '$'
#ORTHOGONAL_HEAD = '+'
#DIAGONAL_HEAD = '-'
#CLOSE_TO_WALL = '?'
#TAIL = 'T'

NO_GO = 'X'
MAYBE_GO = '+'

def buildGrid(data):
    """
    Each grid element is a tuple of data about that space:
    element0 -- friendly symbol that represents what is at this location.
    element1 -- num moves to get here, 0 if this space cannot be occupied
    element2 -- direction you would turn to get here, this is very useful at the
        end when you need to make a move based on your goal
    
    """

    height = data['height']
    width = data['width']
    myId = data['you']
    mySnakeObj = getMySnakeObj(data)

    grid = Grid(width, height, OPEN_SPACE)
    
    # First fill the grid with one value (element0) at each location. This
    # makes it easy to put stuff from the JSON blob into the grid.
        
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
                # Bigger snake, head is NO GO
                grid.set(snake['coords'][0], NO_GO)
                # put a danger zone around the head of larger snake
                orthList = grid.getOrthogonal(snake['coords'][0])
                grid.setList(orthList, MAYBE_GO)
            else:
                # snake is shorter than us, eat this head!
                grid.set(snake['coords'][0], EATABLE_HEAD)
            # mark the tail as a potential move
            grid.set(snake['coords'][-1], MAYBE_GO)
        # rest of body is no-go
        grid.setList(snake['coords'][1:-1], NO_GO)


    # This is the theoretical maximum number of moves that it could take to
    # get to a location (all the way around the outside perimeter). Using this
    # number instead of like MAX_INT
    maxSnakeMove = (height + width) * 2

    # Now populate the grid with a list at each location (default values first)
    for y in range(height):
        for x in range(width):
            symbol = grid.get((x, y))
            grid.set((x, y), [symbol, maxSnakeMove, None])

    return(grid)
