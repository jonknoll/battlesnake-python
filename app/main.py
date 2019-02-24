import bottle
import os
import random
import sys
from .grid import Grid
from .gridhelper import *
from .snakestuff import *
from .taunt import *
from .decisionGrid import *

from cheroot import wsgi
from .convert2019_2017 import convert

from .api import ping_response, start_response, move_response, end_response

#Auto Deployed at http://jerksnake.herokuapp.com

# Running battle_snake locally
# Install Docker
# Run: docker run -it -p 4000:4000 stembolt/battle_snake
# Visit http://localhost:4000 NOTE: Docker runs on a virtual lan so when you
# add a snake to the game you cannot use localhost, use your internal IP instead.



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


##############################################
# WEB CALLS
#############################################

@bottle.route('/')
def index():
    return '''
    Battlesnake documentation can be found at
       <a href="https://docs.battlesnake.io">https://docs.battlesnake.io</a>.
    '''

@bottle.route('/static/<path:path>')
def static(path):
    return bottle.static_file(path, root='static/')

@bottle.post('/ping')
def ping():
    """
    A keep-alive endpoint used to prevent cloud application platforms,
    such as Heroku, from sleeping the application instance.
    """
    print("\nPING request")
    return ping_response()

@bottle.post('/start')
def start():
    data = bottle.request.json
    print("\nSNAKE START!")
    for k,v in data.items():
        print("{}={}".format(k,v))
    print("SNAKE INFO:")


    game_id = data['game']
    board_width = data["board"]['width']
    board_height = data["board"]['height']

    head_url = '%s://%s/static/jerk.png' % (
        bottle.request.urlparts.scheme,
        bottle.request.urlparts.netloc
    )

    # TODO: Do things with data

    #return {
    #    'color': nastyColour(),
    #    'taunt': '{} ({}x{})'.format(game_id, board_width, board_height),
    #    'head_url': head_url,
    #    'name': 'JerkSnake'
    #}
    return start_response(nastyColour())


@bottle.post('/move')
def move():
    data = bottle.request.json
    data = convert(data)

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
    # Offense: Take a list of desired directions in from the goal algorithm
    ################################################################
    
    # Simple test goal: keep on our current trajectory
    #desiredTraj = [ourTrajectory]
    
    # Slightly more interesting goal: pick a random direction
    #desiredTraj = random.choice([['up'], ['down'], ['left'], ['right']])

    # Jerk snake goal: go to heads of other snakes, or eat food
    desiredTraj = desiredTrajectory(ourSnake, enemySnakes, data['food'], ourSnakeObj['health_points'])
    
    # Get an ordered list of directions to try
    directionsToTry = getDirectionsToTry(desiredTraj)
    print("directions to try are = {}".format(directionsToTry))
    
    ################################################################
    # Defense: Rank directions in terms of risk, and take the lowest risk move
    ################################################################
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
    
    # No move is valid! We gonna die! Just head straight on.
    if(ourMove == None):
        print("Can't go anywhere! Maintain current trajectory")
        ourMove = ourTrajectory
                
    print("Our move is = {}".format(ourMove))


    #return {
    #    'move': ourMove,
    #    'taunt': 'battlesnake-python!'
    #}
    return move_response(ourMove)


@bottle.post('/end')
def end():
    data = bottle.request.json
    print("\nEND request - Turn {} - {}".format(data["turn"], data["you"]["name"]))

    """
    TODO: If your snake AI was stateful,
        clean up any stateful objects here.
    """
    #print(json.dumps(data))

    return end_response()


class CherryPyServer(bottle.ServerAdapter):
    def run(self, handler):
        server = wsgi.Server((self.host, self.port), handler)
        
        try:
            server.start()
        finally:
            server.stop()


def main():
    print("RUNNING MAIN... STARTING BOTTLE...")
    print(sys.version)
    # Using one of the allowed TCP ports in the McAfee firewall so it doesn't block traffic
    # As of Feb 2018 we can use: 20-21, 111, 502, 4987, 4988-4989, 5500-5509,
    # 6001-6002, 8282, 13777
    # ALSO: make sure the URL you give the server doesn't have a trailing slash!
    application = bottle.default_app()
    bottle.run(
        application,
        host=os.getenv('IP', '0.0.0.0'),
        port=os.getenv('PORT', '8181'),
        debug=os.getenv('DEBUG', True),
        server=CherryPyServer
        )
    


if __name__ == '__main__':
    main()
