from __future__ import division

import codecs
import time
from collections import defaultdict
from math import log
import sys
from tqdm import tqdm
from tools import dynamicPrint, checkDirectory


D_Levy = 0


def __process_window(cooc_dict, word_dict, post, main_index, end_index):
    global D_Levy
    main_word = post[main_index]
    for index in range(main_index + 1, end_index):
        cooc_dict[(main_word, post[index])] += 1
        cooc_dict[(post[index], main_word)] += 1
        word_dict[main_word] += 1
        word_dict[post[index]] += 1
        D_Levy += 2 * 1


def __process_post(cooc_dict, word_dict, vocab, post):
    post_length = len(post)

    for index, word in enumerate(post):
        if index <= post_length - WINDOW:
            __process_window(cooc_dict, word_dict, post, index, index + WINDOW)
        else:
            __process_window(cooc_dict, word_dict, post, index, post_length)
        vocab.add(word)


def __save_pmi(cooc_dict, word_dict, vocab_dict):
    print "\nsave pmi to " + OUTPUT_FILE_PMI + "\n"
    with codecs.open(OUTPUT_FILE_PMI, 'w', ENCODING) as f:
        for (word_1, word_2), n_uv in cooc_dict.iteritems():
            n_u = word_dict[word_1]
            n_v = word_dict[word_2]
            print>>f, vocab_dict[word_1], vocab_dict[word_2], max(0, log(D_Levy*n_uv/(n_u*n_v)))


def __save_vocab(list_vocab):
    print "\nsave vocab to " + OUTPUT_FILE_VOCAB + "\n"

    with codecs.open(OUTPUT_FILE_VOCAB, 'w', ENCODING) as f:
        list_len = len(list_vocab)
        for i, word in enumerate(list_vocab):
            dynamicPrint(str(i) + " from " + str(list_len))
            print>>f, word


def __save_vw(cooc_dict, vocab):
    print "save wv to " + OUTPUT_FILE_VW + "\n"
    with codecs.open(OUTPUT_FILE_VW, 'w', ENCODING) as f:

        currentWord = ""
        word_string = ""

        for word_1, word_2 in tqdm(sorted(cooc_dict)):
            if currentWord != word_1:
                currentWord = word_1
                if word_string:
                    print >> f, word_string
                word_string = word_1 + ' |@default_class'
            else:
                word_string += ' ' + word_2 + ':' + str(cooc_dict[(word_1, word_2)])

        print >> f, word_string

def main(lines, output_dir, window, create_vw=True, encoding="utf-8"):

    global OUTPUT_FILE_VW, OUTPUT_FILE_VOCAB, OUTPUT_FILE_PMI, cooc_dict, word_dict, vocab, WINDOW, ENCODING
    checkDirectory(output_dir)
    OUTPUT_FILE_VW = output_dir + 'ww_vw.txt'
    OUTPUT_FILE_VOCAB = output_dir + 'vocab.txt'
    OUTPUT_FILE_PMI = output_dir + 'pmi.txt'
    WINDOW = window
    ENCODING = encoding

    start_time = time.time()
    cooc_dict = defaultdict(int)
    word_dict = defaultdict(int)
    vocab = set()

    for line in tqdm(lines):
        words = line.split()
        __process_post(cooc_dict, word_dict, vocab, words)
    if create_vw:
        __save_vw(cooc_dict, vocab)
    __save_vocab(list(vocab))
    vocab_dict = {word: index for index, word in enumerate(list(vocab))}
    __save_pmi(cooc_dict, word_dict, vocab_dict)

    print '\nTime elapsed: ' + str(round(time.time() - start_time, 3)) + ' sec.'

if __name__ == '__main__':

    source_file = sys.argv[1]

    ENCODING = 'utf8'
    SOURCE_FILE = sys.argv[1]
    WINDOW = 7
    CREATE_VW = True
    FOLDER = sys.argv[2]
    OUTPUT_FILE_VW = FOLDER + 'ww_vw.txt'
    OUTPUT_FILE_VOCAB = FOLDER + 'vocab.txt'
    OUTPUT_FILE_PMI = FOLDER + 'pmi.txt'

    checkDirectory(FOLDER)
    start_time = time.time()
    cooc_dict = defaultdict(int)
    word_dict = defaultdict(int)
    vocab = set()

    with codecs.open(SOURCE_FILE, 'r', ENCODING) as f:
        for line in tqdm(f):
            words = line.split()[2:]
            __process_post(cooc_dict, word_dict, vocab, words)
    if CREATE_VW:
        __save_vw(cooc_dict, vocab)
    __save_vocab(list(vocab))
    vocab_dict = {word: index for index, word in enumerate(list(vocab))}
    __save_pmi(cooc_dict, word_dict, vocab_dict)
    print '\nTime elapsed: ' + str(round(time.time() - start_time, 3)) + ' sec.'
