#!/usr/bin/python
# -*- coding: utf8 -*-

from pymystem3 import Mystem
import sys
import regex as re

NAME = u"имя"
name_tags = {u"имя", u"фам", u"отч"}


class CollocationSyntax():
    def __init__(self, collocation):
        self.collocation = collocation
        self.reverse_order = " ".join(reversed(collocation.split()))
        self.replace = "_".join(collocation.split())


def lemmatize(sentence, mystem, words_n=None):
    """
    :param sentence: input sentence
    :param words_n: to check if the number of words has changed after lemmatization
    :return:
    """
    lemmatized_words = mystem.lemmatize(sentence)
    lemmatized = []

    for i, lemma in enumerate(lemmatized_words):
        if lemma != " " and lemma != "\n":
            try:
                analysis = mystem.analyze(lemma)[0]["analysis"][0]["gr"].split(",")
                if len(analysis) > 1 and analysis[1] in name_tags:
                    lemma = NAME
                elif lemma == u"банка":
                    lemma = u"банк"
            except:
                if lemma == u"банка":
                    lemma = u"банк"
            lemmatized.append(lemma)

    if words_n:
        if len(lemmatized) != len(words_n):
            print lemmatized, sentence.split()
            sys.exit(1)

    return lemmatized

def add_collocation(sentence, collocation):
    """
    :param sentence:
    :param collocation: instance of CollocationSyntax
    :return:
    """
    sentence = re.sub(ur"(^| )" + collocation.collocation + ur"($| )", " " + collocation.replace + " ", sentence)
    sentence = re.sub(ur"(^| )" + collocation.reverse_order + ur"($| )", " " + collocation.replace + " ", sentence)
    return sentence


def delete_repeated_words(sentence):
    """
    :param sentence: sentence to delete repeated words
    :return:
    """
    new_phrase = []

    for word in sentence.split():
        if not new_phrase or word != new_phrase[-1]:
            new_phrase.append(word)

    return new_phrase
