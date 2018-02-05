import random
from grid import Grid
from gridhelper import *
from snakestuff import *

# Values to put in grid, priorities TBD
OPEN_SPACE = '.'
FOOD = 'F'
ME_HEAD = '@'
ME_SNAKE = '#'
ME_TAIL = '~'
EATABLE_HEAD_ZONE = 'H'
OTHER_HEAD = 'O'
OTHER_BODY = 'o'
MAYBE_GO = '+'
#EAT_THIS_HEAD = '$'
#ORTHOGONAL_HEAD = '+'
#DIAGONAL_HEAD = '-'
#CLOSE_TO_WALL = '?'
#TAIL = 'T'
#NO_GO = 'X'
#WALL = -1


def executeStrategy(data):
    height = data['height']
    width = data['width']
    ourSnakeObj = getMySnakeObj(data)
    ourSnakeCoords = getOurSnakeCoords(data)
    ourTrajectory = getTrajectory(ourSnakeCoords)
    enemySnakes = getOtherSnakeCoordsList(data)

    # Build Grid with symbols for different things
    symbolGrid = buildSymbolGrid(data)
    symbolGrid.printGrid()

    maxSnakeMove = symbolGrid.getMaxSnakeMove() 
    
    # Build grid that contains the number of moves that it would take to get
    # somewhere.
    distanceGrid = Grid3d(height, width, maxSnakeMove)
    #distanceGrid.printGrid()
    # Build grid that contains which direction the snake should go to get to
    # that coordinate.
    moveGrid = MoveGrid(height, width, None)
    #moveGrid.printGrid()
    
    # Get lists of stuff on the board
    noGoCoordsList = symbolGrid.getListOfType([ME_HEAD, ME_SNAKE, OTHER_HEAD, OTHER_BODY])
    # Note: You would expect ME_TAIL to be in the maybeGoCoordsList, but then
    # it doesn't get a distance associated with it. However the tail will
    # disappear for one move when the snake eats food (2 tail coords so it gets
    # covered up by the body) so actually we should be ok.
    maybeGoCoordsList = symbolGrid.getListOfType([MAYBE_GO])
    # build grid using only safe moves
    barrierCoordsList = noGoCoordsList + maybeGoCoordsList
    
    #print("NO GO COORDS={}".format(noGoCoordsList))
    #print("MAYBE GO COORDS={}".format(maybeGoCoordsList))
    #print("BARRIER COORDS={}".format(barrierCoordsList))
    
    # build up the list of moves at each location
    ourHead = getHeadCoord(ourSnakeCoords)
    fillDistanceAndMoveGrids(distanceGrid, moveGrid, ourHead, barrierCoordsList)
    
    # Print grids for debugging
    distanceGrid.printGrid(2)
    #moveGrid.printGrid()
    
    
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
        elif(val == 'D'):
            return("down")
        else:
            print("***ERROR*** Invalid coordinate! {} = {}, using default 'down'".format(coord, val))
            return("down")
    
    def getMoveCounts(self):
        """
        Get the number of spaces that are available for each move. For example,
        if you are trying to decide whether to move up or right, rather than
        making a random decision, you can get the move counts for each
        direction. There might be 4 positions available if you move up, and 40
        positions if you move right. All other things being equal, you should
        move in the direction that has the most opportunity for future moves.
        
        Return a dictionary of the 4 directions and the number of positions on
        the board available with that direction. Since you can't sort a
        dictionary, there is also a list of keys in the order of preferred
        direction (reverse sorted so the first element is the most favoured
        direction).
        """
        numLeft = len(self.getListOfType(['L']))
        numRight = len(self.getListOfType(['R']))
        numUp = len(self.getListOfType(['U']))
        numDown = len(self.getListOfType(['D']))
        moveDict = {"left":numLeft, "right":numRight, "up":numUp, "down":numDown}
        preferredMoveList = sorted(moveDict, key=moveDict.get, reverse=True)
        print("moveDict={}".format(moveDict))
        return (moveDict, preferredMoveList)
    
    def getHighestMoveCount(self):
        moveCounts = self.getMoveCounts()
        return(max(moveCounts, key=moveCounts.get))





