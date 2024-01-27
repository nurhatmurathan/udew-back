import random


def generate_digit_code():
    return ''.join(random.choices('0123456789', k=6))
