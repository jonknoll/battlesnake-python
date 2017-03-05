import math
#just definitions

import random


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

def dirToCoord(headCoord, direction):
    if(direction == 'right'):
        return([headCoord[0]+1, headCoord[1]])
    elif(direction == 'left'):
        return([headCoord[0]-1, headCoord[1]])
    elif(direction == 'up'):
        return([headCoord[0], headCoord[1]-1])
    else:
        return([headCoord[0], headCoord[1]+1])


# absolute value distance between
def distance(first, second):
    dist = math.fabs(first[0]-second[0]) + math.fabs(first[1]-second[1])
    return int(dist)

#which coordinate in list is closest to target
#MAY RETURN 2 ELEMENTS
def closest(reference, pointList):
    #returns negative if you passed something weird
    closestPoint = pointList[0]
    shortest = distance(reference, pointList[0])
    movesToPoint = ''
    for point in pointList:
        #check for default valuw
        movesToPoint = distance(reference, point)
        if(movesToPoint < shortest):
            #print("Gridhelper: Set shortest point to: {} is {}".format(reference, point))
            shortest = movesToPoint
            closestPoint = point
    return closestPoint


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



#priority based on distance
if __name__=='__main__':
    #print(distance([1,3],[1,2]))
    #print(distance([1,3],[2,3]))
    print(closest([1,3],[[7,1],[1,10],[4,5],[2,3],[1,3]]))
