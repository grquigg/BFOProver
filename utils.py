import re
DEBUG = False
SKOLEM_EXP = "(\[e,[0-9]+,\[([A-Z],)*[A-Z]\]\])"

def display(message, type, debug):
    if(type == "crit"):
        print(message)
    elif(type == "debug"):
        if(debug):
            print(message)

def is_skolem(expr):
    search = re.search('\[e,[0-9]+,\[(?:\w,?)+\]\]', expr)
    if search != None:
        return True
    return False