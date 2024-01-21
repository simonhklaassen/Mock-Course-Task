#!/usr/bin/env python3

def write_png():
    import shutil
    shutil.copyfile("task/ball.png", "ball.png")

def write_csv():
    import os
    os.makedirs("out")
    with open("out/data.csv", "w") as f:
        f.write("'a','b','cdef'\n1,2,3")

write_png()
write_csv()
