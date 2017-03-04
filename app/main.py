import bottle
import os
import random


# Values to put in grid, priorities TBD
OPEN_SPACE = 0
ME_SNAKE = 1
WALL = 2
FOOD = 3
OTHER_SNAKE = 4
BIG_SNAKE = 5

def build_grid(data):
    pass

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

    directions = ['up', 'down', 'left', 'right']

    # move into unfilled spaces.
        # if space orthagonally relative to head has no elements it is unfilled
    # move into non danger zones
        # danger spots relative to other snake heads
        # [[-1,0],[1,0],[0,1],[0,-1]]
    # if energy is less than half get food
    # go to sweet spots
        # the sweet spots relative to opponent snake head
        # [[-2,0],[0,-2],[2,0],[0,2],[-1,-1],[-1,1],[1,-1],[1,1]]
    # do not get into corners

    print("!SNAKE MOVE!")
    for k,v in data.iteritems():
        print("{}={}".format(k,v))
    snakedata = data['snakes']
    for snake in snakedata:
        print("SNAKE!")
        for k,v in snake.iteritems():
            print("{}={}".format(k,v))

    choice = directions[2]
    return {
        'move': choice,
        'taunt': 'battlesnake-python!'
    }


# Expose WSGI app (so gunicorn can find it)
application = bottle.default_app()
if __name__ == '__main__':
    bottle.run(application, host=os.getenv('IP', '0.0.0.0'), port=os.getenv('PORT', '8080'))
