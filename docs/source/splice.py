#!/bin/env python3

import os
import sys

if __name__ == "__main__":
    if len(sys.argv) < 2:
        exit(1)

    command = sys.argv[1]
    ranges = []
    for i in range(2, len(sys.argv)):
        start = 0
        end = -1
        lst = sys.argv[i].split(',')

        if len(lst) > 2:
            print('Bad range format: Expected int(a)[,int(b)] with a<b when b>0')
            exit(1)

        start = int(lst[0])
        if len(lst) > 1:
            end = int(lst[1])
        ranges.append((start, end))

    pipe = os.popen(command, 'r')
    output = []
    for line in pipe:
        output.append(line)
    pipe.close()
     
    last_end = 0
    max = len(output)
    if len(ranges) == 0:
        ranges.append((0, max))

    for (start, end) in ranges:

        if end < 0:
            end = max + end + 1

        if start != last_end:
            print('...')
        for i in range(start, end, 1):
            print(output[i], end='')
        last_end = end

    if last_end != max:
        print('...')
