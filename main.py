import os, json, sys, time
from glob import glob
from nltk.stem import PorterStemmer
from nltk.tokenize import word_tokenize
from bs4 import BeautifulSoup
from pathlib import Path
from collections import defaultdict
from json.decoder import JSONDecodeError
from matrix import InstanceMatrix
import argparse

from build import build
from search import search

def checkToken(token):
    for c in token:
        if c.isalnum():
            return True
    return False

def indexing(stem : list) -> dict:
    #token : file
    token_counts = defaultdict(int)
    # partial_index = dict()

    for s in stem:
        token_counts[s] += 1
    '''
    for token, count in token_counts.items():
        partial_index[token] = [filename + "," + str(count)]
    '''
    return token_counts

#getting file name from full path
def getFileName(path):
    return Path(path).stem

#merging two dictionaries
#dict1 should be full index, dict2 is partial
#dict1 value is list of strings, dict2 value is string
def mergeDict(d1, d2):

    #merged_dict = defaultdict(list)

    #merging two dicts

    for key, value in d2.items():
        if key in d1:
            d1[key] += value

            d1[key].sort()
        else:
            d1[key] = value
    #sorting values which is a list object


    return d1

#sepearting dictionary into term ranges
def seperateDict(dict):

    #a, b, c, d, e, f, g, h, i, j, k, l, m, n, o, p, q, r, s, t, u, v, w, x, y, z, spec = {}, {}, {}, {}, {}, {}, {}, {}, {}, {}, {}, {}, {}, {}, {}, {}, {}, {}, {}, {}, {}, {}, {}, {}, {}, {}, {}
    a_f, g_l, m_s, t_z, spec = {}, {}, {}, {}, {}
    #splitting indices
    for key, val in dict.items():
        if key[0] >= 'a' and key[0] <= 'f':
            a_f[key] = val
        elif key[0] >= 'g' and key[0] <= 'l':
            g_l[key] = val
        elif key[0] >= 'm' and key[0] <= 's':
            m_s[key] = val
        elif key[0] >= 't' and key[0] <= 'z':
            t_z[key] = val
        else:
            spec[key] = val

    return a_f, g_l, m_s, t_z, spec
    #return a, b, c, d, e, f, g, h, i, j, k, l, m, n, o, p, q, r, s, t, u, v, w, x, y, z, spec

def sortAndWriteToDisk(partial_index, filenum):
    filename = f"index{filenum}.json"
    for key in partial_index:
        partial_index[key].sort()

    with open(filename, 'w') as json_file:
        json.dump(partial_index, json_file, sort_keys = True)


def write_full_index(sep_dicts):
    all_file_names = ['a_f.json', 'g_l.json', 'm_s.json','t_z.json','spec.json']
    for i, current_dict in enumerate(sep_dicts):
        if current_dict:
            try:
                with open(all_file_names[i], 'r') as infile:
                    try:
                        #getting index from file
                        old_index = json.load(infile)
                    except JSONDecodeError:
                        old_index = dict()
            except FileNotFoundError:
                old_index = dict()

            #merging dictionaries
            merged_dict = mergeDict(old_index, current_dict)
            with open(all_file_names[i], 'w') as outfile:
            #dumping dict into json file
                json.dump(merged_dict, outfile)

def merge_files(numPartial, full_ind_files):
    for num in range(numPartial):
        filename = f"index{num}.json"
        with open(filename, 'r') as partial_file:
            partial_index = json.load(partial_file)
            sep_dicts = seperateDict(partial_index)
            for i, current_dict in enumerate(sep_dicts):
                if current_dict:
                    try:
                        with open(full_ind_files[i], 'r') as full_file:
                            try:
                                full_index = json.load(full_file)
                            except JSONDecodeError:
                                full_index = dict()
                    except FileNotFoundError:
                        full_index = dict()

                merged_dict = mergeDict(full_index, current_dict)
                with open(full_ind_files[i], 'w') as outfile:
                    json.dump(merged_dict, outfile)
        try:
            os.remove(filename)
        except FileNotFoundError:
            pass


def writeM1(inverted_index, numFiles):
    with open('report.txt', 'w') as file:
        file.write("Number of Documents: " + str(numFiles) + "\n")
        file.write("Number of Unique Tokens: " + str(len(inverted_index)) + "\n")
        file.write("Total Size: " + str(sys.getsizeof(inverted_index) / 1024) + " kb\n")

#writing report to file
def writeReport(files, file_names):

    #holding stats
    num_of_docs = files
    num_of_tokens = 0
    file_size = 0

    #Generate stats report for deliverable
    with open('report.txt', 'w') as file:

        for name in file_names:

            #getting data from index
            with open(name, "r+") as f:
                d = json.load(f)
                num_of_tokens += len(d.keys())
                file_size += os.path.getsize(name) / 1024

        #actually writing to file now
        file.write("Number of Documents: " + str(num_of_docs) +"\n")
        file.write("Number of Unique Tokens: " + str(num_of_tokens) + "\n")
        file.write("Total Size: " + str(file_size) + " kb\n")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    subparsers = parser.add_subparsers()

    # Subcommand build to construct index with optional argument
    # to specify output file to write index to
    parser_build = subparsers.add_parser("build")
    parser_build.set_defaults(func=build)

    # Subcommand search to query index
    # FIXME: ensure index is built/user error if no index found
    parser_search = subparsers.add_parser("search")
    parser_search.add_argument("query", type=str)
    parser_search.set_defaults(func=search)

    args = parser.parse_args()
    args.func(args)

