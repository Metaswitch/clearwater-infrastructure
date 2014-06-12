#!/usr/bin/python
import os
from os.path import isfile, exists
import argparse

def get_logs(dir, prefix, suffix):
    """Return a list of all files in dir which start with prefix or end with suffix"""
    return [dir+'/'+i for i in os.listdir(dir)
                if ((isfile(dir+'/'+i)) and (((prefix != "") and (i.startswith(prefix))) or ((suffix != "") and (i.endswith(suffix)))))]

if __name__ == "__main__":
        parser = argparse.ArgumentParser(description='Delete the oldest files in DIRECTORY beginning with PREFIX and ending with SUFFIX (if set) until the total number is under MAXSIZE.')
        parser.add_argument('directory')
        parser.add_argument('maxsize', type=int)
        parser.add_argument('--prefix', default="")
        parser.add_argument('--suffix', default="")
        args = parser.parse_args()

        logs = get_logs(args.directory, args.prefix, args.suffix)
        size_to_delete = len(logs) - args.maxsize

        for logfile in sorted(logs):
            if (size_to_delete > 0):
                size_to_delete -= 1
                os.unlink(logfile)
