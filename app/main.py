import json
import os
import random
import bottle
import sys

from cheroot import wsgi

from . import strategy
from .simplify2019 import simplify

from .api import ping_response, start_response, move_response, end_response

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
    """
    Given a path, return the static file located relative
    to the static folder.

    This can be used to return the snake head URL in an API response.
    """
    print("STATIC request")
    print("path={}".format(path))
    return bottle.static_file(path, root='static/')

@bottle.post('/ping')
def ping():
    """
    A keep-alive endpoint used to prevent cloud application platforms,
    such as Heroku, from sleeping the application instance.
    """
    print("PING request")
    return ping_response()

@bottle.post('/start')
def start():
    print("START request")
    data = bottle.request.json

    """
    TODO: If you intend to have a stateful snake AI,
            initialize your snake state here using the
            request's data if necessary.
    """
    #print(json.dumps(data))
    
    # What color your snake should be on the board.
    # Accepts any valid CSS color.
    # https://developer.mozilla.org/en-US/docs/Web/CSS/color
    color = "#3F3F3F"

    return start_response(color)


@bottle.post('/move')
def move():
    print("MOVE request")
    data = bottle.request.json

    """
    TODO: Using the data from the endpoint request object, your
            snake AI must choose a direction to move in.
    """
    #print(json.dumps(data))

    data = simplify(data)

    ourMove, ourTaunt = strategy.executeStrategy(data)

    return move_response(ourMove)


@bottle.post('/end')
def end():
    print("END request")
    data = bottle.request.json

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
        host = os.getenv('IP', '0.0.0.0'),
        port = os.getenv('PORT', '8080'),
        debug = os.getenv('DEBUG', True),
        server=CherryPyServer
        )
    
#curl http://192.168.99.1:8080

if __name__ == '__main__':
    main()
