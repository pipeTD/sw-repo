#!/usr/bin/env python
'''
Script name: lss
Author: Mike Harris
Date: 10/14/2016

Description: Script to facilitate the specialized listing of the contents of a folder.

Usage: lss <folder>
       Where <folder> is an optional argument. If omitted, the script will work on the current folder.
       Note: If the <folder> begins with a / it will take that as a root level folder. Otherwise it is relative to
       the current folder.

'''

import os
import re
import sys
import glob

from operator import itemgetter
from itertools import groupby


def _print_usage():
    print "Usage: lss <base path>\n\n\t<base path> : optional directory argument to list the contents\n"


def _validate_basedir():
    ''' Validate user input '''
    base_dir = os.getcwd()
    args = sys.argv[1:]
    if '-h' in args or '--help' in args:
        _print_usage()
        sys.exit()
    if args:
        if len(args) > 1:
            _print_usage()
            sys.tracebacklimit = 0
            raise ValueError("Invalid argument(s) to lss command: %s" % " ".join(args[1:]))
        if not args[0].startswith('/'):
            base_dir = os.path.join(base_dir, args[0])
        else:
            base_dir = args[0]
    if not os.path.exists(base_dir):
        sys.tracebacklimit = 0
        raise OSError("No such file or directory: %s" % (base_dir))
    return base_dir


def _print_results(results):
    for key, value in results.items():
        print len(value.get("file_names", [])), key, value.get("frame_list", "")


def _string_replace(item, old_str, new_str, position=1):
    ''' Search item for old_str and replace with new_str at nth position '''
    indicies = [i for i in range(len(item) - len(old_str) + 1) if item[i:i + len(old_str)] == old_str]
    item = list(item)
    item[indicies[position - 1]:indicies[position - 1] + len(old_str)] = new_str
    return ''.join(item)


def _get_number_ranges(num_list):
    ''' Format number ranges for a sequence of numbers '''
    ranges = list()
    num_list.sort()
    for k, g in groupby(enumerate(num_list), lambda(i, x): i - x):
        group = map(itemgetter(1), g)
        if len(group) > 1:
            ranges.append("%d-%d" % (int(group[0]), int(group[-1])))
        else:
            ranges.append(str(group[0]))
    return ", ".join(ranges)


def main():
    ''' Main process '''
    results = dict()
    frame_list = list()
    new_key = ""
    base_dir = _validate_basedir()
    content = os.listdir(base_dir)
    pat_numbers = re.compile(r"[\d]+")
    pat_no_numbers = re.compile(r"^[\D]+$")
    for f_name in content:
        file_path = os.path.join(base_dir, f_name)
        single_file = True
        if not os.path.isfile(file_path):
            continue
        if re.search(pat_no_numbers, f_name):
            results[f_name] = {"file_names": [f_name]}
            continue
        numbers = re.findall(pat_numbers, f_name)
        for number in numbers:
            index = 0
            frame_list = list()
            mod_string = _string_replace(file_path, number, "*")
            file_range = [os.path.basename(x) for x in glob.glob(mod_string)]
            if numbers.count(number) > 1:
                for index in xrange(numbers.count(number)):
                    mod_string = _string_replace(file_path, number, "*", position=index + 1)
                    file_range = [os.path.basename(x) for x in glob.glob(mod_string)]
                    if len(file_range) > 1:
                        break
            if len(file_range) > 1:
                prefix, suffix = os.path.basename(mod_string).split("*")
                single_file = False
                sub_pat = "%d"
                if len(number) > 1:
                    sub_pat = "%%0%dd" % int(len(number))
                new_key = _string_replace(f_name, number, sub_pat, position=index + 1)
                if new_key not in results:
                    results[new_key] = dict()
                    results[new_key]["file_names"] = list()
                for item in file_range:
                    if len(item) == len(f_name) and item in content and item.startswith(prefix) and item.endswith(suffix):
                        content.remove(item)
                        results[new_key]["file_names"].append(item)
                        frame_list.append(int(item.replace(prefix, "").replace(suffix, "")))
                break
        if single_file:
            results[f_name] = {"file_names": [f_name]}
        else:
            results[new_key]["frame_list"] = _get_number_ranges(frame_list)

    _print_results(results)


if __name__ == '__main__':
    main()
