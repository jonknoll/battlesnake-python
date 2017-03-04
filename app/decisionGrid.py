from gridhelper import *
import random

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
    return random.choice(directions)

def offensiveTarget(me, heads, food, energy):
    priority = ''

    #am i hungry? If so go to food.
    if energy <= HUNGRYAT:
        #Get food code priority food
        #generate direction to go toward food
        print("nothing here")
    else:
        #Find kill point priority kill
        #get list of snake heads
        #find nearest snake head and move towards it
        print("nothing here")




    """
    assume I have a list of other snake coordinates and
    """
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

    return 'Nothing yet'


if __name__=='__main__':
    print(offensiveTarget)
    print(howDoIgetThere([2,2],[4,4]))

#getOurSnakeCoords(data)
#getOtherSnakeCoords(data)
