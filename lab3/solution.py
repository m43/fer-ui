import sys
import csv
from abc import ABC, abstractmethod
from collections import Counter
from configparser import ConfigParser
import math


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
        self.max_depth = dict.get(self.KEYWORD_MAX_DEPTH, self.DEFAULT_MAX_DEPTH)
        self.num_trees = dict.get(self.KEYWORD_NUMBER_OF_TREES, self.DEFAULT_NUMBER_OF_TREES)
        self.feature_ratio = dict.get(self.KEYWORD_FEATURE_RATIO, self.DEFAULT_FEATURE_RATIO)
        self.example_ratio = dict.get(self.KEYWORD_EXAMPLE_RATIO, self.DEFAULT_EXAMPLE_RATIO)

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


class Model(ABC):
    @abstractmethod
    def __init__(self, config):
        pass

    @abstractmethod
    def fit(self, dataset):
        pass

    @abstractmethod
    def prediction(self, dataset):
        pass


class Node(ABC):
    @abstractmethod
    def evaluate(self, row):
        pass


class LeafNode(Node):
    def __init__(self, y):
        self.y = y

    def evaluate(self, row):
        return self.y


class CompositeNode(Node):
    def __init__(self, x, x_idx, x_to_child_node):
        self.x = x
        self.x_idx = x_idx
        self.x_to_child_node = x_to_child_node

    def evaluate(self, row):
        return self.x_to_child_node[row[self.x_idx]].evaluate(row)


class ID3(Model):
    def __init__(self, config):
        super().__init__(config)
        self.config = config

    def fit(self, dataset):
        self.root = self._id3(dataset, dataset.rows, dataset.header[:-1])
        if config.is_test_mode():
            nodes = []
            # Love this recursive lambda <3
            recursive = lambda depth, node: [] if isinstance(node, LeafNode) else nodes.extend([(depth, node.x)]) or [
                recursive(depth + 1, child) for key, child in node.x_to_child_node.items()]
            if isinstance(self.root, CompositeNode):
                recursive(0, self.root)
            print(", ".join(["{}:{}".format(depth, x) for depth, x in nodes]))

    def prediction(self, dataset):
        result = [self.root.evaluate(row) for row in dataset.rows]
        if config.is_test_mode():
            print(" ".join(result))
        return result

    def _id3(self, dataset, current_rows, unprocessed_features, depth=0):
        # if there are no rows left, lets return the class that is most likely in the dataset
        if not current_rows:
            return LeafNode(dataset.most_frequent_classes[0][0])

        # is the leaf condition reached?
        y_sorted_counts = sorted(Counter(Dataset.extract_last_column(current_rows)).items(),
                                 key=lambda x: (-x[1], x[0]))
        if not unprocessed_features or len(y_sorted_counts) == 1:
            return LeafNode(y_sorted_counts[0][0])

        # Lets pick the next feature and remove it from unprocessed features
        x, x_idx, _ = self.__select_feature_by_information_gain(dataset, current_rows, unprocessed_features)
        new_unprocessed_features = unprocessed_features[:]
        new_unprocessed_features.remove(x)

        # Creating and returning the child node as a CompositeNode
        x_to_child_node = {key: self._id3(dataset, group, new_unprocessed_features, depth + 1)
                           for key, group in group_rows(current_rows, x_idx).items()}
        return CompositeNode(x, x_idx, x_to_child_node)

    def __select_feature_by_information_gain(self, dataset, current_rows, unprocessed_features):
        y_idx = dataset.header_to_index[dataset.header[-1]]
        information_gains = []  # [(x,idx,information_gain), ...]

        entropy_before = self.rows_entropy(current_rows, y_idx)
        for x in unprocessed_features:
            idx = dataset.header_to_index[x]

            # "sunny":[row1 row2 row4] "cloudy":[row3, row5] ..
            groups = group_rows(current_rows, idx)

            # (n, y1:1 y2:2 y3:10 ..)
            entropy_after_x = sum(
                [(len(group) * self.rows_entropy(group, y_idx)) / len(current_rows) for group in groups.values()])

            # entropy = 0
            # for n, counts in group_y_counts:
            #     for count in counts.items():
            #         p = count[1] / n
            #         entropy -= p * math.log2(p)
            # information_gains.append((x, idx, entropy_before - entropy))

            information_gains.append((x, idx, entropy_before - entropy_after_x))

        information_gains.sort(key=lambda t: (-t[2], t[1]))
        if config.is_verbose_mode():
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


class ModelFactory:
    # TODO use dynamic binding to accomplish this
    @staticmethod
    def get(name):
        if name.lower() == "id3":
            return ID3
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