def buildSymbolGrid(data):
    """
    Build a grid and use symbols to represent all the items in the grid.
    Then you can use getListOfType() to get all the coordinates for a list
    of symbols. You can also print this grid (super useful for debugging).
    
    The grid should be built up in layers from least dangerous (eg. food) to
    most dangerous (eg. snake body). That way, any additional zones put in
    place do not clobber no-go coordinates.
    """

    height = data['height']
    width = data['width']
    myId = data['you']
    mySnakeObj = getMySnakeObj(data)

    grid = Grid(width, height, OPEN_SPACE)
        
    # Food (very safe)
    grid.setList(data['food'], FOOD)
    
    # Area around Eatable Snake Heads (safe)
    for snake in data['snakes']:
        if(snake['id'] != myId):
            if(len(snake['coords']) < len(mySnakeObj['coords'])):
                # snake is shorter than us. Positions around the head are
                # the goal, not the head itself, as the snake's head will not
                # be there on the next move.
                orthList = grid.getOrthogonal(snake['coords'][0])
                grid.setList(orthList, EATABLE_HEAD_ZONE)

    # Area around Non-eatable Snake Heads (risky: maybe-go)
    for snake in data['snakes']:
        if(snake['id'] != myId):
            if(len(snake['coords']) >= len(mySnakeObj['coords'])):
                # Bigger snake
                # put a danger zone around the head of larger snake
                orthList = grid.getOrthogonal(snake['coords'][0])
                grid.setList(orthList, MAYBE_GO)

    # Snake heads and bodies (deadly: no-go) and tails (risky: maybe-go)
    # Must lay down after everything else, so it doesn't get overwritten
    for snake in data['snakes']:
        if(snake['id'] == myId):
            # Keep this order (tail, snake, head). There are 2 tail coordinates
            # at the same location when the snake eats food. So the tail is
            # temporarily hidden by the body which gets overlayed after the
            # tail has been placed. This is actually what we want so we don't
            # choose the tail spot after a snake has eaten something.
            grid.set(snake['coords'][-1], ME_TAIL)
            grid.setList(snake['coords'][1:-1], ME_SNAKE)
            grid.set(snake['coords'][0], ME_HEAD)
            print("me snake coords={}".format(snake['coords']))
        else:
            grid.set(snake['coords'][-1], MAYBE_GO)
            grid.setList(snake['coords'][1:-1], OTHER_BODY)
            grid.set(snake['coords'][0], OTHER_HEAD)
            print("snake coords={}".format(snake['coords']))
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
    maxSnakeMove = symbolGrid.getMaxSnakeMove()
    ourMove = None
    
    # Priority #1 -- don't paint yourself into a corner
    moveDict, preferredMoveList = moveGrid.getMoveCounts()
    
        # Priority #2 -- stay healthy and try to be the biggest snake
    if ourMove == None:
        health = getOurSnakeHealth(data)
        largerThanUs = snakesLargerThanUs(data)
        print("Health={}, snakes larger than us={}".format(health, largerThanUs))
        if (health < 75) or (largerThanUs > 0):
            nearestFoodList = getNearestOfType([FOOD], symbolGrid, distanceGrid)
            numFood = len(nearestFoodList)
            #print("nearestFoodList={}".format(nearestFoodList))
            if numFood == 0:
                #print("No Food! Moving on...")
                pass
            elif numFood == 1:
                ourMove = moveGrid.getMove(nearestFoodList[0])
                print("Decision: Eat food at {}, distance={}, ourMove={}".format(nearestFoodList[0], distanceGrid.get(nearestFoodList[0]), moveGrid.getMove(nearestFoodList[0])))
            else: # special case: more than one food at equal distance!
                moveList = []
                for coord in nearestFoodList:
                    moveList.append(moveGrid.getMove(coord))
                for k in preferredMoveList:
                    if k in moveList:
                        ourMove = k
                        break
                print("Decision: Multiple Food: {}, distance={}, ourMove={}".format(nearestFoodList, distanceGrid.get(nearestFoodList[0]), ourMove))    
    
    # Priority #3 -- eat smaller snakes!
    if ourMove == None: # turn this off for less risky behaviour!
        eatableSnakeHeadsList = getNearestOfType([EATABLE_HEAD_ZONE], symbolGrid, distanceGrid)
        #print("eatableSnakeHeadsList={}".format(eatableSnakeHeadsList))
        numHeads = len(eatableSnakeHeadsList)
        if numHeads == 0:
            #print("No Snakes! Moving on...")
            pass
        elif numHeads == 1:
            ourMove = moveGrid.getMove(eatableSnakeHeadsList[0])
            print("Decision: Eat head at {}, distance={}, ourMove={}".format(eatableSnakeHeadsList[0], distanceGrid.get(eatableSnakeHeadsList[0]), moveGrid.getMove(eatableSnakeHeadsList[0])))
        else: # special case: more than one snake head at equal distance!
            moveList = []
            for coord in eatableSnakeHeadsList:
                moveList.append(moveGrid.getMove(coord))
            for k in preferredMoveList:
                if k in moveList:
                    ourMove = k
                    break
            print("Decision: Multiple heads: {}, distance={}, ourMove={}".format(eatableSnakeHeadsList, distanceGrid.get(eatableSnakeHeadsList[0]), ourMove))    
    
    # if no snakes to eat then move on
    
    # Priority #4 -- chase tail!
    if ourMove == None:
        myTail = getTailCoord(getOurSnakeCoords(data))
        if distanceGrid.get(myTail) < maxSnakeMove:
            ourMove = moveGrid.getMove(myTail)
            print("Decision: Chase tail at {}, distance={}, ourMove={}".format(myTail, distanceGrid.get(myTail), moveGrid.getMove(myTail)))
        #else:
        #    print("Decision: Can't get to tail!")
    
    # Nothing within reach! Start to panic.
    # First check the moveDict to see if any direction shows available moves.
    # Go with whichever direction has the most coordinates marked.
    # Since moveDict is sorted, just pick the first direction.
    if ourMove == None:
        # make sure there is at least one position to move into
        if moveDict[preferredMoveList[0]] > 0:
            ourMove = preferredMoveList[0]
            print("Decision: go with the majority (L={},R={},U={},D={}) move={}".format(moveDict['left'], moveDict['right'], moveDict['up'], moveDict['down'], ourMove))

    # If we get here, then we should be panicing.
    # At this point, go to the list of "maybe go" positions. This is a last
    # resort because moving into these positions are high risk (eg. moving
    # beside the head of a larger snake). But if no other choice, then a
    # maybe-go is better than a random fate.
    if ourMove == None:
        ourSnakeHead = getHeadCoord(getOurSnakeCoords(data))
        orthogonalList = symbolGrid.getOrthogonal(ourSnakeHead)
        maybeGoCoordsList = symbolGrid.getListOfType([ME_TAIL, MAYBE_GO])
        for coord in orthogonalList:
            if coord in maybeGoCoordsList:
                # found a direction -- go for it
                ourMove = getTrajectory([coord, ourSnakeHead])
                print("Decision: No good options. Resort to the Maybe-go list, move={}".format(ourMove))
    
    # Full panic, we're probably going to die. Keep on our trajectory, so we
    # at least don't turn in on ourself.
    if ourMove == None:
        #directions = ['up', 'down', 'left', 'right']
        #ourMove = random.choice(directions)
        ourMove = getTrajectory(getOurSnakeCoords(data))
        print("Descision: PANIC! No moves available! Going straight ahead: {}".format(ourMove))
    return(ourMove)
    

