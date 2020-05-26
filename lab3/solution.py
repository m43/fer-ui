import csv
import math
import random
import sys
from abc import ABC, abstractmethod
from collections import Counter
from configparser import ConfigParser


class Configuration:
    MODE_VERBOSE = "verbose"
    MODE_TEST = "test"
    KEYWORD_MODE = "mode"
    KEYWORD_MODEL = "model"
    KEYWORD_MAX_DEPTH = "max_depth"
    KEYWORD_NUMBER_OF_TREES = "num_trees"
    KEYWORD_FEATURE_RATIO = "feature_ratio"
    KEYWORD_EXAMPLE_RATIO = "example_ratio"

    DEFAULT_MAX_DEPTH = -1  # (inf)
    DEFAULT_NUMBER_OF_TREES = 1
    DEFAULT_FEATURE_RATIO = 1
    DEFAULT_EXAMPLE_RATIO = 1

    def __init__(self, dict):
        self.mode = dict.get(self.KEYWORD_MODE)
        self.model = dict.get(self.KEYWORD_MODEL)
        self.max_depth = int(dict.get(self.KEYWORD_MAX_DEPTH, self.DEFAULT_MAX_DEPTH))
        self.num_trees = int(dict.get(self.KEYWORD_NUMBER_OF_TREES, self.DEFAULT_NUMBER_OF_TREES))
        self.feature_ratio = float(dict.get(self.KEYWORD_FEATURE_RATIO, self.DEFAULT_FEATURE_RATIO))
        self.example_ratio = float(dict.get(self.KEYWORD_EXAMPLE_RATIO, self.DEFAULT_EXAMPLE_RATIO))

    @staticmethod
    def from_path(path):
        cfg = ConfigParser()
        cfg.read_string("[CONFIG]\n" + open(path).read())
        return Configuration(dict(cfg["CONFIG"].items()))

    def is_verbose_mode(self):
        return self.mode == self.MODE_VERBOSE

    def is_test_mode(self):
        return self.mode == self.MODE_TEST


class Dataset:

    def __init__(self, header, rows):
        self.header = header
        self.header_to_index = dict(zip(self.header, range(len(self.header))))
        self.rows = rows
        self.class_to_frequency = Counter(self.extract_last_column(rows))
        self.classes = list(self.class_to_frequency.keys())
        self.most_frequent_classes = sorted(
            list(self.class_to_frequency.items()),
            key=lambda x: (-x[1], x[0]))

    @staticmethod
    def from_path(path):
        with open(path) as csvfile:
            dataset_reader = csv.reader(csvfile, delimiter=",")
            dataset_lines = list(dataset_reader)
            return Dataset(dataset_lines[0], dataset_lines[1:])

    @staticmethod
    def extract_last_column(rows):
        if not rows:
            return []
        return [row[len(rows[0]) - 1] for row in rows]

    def extract_sample(self, column_indices, row_indices):
        header = [self.header[idx] for idx in column_indices]
        rows = [[self.rows[row_idx][col_idx] for col_idx in column_indices] for row_idx in row_indices]
        return Dataset(header, rows)


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


class Node(ABC):
    @abstractmethod
    def evaluate(self, x_to_index, row):
        pass


class LeafNode(Node):
    def __init__(self, y):
        self.y = y

    def evaluate(self, x_to_index, row):
        return self.y


class CompositeNode(Node):
    def __init__(self, x, x_to_child_node, fallback):
        self.x = x
        self.x_to_child_node = x_to_child_node
        self.fallback = fallback

    def evaluate(self, x_to_index, row):
        return self.x_to_child_node.get(row[x_to_index[self.x]], self.fallback).evaluate(x_to_index, row)


