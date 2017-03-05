import random
#Supa dank insult
def taunt():

    #List of dank insults
    dankInsults = ['Cant heck this snek',
    'No step on snek',
    'Imma do you a frighten',
    'Am Scary Cober',
    'Dont tread on REEEEE',
    'If your mom was a collection class, her insert method would be private',
    'Your mom was is so fat that she turned a binary tree into a linked list in constant time',
    'They told me to refactor my code, so I will refactor their sneks']

    #Got em!
    return (random.choice(dankInsults))


#Void parameterless function that will print an ugly hex number
#Doing me a hex
def nastyColour():

    #A list of fugly hex colours
    disgustingColours = [ '#00ff00', '#ffff00', '#4a412a', '#00ffff', '#ff0000', '#ff0066', '#ff00ff']

    #Ehmergehd, muh i's
    return (random.choice(disgustingColours))

if __name__=='__main__':
    i = 0
    while i<100:
        print(taunt())
        print(nastyColour())
        i+=1
