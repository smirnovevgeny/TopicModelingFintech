class Branches():

    class outputData:

        def __init__(self):
            self.sentence_id = []
            self.branch_id = []
            self.branch = []
            self.branch_ids_local = []
            self.branch_ids_global = []

        def addValues(self, SENTENCE_ID, BRANCH_ID, BRANCH, WORD_IDS_LOCAL=None, WORD_IDS_GLOBAL=None):
            self.sentence_id.append(SENTENCE_ID)
            self.branch_id.append(BRANCH_ID)
            self.branch.append(BRANCH)
            if WORD_IDS_LOCAL:
                self.branch_ids_local.append(WORD_IDS_LOCAL)
            if WORD_IDS_GLOBAL:
                self.branch_ids_global.append(WORD_IDS_GLOBAL)

        def getDataFrame(self):

            import pandas as pd

            SENTENCE_ID = "sentence_id"
            WORD_IDS_LOCAL = "word_ids_local"
            WORD_IDS_GLOBAL = "word_ids_global"
            BRANCH = "branch"
            BRANCH_ID = "branch_id"

            dataFrame = pd.DataFrame()
            dataFrame[SENTENCE_ID] = self.sentence_id
            dataFrame[BRANCH_ID] = self.branch_id
            dataFrame[BRANCH] = self.branch
            if self.branch_ids_local:
                dataFrame[WORD_IDS_LOCAL] = self.branch_ids_local
            if self.branch_ids_global:
                dataFrame[WORD_IDS_GLOBAL] = self.branch_ids_global

            return dataFrame


    def __init__(self, vocab=None, stop_words=None, bad_tags={u'ADP', U'CONJ', U'AUX', U'PRON', U'NUM', U'SCONJ'}):
        self.dictionary_pairs = dict()
        self.dictionary_frequency = dict()
        self.bad_tags = bad_tags
        self.stop_words = stop_words
        self.vocab = vocab
        if self.vocab:
            self.check = self.vocab_check
        else:
            self.check = self.stop_word_check
        self.error_number = 0
        self.outputData = self.outputData()
        self.passNext = False

    def stop_word_check(self, word):
        return word in self.stop_words

    def vocab_check(self, word):
        return not (word in self.vocab)

    def addValues(self, words, parent_ids, tags, sentence_id,  word_ids_local, word_ids_global=None, save_local_ids=True, window_size=2,
                  addTags=True):

        if self.passNext:
            self.passNext = False
            return

        ROOT = -1
        DELETED = -2

        leafes = set(range(len(word_ids_local)))
        max_parent = len(word_ids_local) - 1
        not_leafes = set()
        deleted = set()

        len_number = len(words)

        for i in xrange(len_number):
            word, word_id_local, tag, parent_id = words[i], word_ids_local[i], tags[i], parent_ids[i]
            if parent_id > max_parent or parent_id == word_id_local:
                self.passNext = True
                print "error", parent_id, max_parent, word_id_local, parent_id > max_parent, parent_id == word_id_local
                return
            if parent_id != DELETED and (self.check(word) or tag in self.bad_tags):

                for j in xrange(len(words)):
                    if parent_ids[j] == word_id_local:
                        parent_ids[j] = parent_id

                parent_ids[i] = DELETED
                leafes.remove(i)
                deleted.add(i)

            elif addTags:
                if word in self.dictionary_frequency:
                    self.dictionary_frequency[word] += 1
                else:
                    self.dictionary_frequency[word] = 1

        for word_id, parent_id in zip(word_ids_local, parent_ids):
            if parent_id != DELETED:
                not_leafes.add(parent_id)

        not_leafes.difference({ROOT})
        leafes.difference_update(not_leafes)
        if word_ids_global and save_local_ids:
            branch_elements = zip(tags, words, word_ids_local, word_ids_global)
        elif save_local_ids:
            branch_elements = zip(tags, words, word_ids_local)
        else:
            branch_elements = zip(tags, words)


        branch_id = 0

        for leaf in leafes:
            search_element = leaf
            new_branch = []

            while search_element != ROOT:
                if search_element not in deleted:
                    new_branch.append(branch_elements[search_element])
                search_element = parent_ids[search_element]

            if len(new_branch) > 1:
                new_branch.reverse()
                extracted = zip(*new_branch)
                if addTags:
                    self.addTags(zip(extracted[0], extracted[1]), window_size)
                if word_ids_global and save_local_ids:
                    self.outputData.addValues(sentence_id, branch_id, " ".join(extracted[1]),
                                          list(extracted[2]), list(extracted[3]))
                elif save_local_ids:
                    self.outputData.addValues(sentence_id, branch_id, " ".join(extracted[1]),
                                              list(extracted[2]))
                else:
                    self.outputData.addValues(sentence_id, branch_id, " ".join(extracted[1]))
                branch_id += 1

    def addTags(self, branch, window_size):

        if len(branch) >= window_size:

            tags = []
            words = []

            for i, element in enumerate(branch):
                tag, word = element
                if tag not in self.bad_tags:
                    tags.append(tag)
                    words.append(word)
                else:
                    continue

                if i >= window_size - 1:
                    words_tuple = tuple(sorted(words))
                    tags_tuple = tuple(sorted(tags))
                    try:
                        self.dictionary_pairs[tags_tuple][words_tuple] += 1
                    except:
                        try:
                            self.dictionary_pairs[tags_tuple][words_tuple] = 1
                        except:
                            self.dictionary_pairs[tags_tuple] = {words_tuple: 1}
                    del tags[0], words[0]


    def addDataFrame(self, data, addTags=True, save_global_ids=True, save_local_ids=True):

        from tools import dynamicPrint

        SENTENCE_ID = "sentence_id"
        WORD_ID = "word_id"
        WORD = "lemmatized"
        TAG = "tag"
        PARENT_ID = "parent_id"

        start_row = data.iloc[0]
        current_sentence_id = start_row[SENTENCE_ID]

        word_ids_local = []
        if save_global_ids:
            word_ids_global = []
        else:
            word_ids_global = None
        words = []
        tags = []
        parent_ids = []

        words_n = len(data)

        i = 0

        for index, row in data.iterrows():
            if i % 10000 == 0:
                dynamicPrint("word {} from {}".format(i, words_n))
            sentence_id = row[SENTENCE_ID]

            if sentence_id != current_sentence_id:

                if len(word_ids_local) > 1:
                    self.addValues(words, parent_ids, tags, current_sentence_id, word_ids_local, word_ids_global, save_local_ids, addTags=addTags)

                word_ids_local = []
                if save_global_ids:
                    word_ids_global = []
                words = []
                tags = []
                parent_ids = []
                current_sentence_id = sentence_id

            word_ids_local.append(row[WORD_ID])
            if save_global_ids:
                word_ids_global.append(index)
            words.append(row[WORD])
            tags.append(row[TAG])
            parent_ids.append(row[PARENT_ID])

            i += 1

        self.addValues(words, parent_ids, tags, current_sentence_id, word_ids_local, word_ids_global, addTags=addTags)

    def dump_dictionaries(self, path):
        import pickle
        pickle.dump(self.dictionary_frequency, open(path + "dictionary_frequency.pkl", "wb"))
        pickle.dump(self.dictionary_pairs, open(path + "dictionary_pairs.pkl", "wb"))