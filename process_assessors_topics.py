#!/usr/bin/python
# -*- coding: utf8 -*-

"""
input:
        argv[1] : folder with train text for each topic
output: in folder argv[2]
        syntax analysis + lemmatization + names_correction
        topic_names.pkl
        metaData.pkl
"""

import pandas as pd
import numpy as np
import os, csv
import regex as re
from subprocess import call
import codecs
from tools import checkDirectory, dynamicPrint
import pickle
from preprocess_line import lemmatize
from pymystem3 import Mystem



WORD_ID = "word_id"
WORD = "word"
PARENT_ID = "parent_id"
TAG = "tag"
DEPENDENCY = "dependency"
SENTENCE_ID = "sentence_id"
TOPIC = "topic"
LEMMATIZED = "lemmatized"
NAME = u"имя"
name_tags = {u"имя", u"фам", u"отч"}

ERROR_MESSAGE = "something has gone wrong"



def make_set_each_topic(min_number=5, verbose=False):
    """
    Delete identical sentences from train text
    :param min_number: The minimum value of lines for topic to be included in model
    :return: print the number of processed files
    """
    files_number = 0
    checkDirectory(folder_prepare)
    for file_name in os.listdir(input_path):
        if not file_name.startswith(".") and not file_name.endswith(".ipynb") and not file_name.endswith(".py") and "for" not in file_name:
            with codecs.open(input_path + file_name, "r", encoding="utf-8") as inputFile:
                lines = inputFile.read().splitlines()
            if len(lines) > min_number:
                files_number += 1
                if verbose:
                    print file_name
                lines = [line.strip() for line in lines if line]
                with codecs.open(folder_prepare + file_name, "w", encoding="utf-8") as outputFile:
                    print >> outputFile, "\n\n".join([lines[0]] + list(set(lines[1:])))


def syntaxnet_post_process(file_from):

    WORD_ID = "word_id"
    WORD = "word"
    PARENT_ID = "parent_id"
    TAG = "tag"
    DEPENDENCY = "dependency"
    SENTENCE_ID = "sentence_id"
    LEMMATIZED = "lemmatized"

    from_syntaxnet = pd.read_table(file_from, encoding="utf-8", header=None, dtype={0: np.int32, 6: np.int32},
                                   quoting=csv.QUOTE_NONE, engine="c")[[0, 1, 6, 3, 7]].fillna("")
    from_syntaxnet.columns = [[WORD_ID, WORD, PARENT_ID, TAG, DEPENDENCY]]
    from_syntaxnet[WORD_ID] -= 1
    from_syntaxnet[PARENT_ID] -= 1

    sentence_id = -1
    sentences_id = []
    lemmatized = []
    words = []

    lines_n = len(from_syntaxnet)

    mystem = Mystem()

    for index, (word_id, word) in enumerate(zip(from_syntaxnet[WORD_ID], from_syntaxnet[WORD])):

        if index % 10000 == 0:
            dynamicPrint("line {} from {}".format(index, lines_n))

        if word_id == 0:
            sentence_id += 1
            lemmatized += lemmatize(" ".join(words), mystem)
            words = []

        words.append(word)
        sentences_id.append(sentence_id)

    lemmatized += lemmatize(" ".join(words), mystem)

    from_syntaxnet[SENTENCE_ID] = sentences_id
    # print len(lemmatized), len(sentences_id)
    from_syntaxnet[LEMMATIZED] = lemmatized
    return from_syntaxnet


def create_topic_name_dict(topic_names_set, background_name=u"== фон"):

    global topic_names_dict
    topic_names_dict = dict()
    topic_names_dict[background_name] = len(topic_names_set) - 1
    topic_names_set.remove(background_name)

    for i, topic_name in enumerate(topic_names_set):
        topic_names_dict[topic_name] = i

    path = output_path + "topic_names.pkl"
    pickle.dump(topic_names_dict, open(path, "wb"))

def main(input_dir="data/assessor_tasks/topics_alena/", output_dir="data/labeled_data/topics_alena/", verbose=False):

    global input_path, output_path, folder_prepare, file_from

    input_path = input_dir
    output_path = output_dir

    folder_prepare = input_path + "forsyntaxnet/"
    file_to = folder_prepare + 'to_syntaxnet.txt'
    file_from = folder_prepare + "from_syntaxnet.txt"
    SYNTAXNET_MODELS_PATH = "~/Python_libs/models/syntaxnet/syntaxnet/models"

    if call(["rm", "-rf", folder_prepare]) != 0:
        print ERROR_MESSAGE

    make_set_each_topic()

    # Не должно быть символов типа ".,_-"
    # Выход: предложение, метадата,

    sentences = []
    topics = []
    topic = ''
    topic_names_set = set()

    for file_index, filename in enumerate(sorted(os.listdir(folder_prepare))):
        if not os.path.isdir(filename) and not (".py" in filename or ".ipynb" in filename) and filename[0] != "." and not "csv" in filename:
            with codecs.open(os.path.join(folder_prepare, filename), 'r', encoding="utf-8") as reader:
                for line_index, line in enumerate(reader):
                    line = line.rstrip()
                    if line_index == 0:
                        topic = line
                        topic_names_set.add(topic)
                        if verbose:
                            print topic, filename
                    elif line:
                        line = re.sub(ur'[^A-Za-zА-Яа-я ]', u' ', line).lower().strip()
                        line = re.sub("\s\s+", " ", line)
                        sentences.append(line)
                        topics.append(topic)

    with codecs.open(file_to, 'w', encoding="utf-8") as output:
        print >> output, "\n".join(sentences)

    create_topic_name_dict(topic_names_set)

    metaData = pd.DataFrame()
    metaData[TOPIC] = [topic_names_dict[topic] for topic in topics]
    metaData.to_pickle(output_path + "metaData.pkl")

    print u"Число тем - {}, число тематических сегментов - {}".format(len(set(topics)), len(sentences))

    print "Запустим syntaxnet"
    if os.system("./run_syntaxnet.sh {} {} {}".format(file_to, file_from, SYNTAXNET_MODELS_PATH)) != 0:
        print ERROR_MESSAGE

    print "Обработка выхода от SyntaxNet"
    from_syntaxnet = syntaxnet_post_process(file_from)
    from_syntaxnet.to_pickle(folder_prepare + "sentence_analysis.pkl")
