#just definitions

import random

# absolute value distance between
def distance(first, second):
    distanceInMoves = 0
    return distanceInMoves

#which coordinate in list is closest to target
def closest(xy,xylist):
    return [0,0]


def directionsToTry(desiredDir):
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
    randChoice = randChoice(directions)
    priorityList.append(randChoice)
    directions.remove(randChoice)
    priorityList.append(directions[0])
    return(priorityList)




