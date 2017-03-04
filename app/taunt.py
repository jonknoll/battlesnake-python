from random import randint

def taunt():
    taunts = ['Cant heck this snek',
    'No step on snek', 'Imma do you a frighten',
    'Am Scary Cober',
    'Dont tread on REEEEE',
    'If your mom was a collection class, her insert method would be private',
    'Your mom was is so fat that she turned a binary tree into a linked list in constant time',
    'They told me to refactor my code, so I will refactor their sneks']
    taunt = taunts[randint(0,len(taunts)-1)]
    return taunt

if __name__=='__main__':
    i = 0
    while i<100:
        print(taunt())
        i+=1
