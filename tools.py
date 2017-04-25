import sys, os, codecs

def dynamicPrint(str):
    sys.stdout.write('\r{}'.format(str))
    sys.stdout.flush()


def checkDirectory(path):
    if not os.path.exists(path):
        os.makedirs(path)

def getListFromFile(path, encoding="utf-8"):
    with codecs.open(path, encoding=encoding) as input_file:
        return input_file.read().splitlines()

def getSetFromFile(path, encoding="utf-8"):
    return set(getListFromFile(path, encoding=encoding))


def WWconcantenateTrain(path_ww, path_train, path_output):

    with codecs.open(path_ww, encoding="utf-8") as wwFile:
        data_ww = wwFile.read()

    with codecs.open(path_train, encoding="utf-8") as trainFile:
        data_train = trainFile.read()

    with codecs.open(path_output, mode="w", encoding="utf-8") as output:
        print >> output, data_ww + data_train[:-1]


def getIntersectionDict(dict1, dict2):
    keys_intersections = set(dict1.keys()) & set(dict2.keys())

    dict_intersection = dict()
    for key in keys_intersections:
        if key in dict1:
            value1 = dict1[key]
        else:
            continue
        if key in dict2:
            value2 = dict2[key]
        else:
            continue
        dict_intersection[key] = min(value1, value2)

    return dict_intersection


def getUnionDict(dict1, dict2):
    keys_union = set(dict1.keys()) | set(dict2.keys())
    dict_union = dict()

    for key in keys_union:
        if key in dict1:
            value1 = dict1[key]
        else:
            dict_union[key] = dict2[key]
            continue
        if key in dict2:
            value2 = dict2[key]
        else:
            dict_union[key] = value1
            continue
        dict_union[key] = max(value1, value2)

    return dict_union