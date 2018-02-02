import bottle
import os
import sys
import random
import strategy

#Auto Deployed at http://jerksnake.herokuapp.com

# Running battle_snake locally
# Install Docker
# Run: docker run -it -p 4000:4000 stembolt/battle_snake
# Visit http://localhost:4000 NOTE: Docker runs on a virtual lan so when you
# add a snake to the game you cannot use localhost, use your internal IP instead.



##############################################
# WEB CALLS
#############################################


@bottle.route('/static/<path:path>')
def static(path):
    print("STATIC request")
    print("path={}".format(path))
    return bottle.static_file(path, root='../static/')


@bottle.post('//start')
def start():
    print("START request")
    data = bottle.request.json

    print("\nSNAKE START!")
    for k,v in data.items():
        print("{}={}".format(k,v))


    #game_id = data['game_id']
    #board_width = data['width']
    #board_height = data['height']
    print("URL Parts:")
    #for k,v in bottle.request.urlparts.items():
    #    print("{}={}".format(k, v))
    print(bottle.request.urlparts)

    head_url = "{}://{}/static/jerk.png".format(
        bottle.request.urlparts.scheme,
        bottle.request.urlparts.netloc
    )

    return {
        # What color your snake should be on the board.
        # Accepts any valid CSS color.
        # https://developer.mozilla.org/en-US/docs/Web/CSS/color
        'color': '#4a412a',
        'name': "JerkSnake II",

        # URL of the image to display as your avatar.
        'head_url': head_url,
        'taunt': "No room for error", #'{} ({}x{})'.format(game_id, board_width, board_height),
        #head_type: HeadType;
        #tail_type: TailType;
        'secondary_color': '#ff00ff',
    }


@bottle.post('//move')
def move():
    print("MOVE request")
    data = bottle.request.json

    ourMove = strategy.executeStrategy(data)
    return {
        'move': ourMove,
        'taunt': 'battlesnake-python!'
    }


# Expose WSGI app (so gunicorn can find it)
application = bottle.default_app()
if __name__ == '__main__':
    print("RUNNING MAIN... STARTING BOTTLE...")
    print(sys.version)
    bottle.run(application, host=os.getenv('IP', '0.0.0.0'), port=os.getenv('PORT', '8080'))

#curl http://192.168.99.1:8080

