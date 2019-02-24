from .gridhelper import *
import random
from . import gridhelper

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

if __name__=='__main__':
    print(desiredTrajectory([3,1], [[[100,8],[3,2]],[[45,8],[3,2]]], [[7,1]], 100))

#getOurSnakeCoords(data)
#getOtherSnakeCoords(data)