def getNearestOfType(thingsToFindList, symbolGrid, distanceGrid):
    """
    Pass in an array of things to find in the symbol table, and return an
    array of coordinates of the nearest things. Normally there will be an arry
    with 1 coordinate, but in some cases there will be 2 things of equal
    distance away. When that happens, further decisions need to be made as
    to which thing to head towards.
    """
    maxSnakeMove = symbolGrid.getMaxSnakeMove()
    foundThingsList = symbolGrid.getListOfType(thingsToFindList)
    distanceDict = {} # key=coordinate, value=distance from head
    nearestThingsCoordsList = []
    for coord in foundThingsList:
        coordDistance = distanceGrid.get(coord)
        if coordDistance < maxSnakeMove: # check for unobtainium
            distanceDict[coord] = coordDistance
    #print("distanceDict={}".format(distanceDict))
    # klunktastic
    sortedCoords = sorted(distanceDict, key=distanceDict.get)
    sortedDistances = sorted(distanceDict.values())
    #print("sortedCoords={}, sortedDistances={}".format(sortedCoords, sortedDistances))
    shortestDistance = None
    for i in range(len(sortedCoords)):
        if shortestDistance == None or sortedDistances[i] == shortestDistance:
            nearestThingsCoordsList.append(sortedCoords[i])
            shortestDistance = sortedDistances[i]
    return(nearestThingsCoordsList)




