import math
from collections import Counter
from operator import itemgetter

from model.model import Model
from node import LeafNode, CompositeNode
from dataset import Dataset


class ID3(Model):
    def __init__(self, config, silent=False):
        super().__init__(config)
        self.config = config
        self.silent = silent

    def fit(self, dataset):
        if not dataset.rows:
            raise Exception("Cannot train on empty dataset")

        self.root = self._id3(dataset.header, dataset.header_to_index, dataset.rows, dataset.rows, dataset.header[:-1])
        if not self.silent and self.config.is_test_mode():
            nodes = []
            # Love this recursive lambda <3
            recursive = lambda depth, node: [] if isinstance(node, LeafNode) else nodes.extend([(depth, node.x)]) or [
                recursive(depth + 1, child) for key, child in
                sorted(sorted(node.x_to_child_node.items(), key=itemgetter(0), reverse=True),
                       key=lambda t: (t[1].x if isinstance(t[1], CompositeNode) else ""),
                       reverse=True)]
            if isinstance(self.root, CompositeNode):
                recursive(0, self.root)
            # nodes.sort(key=lambda x: (-x[0], x[1]), reverse=True)
            print(", ".join(["{}:{}".format(depth, x) for depth, x in nodes]))

    def prediction(self, dataset):
        expected = dataset.extract_last_column(dataset.rows)
        predicted = [self.root.evaluate(dataset.header_to_index, row) for row in dataset.rows]
        if not self.silent and self.config.is_test_mode():
            self.print_confusion_matrix(expected, predicted, dataset.classes)
        return predicted

    def _id3(self, header, header_to_index, parent_rows, current_rows, unprocessed_features, depth=0):
        if not current_rows:  # if there are no rows left, lets return the class that is most likely in parent rows
            # NOTE! in practice this line is never reached as I have implemented it this way.
            # This is because I create x_to_child_node only with feature values that can be seen in current rows.
            # raise Exception("This should never be reached!")

            most_likely_in_parent_rows = sorted(Counter(Dataset.extract_last_column(parent_rows)).items(),
                                                key=lambda t: (-t[1], t[0]))[0][0]
            return LeafNode(most_likely_in_parent_rows)

        # is the leaf condition reached?
        y_sorted_counts = sorted(Counter(Dataset.extract_last_column(current_rows)).items(),
                                 key=lambda t: (-t[1], t[0]))
        if not unprocessed_features or len(y_sorted_counts) == 1 or depth == self.config.max_depth:
            return LeafNode(y_sorted_counts[0][0])

        # Lets pick the next feature and remove it from unprocessed features
        x, x_idx, _ = self.__select_feature_by_information_gain(header, header_to_index, current_rows,
                                                                unprocessed_features)
        new_unprocessed_features = unprocessed_features[:]
        new_unprocessed_features.remove(x)

        # if not self.silent and self.config.is_test_mode():
        #     print((", " if depth != 0 else "") + str(depth) + ":" + x, end="")

        # Creating and returning the child node as a CompositeNode
        x_to_child_node = {
            key: self._id3(header, header_to_index, current_rows, group, new_unprocessed_features, depth + 1)
            for key, group in Dataset.group_rows(current_rows, x_idx).items()}

        # if not self.silent and self.config.is_test_mode() and depth == 0:
        #     print()

        return CompositeNode(x, x_to_child_node, LeafNode(y_sorted_counts[0][0]))  # TODO or is it `self.__most_likely`?

    def __select_feature_by_information_gain(self, header, header_to_index, current_rows, unprocessed_features):
        y_idx = header_to_index[header[-1]]
        information_gains = []  # [(x,idx,information_gain), ...]

        entropy_before = self.rows_entropy(current_rows, y_idx)
        for x in unprocessed_features:
            idx = header_to_index[x]

            # "sunny":[row1 row2 row4] "cloudy":[row3, row5] ..
            groups = Dataset.group_rows(current_rows, idx)

            entropy_after_x = sum(
                [(len(group) * self.rows_entropy(group, y_idx)) / len(current_rows) for group in groups.values()])

            information_gains.append((x, idx, entropy_before - entropy_after_x))

        information_gains.sort(key=lambda t: (-t[2], t[0]))
        if not self.silent and self.config.is_verbose_mode():
            print(information_gains)

        return information_gains[0]

    @staticmethod
    def rows_entropy(rows, column_idx):
        e = 0
        for _, count in Dataset.count_grouped_rows(rows, column_idx).items():
            p = count / len(rows)
            e -= p * math.log2(p)
        return e