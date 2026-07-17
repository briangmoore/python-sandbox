# python scripts echoing caculator programs
# Changing now to have the count include *after* the repeated bday is added

def bdaysim():
    import math
    import random
    L3 = []
    N = random.randint(1,365)
    while True:
        L3.append(N)
        N = random.randint(1,365)
        if N in L3:
            L3.append(N)
            print(L3)
            return len(L3)        