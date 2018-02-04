import random
from grid import Grid
from gridhelper import *
from snakestuff import *

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


def executeStrategy(data):
    height = data['height']
    width = data['width']
    ourSnakeObj = getMySnakeObj(data)
    ourSnakeCoords = getOurSnakeCoords(data)
    ourTrajectory = getTrajectory(ourSnakeCoords)
    enemySnakes = getOtherSnakeCoordsList(data)
    maxSnakeMove = getMaxSnakeMove(data) 

    # Build Grid with symbols for different things
    symbolGrid = buildSymbolGrid(data)
    symbolGrid.printGrid()

    
    # Build grid that contains the number of moves that it would take to get
    # somewhere.
    distanceGrid = Grid3d(height, width, maxSnakeMove)
    #distanceGrid.printGrid()
    # Build grid that contains which direction the snake should go to get to
    # that coordinate.
    moveGrid = MoveGrid(height, width, None)
    #moveGrid.printGrid()
    
    
    # Get lists of stuff on the board
    noGoCoordsList = symbolGrid.getListOfType([ME_HEAD, ME_SNAKE, NO_GO])
    maybeGoCoordsList = symbolGrid.getListOfType([MAYBE_GO, ME_TAIL])
    barrierCoordsList = noGoCoordsList
    
    print("NO GO COORDS={}".format(noGoCoordsList))
    print("MAYBE GO COORDS={}".format(maybeGoCoordsList))
    print("BARRIER COORDS={}".format(barrierCoordsList))
    
    # build up the list of moves at each location
    ourHead = getHeadCoord(ourSnakeCoords)
    fillDistanceAndMoveGrids(distanceGrid, moveGrid, ourHead, barrierCoordsList)
    
    distanceGrid.printGrid(2)
    moveGrid.printGrid()
    
    
    # Decide on a direction
    ourMove = decisionTree(data, symbolGrid, distanceGrid, moveGrid)
        
    
    print("Our move is {}".format(ourMove))
    return(ourMove)


class Grid3d(Grid):
    """
    Class stores "3 dimentional" coordinates: [<x>, <y>, <direction>]
    """
    
    def getOrthogonalWithDirection(self, coord):
        coordsList3d = []
        right = (coord[0]+1, coord[1], 'R')
        left = (coord[0]-1, coord[1], 'L')
        down = (coord[0], coord[1]+1, 'D')
        up = (coord[0], coord[1]-1, 'U')
        if(self.get(right) != None):
            coordsList3d.append(right)
        if(self.get(left) != None):
            coordsList3d.append(left)
        if(self.get(down) != None):
            coordsList3d.append(down)
        if(self.get(up) != None):
            coordsList3d.append(up)
        return(coordsList3d)

    def getOrthogonalPreserveDirection(self, coord3d):
        coordsList3d = self.getOrthogonal(coord3d)
        for i in range(len(coordsList3d)):
            # add the original direction into the coordinates
            coordsList3d[i] = (coordsList3d[i][0], coordsList3d[i][1], coord3d[2])
        return(coordsList3d)
    
    def getOrthogonalFromList3d(self, inputList3d):
        coordsList3d = []
        for coord3d in inputList3d:
            orthList3d = self.getOrthogonalPreserveDirection(coord3d)
            for orthCoord3d in orthList3d:
                if orthCoord3d not in coordsList3d:
                    coordsList3d.append(orthCoord3d)
        return(coordsList3d)

class MoveGrid(Grid):
    def getMove(self, coord):
        val = self.get(coord)
        if(val == 'L'):
            return("left")
        elif(val == 'R'):
            return("right")
        elif(val == 'U'):
            return("up")
        else:
            return("down")
    
    def getMoveCounts(self):
        numLeft = len(self.getListOfType(['L']))
        numRight = len(self.getListOfType(['R']))
        numUp = len(self.getListOfType(['U']))
        numDown = len(self.getListOfType(['D']))
        return {"left":numLeft, "right":numRight, "up":numUp, "down":numDown}
    
    def getHighestMoveCount(self):
        moveCounts = self.getMoveCounts()
        return(max(moveCounts, key=moveCounts.get))





def buildSymbolGrid(data):
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

    # Snake heads
    for snake in data['snakes']:
        if(snake['id'] == myId):
            grid.setList(snake['coords'], ME_SNAKE)
            grid.set(snake['coords'][0], ME_HEAD)
            grid.set(snake['coords'][-1], ME_TAIL)
        else:
            # other snake bodies are always no-go
            if(len(snake['coords']) >= len(mySnakeObj['coords'])):
                # Bigger snake
                # put a danger zone around the head of larger snake
                orthList = grid.getOrthogonal(snake['coords'][0])
                grid.setList(orthList, MAYBE_GO)
            else:
                # snake is shorter than us. Positions around the head are
                # the goal, not the head itself, as the snake's head will not
                # be there on the next move.
                orthList = grid.getOrthogonal(snake['coords'][0])
                grid.setList(orthList, EATABLE_HEAD)
            # mark the tail as a potential move
            grid.set(snake['coords'][-1], MAYBE_GO)

    # Snake bodies other than tail
    # Must lay down after everything else, so it doesn't get overwritten
    for snake in data['snakes']:
        grid.setList(snake['coords'][:-1], NO_GO)
    return(grid)


