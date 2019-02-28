import sys
import json

from app import main as snakeMain


def main():
    f = open(sys.argv[1])
    rawJson = f.read()
    f.close()
    jsonData = json.loads(rawJson)
    
    snakeMain.doMove(jsonData)



if __name__ == '__main__':
    main()
