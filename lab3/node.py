from abc import ABC, abstractmethod


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
