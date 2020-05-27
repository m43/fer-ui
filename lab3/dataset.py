import csv
from collections import Counter


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

    @staticmethod
    def group_rows(array, column_idx) -> dict:
        result = {}
        for row in array:
            key = row[column_idx]
            if key not in result:
                result[key] = []
            result[key].append(row)
        return result

    @staticmethod
    def count_grouped_rows(array, column_idx) -> dict:
        result = {}
        [result.update({i[column_idx]: result.get(i[column_idx], 0) + 1}) for i in array]
        return result