import sys


class Grid(object):
    def __init__(self, width, height):
        self.width = width
        self.height = height
        self.grid = [[0 for x in range(width)] for y in range(height)]
    
    def set(self, coord, val):
        self.grid[coord[1]][coord[0]] = val
    
    def get(self, coord):
        if((coord[0] >= self.width) or (coord[0] < 0)):
            return(-1)
        elif((coord[1] >= self.height) or (coord[1] < 0)):
            return(-1)
        return self.grid[coord[1]][coord[0]]
    
    def setList(self, coordsList, val):
        for coord in coordsList:
            self.set(coord, val)
    
    def getListOfType(self, typeList):
        coordsList = []
        for y in range(self.height):
            for x in range(self.width):
                thingAtCoord = self.get([x,y])
                if(thingAtCoord in typeList):
                    coordsList.append([x,y])
        return(coordsList)
    
    def getOrthagonal(self, coord):
        coordsList = []
        right = [coord[0]+1, coord[1]]
        left = [coord[0]-1, coord[1]]
        down = [coord[0], coord[1]+1]
        up = [coord[0], coord[1]-1]
        if(self.get(right) != -1):
            coordsList.append(right)
        if(self.get(left) != -1):
            coordsList.append(left)
        if(self.get(down) != -1):
            coordsList.append(down)
        if(self.get(up) != -1):
            coordsList.append(up)
        return(coordsList)
    
    def getDiagonal(self, coord):
        coordsList = []
        topLeft = [coord[0]-1, coord[1]-1]
        bottomLeft = [coord[0]-1, coord[1]+1]
        topRight = [coord[0]+1, coord[1]-1]
        bottomRight = [coord[0]+1, coord[1]+1]
        if(self.get(topLeft) != -1):
            coordsList.append(topLeft)
        if(self.get(bottomLeft) != -1):
            coordsList.append(bottomLeft)
        if(self.get(topRight) != -1):
            coordsList.append(topRight)
        if(self.get(bottomRight) != -1):
            coordsList.append(bottomRight)
        return(coordsList)
    
    def add(self, coord, val):
        origVal = self.get(coord)
        newVal = origVal + val
        self.set(coord, newVal)
        return(newVal)
    
    def printGrid(self, style=0):
        print("GRID: ({} x {})".format(self.width, self.height))
        for y in range(self.height):
            #print("y={}".format(y))
            for x in range(self.width):
                if(self.get([x,y]) == 0):
                    sys.stdout.write("{} ".format(style))
                else:
                    sys.stdout.write("{} ".format(self.get([x,y])))  
            sys.stdout.flush()
            print("")
    
    def print2(self):
        print(self.grid)
    
    def countFreeBlocks(self, startingCoord, direction, freeTypes):
        """
        startingCoord = [x,y]
        direction =  'up', 'down', 'left' or 'right'
        freeTypes = list of things that are considered free space
        """
        pass
        
            
if __name__=='__main__':
    testGrid = Grid(5,10)
    testGrid.set([0,2], 22)
    testGrid.set([4,0], 44)
    testGrid.print2()
    testGrid.printGrid()
    
    