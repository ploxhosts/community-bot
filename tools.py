import random
import time


def generate_flake():
    flake = (int((time.time() - 946702800) * 1000) << 23) + random.SystemRandom().getrandbits(23)
    return flake


def get_time(word):
    res = None
    if "perm" == word.lower():
        pass
    elif "s" in word:
        res = int(word.split("s")[0]) / 60
    elif "m" in word:
        formatted_word = word.split("m")
        res = int(formatted_word[0])
    elif "h" in word:
        formatted_word = word.split("h")
        res = int(formatted_word[0]) * 60
    elif "d" in word:
        formatted_word = word.split("d")
        res = int(formatted_word[0]) * 60 * 24
    elif "w" in word:
        formatted_word = word.split("w")
        res = int(formatted_word[0]) * 60 * 24 * 7
    return res