class ID3(Model):
    def __init__(self, config, silent=False):
        super().__init__(config)
        self.config = config
        self.silent = silent

    def fit(self, dataset):
        self.__most_likely = LeafNode(dataset.most_frequent_classes[0][0])
        self.root = self._id3(dataset, dataset.rows, dataset.header[:-1])
        if config.is_test_mode():
            nodes = []
            # Love this recursive lambda <3
            recursive = lambda depth, node: [] if isinstance(node, LeafNode) else nodes.extend([(depth, node.x)]) or [
                recursive(depth + 1, child) for key, child in node.x_to_child_node.items()]
            if isinstance(self.root, CompositeNode):
                recursive(0, self.root)
            nodes.sort(key=lambda x: (-x[0], x[1]), reverse=True)
            if not self.silent and config.is_test_mode():
                print(", ".join(["{}:{}".format(depth, x) for depth, x in nodes]))

    def prediction(self, dataset):
        expected = dataset.extract_last_column(dataset.rows)
        predicted = [self.root.evaluate(dataset.header_to_index, row) for row in dataset.rows]
        if not self.silent and config.is_test_mode():
            self.print_confusion_matrix(expected, predicted, dataset.classes)
        return predicted

    def _id3(self, dataset, current_rows, unprocessed_features, depth=0):
        # if there are no rows left, lets return the class that is most likely in the dataset
        if not current_rows:
            return self.__most_likely

        # is the leaf condition reached?
        y_sorted_counts = sorted(Counter(Dataset.extract_last_column(current_rows)).items(),
                                 key=lambda t: (-t[1], t[0]))
        if not unprocessed_features or len(y_sorted_counts) == 1 or depth == config.max_depth:
            return LeafNode(y_sorted_counts[0][0])

        # Lets pick the next feature and remove it from unprocessed features
        x, x_idx, _ = self.__select_feature_by_information_gain(dataset, current_rows, unprocessed_features)
        new_unprocessed_features = unprocessed_features[:]
        new_unprocessed_features.remove(x)

        # Creating and returning the child node as a CompositeNode
        x_to_child_node = {key: self._id3(dataset, group, new_unprocessed_features, depth + 1)
                           for key, group in group_rows(current_rows, x_idx).items()}

        return CompositeNode(x, x_to_child_node, LeafNode(y_sorted_counts[0][0]))  # TODO or is it `self.__most_likely`?

    def __select_feature_by_information_gain(self, dataset, current_rows, unprocessed_features):
        y_idx = dataset.header_to_index[dataset.header[-1]]
        information_gains = []  # [(x,idx,information_gain), ...]

        entropy_before = self.rows_entropy(current_rows, y_idx)
        for x in unprocessed_features:
            idx = dataset.header_to_index[x]

            # "sunny":[row1 row2 row4] "cloudy":[row3, row5] ..
            groups = group_rows(current_rows, idx)

            entropy_after_x = sum(
                [(len(group) * self.rows_entropy(group, y_idx)) / len(current_rows) for group in groups.values()])

            information_gains.append((x, idx, entropy_before - entropy_after_x))

        information_gains.sort(key=lambda t: (-t[2], t[1]))
        if not self.silent and config.is_verbose_mode():
            print(information_gains)

        return information_gains[0]

    @staticmethod
    def rows_entropy(rows, column_idx):
        e = 0
        for _, count in count_grouped_rows(rows, column_idx).items():
            p = count / len(rows)
            e -= p * math.log2(p)
        return e


def group_rows(array, column_idx) -> dict:
    result = {}
    for row in array:
        key = row[column_idx]
        if key not in result:
            result[key] = []
        result[key].append(row)
    return result


def count_grouped_rows(array, column_idx) -> dict:
    result = {}
    [result.update({i[column_idx]: result.get(i[column_idx], 0) + 1}) for i in array]
    return result


class RandomForrest(Model):
    def __init__(self, config, silent=False):
        super().__init__(config, silent)
        self.config = config
        self.silent = silent
        self.trees = [ID3(config, True) for i in range(config.num_trees)]

    def fit(self, dataset):
        instance_subset = round(config.example_ratio * len(dataset.rows))
        feature_subset = round(config.feature_ratio * (len(dataset.header) - 1))
        for tree in self.trees:
            tree_rows = random.sample(range(len(dataset.rows)), instance_subset)
            tree_features = random.sample(range(len(dataset.header) - 1), feature_subset)
            # for tree, tree_features, tree_rows in zip(self.trees, [[0, 1],
            #                                                        [1, 3],
            #                                                        [0, 1],
            #                                                        [1, 2],
            #                                                        [1, 2]],
            #                                           [[8, 2, 10, 13, 6, 13, 7],
            #                                            [11, 12, 5, 2, 2, 6, 9],
            #                                            [13, 8, 10, 11, 6, 11, 4],
            #                                            [11, 9, 1, 13, 3, 13, 0],
            #                                            [3, 7, 8, 3, 0, 11, 8]]):
            tree_dataset = dataset.extract_sample(tree_features + [-1], tree_rows)
            tree.fit(tree_dataset)
            if not self.silent and self.config.is_test_mode():
                print(" ".join([dataset.header[idx] for idx in tree_features]))
                print(" ".join([str(row) for row in tree_rows]))

    def prediction(self, dataset):
        expected = dataset.extract_last_column(dataset.rows)
        predicted = []
        tree_predictions = [tree.prediction(dataset) for tree in self.trees]
        tree_predictions_transposed = [[tree_predictions[i][j] for i in range(len(tree_predictions))] for j in
                                       range(len(tree_predictions[0]))]
        for i in range(len(dataset.rows)):
            predicted.append(sorted(Counter(tree_predictions_transposed[i]).items(), key=lambda t: (-t[1], t[0]))[0][0])

        if not self.silent:
            self.print_confusion_matrix(expected, predicted, dataset.classes)

        return predicted


class ModelFactory:
    # TODO use dynamic binding to accomplish this
    @staticmethod
    def get(name):
        if name.lower() == "id3":
            return ID3
        if name.lower() == "rf":
            return RandomForrest
        else:
            raise ValueError("No")


if __name__ == '__main__':
    if (len(sys.argv)) != 4:
        raise Exception("Invalid number of arguments. Got {} arguments, expected 4.".format(len(sys.argv)))

    train_path = sys.argv[1]
    test_path = sys.argv[2]
    config_path = sys.argv[3]

    config = Configuration.from_path(config_path)
    train = Dataset.from_path(train_path)
    test = Dataset.from_path(test_path)

    model = ModelFactory.get(config.model)(config)
    model.fit(train)
    model.prediction(test)
