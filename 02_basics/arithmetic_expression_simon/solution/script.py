#!/usr/bin/env python3
# `a - (b^2 / (c + d * (√a % b)))`
import math

def calculate(a, b, c, d):
    return a - ((b*b) / (c + d * (math.sqrt(a) % b)))

print(calculate(4,5,6,7))

