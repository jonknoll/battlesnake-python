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
    
    print("!SNAKE MOVE!")
    for k,v in data.iteritems():
        print("{}={}".format(k,v))
    snakedata = data['snakes']
    for snake in snakedata:
        print("SNAKE!")
        for k,v in snake.iteritems():
            print("{}={}".format(k,v))

    # TODO: Do things with data
    directions = ['up', 'down', 'left', 'right']

    return {
        'move': random.choice(directions),
        'taunt': 'battlesnake-python!'
    }


# Expose WSGI app (so gunicorn can find it)
application = bottle.default_app()
if __name__ == '__main__':
    bottle.run(application, host=os.getenv('IP', '0.0.0.0'), port=os.getenv('PORT', '8080'))
