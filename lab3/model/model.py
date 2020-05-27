from abc import ABC, abstractmethod


class Model(ABC):
    @abstractmethod
    def __init__(self, config, silent=False):
        pass

    @abstractmethod
    def fit(self, dataset):
        pass

    @abstractmethod
    def prediction(self, dataset):
        pass

    @staticmethod
    def print_confusion_matrix(expected, predicted, classes):
        confusion_matrix = {}
        correct = 0
        for e, p in zip(expected, predicted):
            if e == p:
                correct += 1
            confusion_matrix[e, p] = confusion_matrix.get((e, p), 0) + 1
        print(" ".join(predicted))
        print(correct / len(expected))
        for clazz_e in sorted(classes):
            print(
                " ".join([str(confusion_matrix.get((clazz_e, clazz_p), 0)) for clazz_p in sorted(classes)]))
