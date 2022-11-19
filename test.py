import random

bag = range(6)
random.shuffle(bag)

while bag:
    print(bag)
    b = random.choice(bag)
    bag.remove(b)

    print(b)
    print(bag)