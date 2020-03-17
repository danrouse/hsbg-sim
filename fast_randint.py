from random import random

def randint(min, max):
    """
    Generate a random integer between min and max (inclusive)
    See https://eli.thegreenplace.net/2018/slow-and-fast-methods-for-generating-random-integers-in-python/
    """
    return min + int(random() * (max - min))
