import bottle
import os
import random
from grid import Grid


# Values to put in grid, priorities TBD
OPEN_SPACE = 0
ME_SNAKE = '#'
WALL = -1
FOOD = 'F'
OTHER_SNAKE = 'S'
BIG_SNAKE = 5
DEAD_SNAKE = 'D'
SNAKE_HEAD = '@'



def build_grid(data):
    height = data['height']
    width = data['width']
    myId = data['you']
    
    grid = Grid(width, height)
    
    # fill with the living snakes
    for snake in data['snakes']:
        id = snake['id']
        if(id == myId):
            snakeType = ME_SNAKE
        else:
            snakeType = OTHER_SNAKE
        
        grid.setList(snake['coords'], snakeType)
        if(snakeType != ME_SNAKE):
            grid.set([snake['coords'][0][0], snake['coords'][0][1]], SNAKE_HEAD)
        
    # fill with the dead snakes
    for snake in data['dead_snakes']:
        grid.setList(snake['coords'], DEAD_SNAKE)

    # fill with food
    for food in data['food']:
        grid.setList(data['food'], FOOD)

    return(grid)

def getOurHeadCoord(data):
    myId = data['you']
    for snake in data['snakes']:
        id = snake['id']
        if(id == myId):
            return(snake['coords'][0])

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
        'color': '#00FF00',
        'taunt': '{} ({}x{})'.format(game_id, board_width, board_height),
        'head_url': head_url,
        'name': 'Jon Snake'
    }


@bottle.post('/move')
def move():
    data = bottle.request.json
    grid = build_grid(data)
    ourCoord = getOurHeadCoord(data)
    
    print("!SNAKE MOVE!")
    for k,v in data.iteritems():
        print("{}={}".format(k,v))
    snakedata = data['snakes']
    for snake in snakedata:
        print("SNAKE!")
        for k,v in snake.iteritems():
            print("{}={}".format(k,v))
    print("\n\n")
    grid.printGrid(0)
    print("\nWe are at {}".format(ourCoord))

    # TODO: Do things with data
    #directions = ['up', 'down', 'left', 'right']
    directions = []
    if(grid.get([ourCoord[0]-1,ourCoord[1]]) == 0):
        print("x-1,y = {}".format(grid.get([ourCoord[0]-1,ourCoord[1]])))
        directions.append('left')
    if(grid.get([ourCoord[0]+1,ourCoord[1]]) == 0):
        print("x+1,y = {}".format(grid.get([ourCoord[0]+1,ourCoord[1]])))
        directions.append('right')
    if(grid.get([ourCoord[0],ourCoord[1]+1]) == 0):
        print("x,y+1 = {}".format(grid.get([ourCoord[0],ourCoord[1]+1])))
        directions.append('down')
    if(grid.get([ourCoord[0],ourCoord[1]-1]) == 0):
        print("x,y-1 = {}".format(grid.get([ourCoord[0],ourCoord[1]-1])))
        directions.append('up')
    
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
