import random
from collections import Counter

from model.id3 import ID3
from model.model import Model


class RandomForrest(Model):
    def __init__(self, config, silent=False):
        super().__init__(config, silent)
        self.config = config
        self.silent = silent
        self.trees = [ID3(config, True) for _ in range(config.num_trees)]

    def fit(self, dataset):
        instance_subset = round(self.config.example_ratio * len(dataset.rows))
        feature_subset = round(self.config.feature_ratio * (len(dataset.header) - 1))
        # f = ...
        # r = ...
        # for tree, tree_features, tree_rows in zip(self.trees, f, r):
        for tree in self.trees:
            tree_rows = random.sample(range(len(dataset.rows)), instance_subset)
            tree_features = random.sample(range(len(dataset.header) - 1), feature_subset)
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