def fillDistanceAndMoveGrids(distanceGrid, moveGrid, startingCoord, noGoCoords):
    maxMoves = distanceGrid.get((0,0))
    
    # make a list of all the coordinates to try this round
    # remove them if they are one of the no go coordinates
    stepList = distanceGrid.getOrthogonalWithDirection(startingCoord)
    #if len(stepList) == 0:
    #    return
    
    for stepNumber in range(1, maxMoves):
        coordsForNextStep = []
        #print("STEP {}".format(stepNumber))
        
        # Take out any new coordinates that overlap a no go coordinate.
        tempList = []
        for stepCoord in stepList:
            coord2d = (stepCoord[0], stepCoord[1])
            if coord2d not in noGoCoords:
                tempList.append(stepCoord)
            else: 
                #print("no go coord: {}".format(coord2d))
                pass
        stepList = tempList
        # if no coordinates to check out then we're done.
        if len(stepList) == 0:
            break
        
        #print("step {}: {}".format(stepNumber, stepList))
        # go through the coordinates and see if any of them are more optimal than
        # what is already there. If so, overwrite
        for stepCoord in stepList:
            if stepNumber < distanceGrid.get(stepCoord):
                distanceGrid.set(stepCoord, stepNumber)
                # update move grid
                moveGrid.set(stepCoord, stepCoord[2])
                # keep this coordinate for the next step
                coordsForNextStep.append(stepCoord)
        # Get the coordinates for the next step
        stepList = distanceGrid.getOrthogonalFromList3d(coordsForNextStep)
                
                    
def decisionTree(data, symbolGrid, distanceGrid, moveGrid):
    """
    Decisions for Snake:
    - Goals are: Food, Heads of smaller snakes, Chase our own tail
    - The direction is determined by whatever is the top goal for this round
    - The top priority is food if below the health threshold
    - The second priority is go for heads of smaller snakes
    - If health is good and no smaller snakes then chase tail
    - If none of the goals can be reached then see if any of our directions are
      in the "MAYBE_GO" list, if so, take it.
    - If there is no move available, then make a random choice and die.
    """
    maxSnakeMove = getMaxSnakeMove(data)
    ourMove = None
    ourSnakeLength = len(getOurSnakeCoords(data))
    
    # Priority #1 -- don't paint yourself into a corner
    moveDict = moveGrid.getMoveCounts()
    
        # Priority #2 -- stay healthy and try to be the biggest snake
    if(ourMove == None):
        health = getOurSnakeHealth(data)
        largerThanUs = snakesLargerThanUs(data)
        print("Health={}, snakes larger than us={}".format(health, largerThanUs))
        if (health < 75) or (largerThanUs > 0):
            foodCoordsList = symbolGrid.getListOfType([FOOD])
            numFood = len(foodCoordsList)
            if numFood != 0: # most likely
                foodToEat = foodCoordsList[0]
                if numFood > 1:
                    for coord in foodCoordsList:
                        if distanceGrid.get(coord) < distanceGrid.get(foodToEat):
                            foodToEat = coord
                if distanceGrid.get(foodToEat) < maxSnakeMove:
                    print("Decision: Eat food at {}, distance={}, move={}".format(foodToEat, distanceGrid.get(foodToEat), moveGrid.getMove(foodToEat)))
                    ourMove = moveGrid.getMove(foodToEat)
                else:
                    print("Decision: food at {}, no path to food".format(foodToEat))
            else:
                print("Desicion: no food!")
        # if no food or lots of health then move on
    
    # Priority #3 -- eat smaller snakes!
    if(ourMove == None):
        eatableSnakeHeadsList = symbolGrid.getListOfType([EATABLE_HEAD])
        numHeads = len(eatableSnakeHeadsList)
        if numHeads != 0: # most likely
            headToEat = eatableSnakeHeadsList[0]
            if numHeads > 1:
                for coord in eatableSnakeHeadsList:
                    if distanceGrid.get(coord) < distanceGrid.get(headToEat):
                        headToEat = coord
            if distanceGrid.get(headToEat) < maxSnakeMove:
                print("Decision: Eat head at {}, distance={}, move={}".format(headToEat, distanceGrid.get(headToEat), moveGrid.getMove(headToEat)))
                ourMove = moveGrid.getMove(headToEat)
        else:
            print("Desicion: no snakes to eat!")
    # if no snakes to eat then move on
    
    # Priority #4 -- chase tail!
    if(ourMove == None):
        myTail = getTailCoord(getOurSnakeCoords(data))
        if distanceGrid.get(myTail) < maxSnakeMove:
            print("Decision: Chase tail at {}, distance={}, move={}".format(myTail, distanceGrid.get(myTail), moveGrid.getMove(myTail)))
            ourMove = moveGrid.getMove(myTail)
        else:
            print("Decision: Can't get to tail!")
    
    # Nothing within reach! Better do some statistical checking
    # Go with whichever direction has the most coordinates marked
    if(ourMove == None):
        ourMove = max(moveDict, key=moveDict.get)
    
        if moveDict[ourMove] > 0:
            print("Decision: go with the majority (L={},R={},U={},D={}) move={}".format(moveDict['left'], moveDict['right'], moveDict['up'], moveDict['down'], ourMove))
        else:
            directions = ['up', 'down', 'left', 'right']
            ourMove = random.choice(directions)
            print("PANIC! No moves available! Going random: {}".format(ourMove))
    return(ourMove)
    
    
    



