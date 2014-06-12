#!/usr/bin/python
import os
from os.path import isfile, getsize, exists
import argparse

def get_logs(dir, prefix, suffix):
    """Return a list of all files in dir which start with prefix or end with suffix"""
    return [dir+'/'+i for i in os.listdir(dir)
                if ((isfile(dir+'/'+i)) and (((prefix != "") and (i.startswith(prefix))) or ((suffix != "") and (i.endswith(suffix)))))]

def total(logfiles):
    """Return the total filesize, in bytes, of all files in logfiles"""
    return sum([getsize(f) for f in logfiles])

if __name__ == "__main__":
	parser = argparse.ArgumentParser(description='Delete the oldest files in DIRECTORY beginning with PREFIX and ending with SUFFIX (if set) until the total size is under MAXSIZE.')
	parser.add_argument('directory')
	parser.add_argument('prefix')
	parser.add_argument('maxsize', type=int)
	parser.add_argument('--suffix', default="")
	args = parser.parse_args()

	logs = get_logs(args.directory, args.prefix)
	size_to_delete = total(logs) - args.maxsize

	for logfile in sorted(logs):
	    if (size_to_delete > 0):
	        size_to_delete -= getsize(logfile)
	        os.unlink(logfile)
