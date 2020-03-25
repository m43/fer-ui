class Node:
    ROOT_PARENT = None

    def __init__(self, state, depth=None, parent=None, cost=None):
        """
        Create a new node with as much data given as needed. It is only necessary to specify the state name.

        :param state: the state (string, or any other object)
        :param depth: the depth of this node
        :param parent: the parent of this node
        :param cost: the cost of this node
        """
        self.state = state
        self.depth = depth
        self.parent = parent
        self.cost = cost

    @staticmethod
    def initial_node(state):
        """
        Call this method to create an initial node, with depth and cost initialized to 0, and parent referencing None.

        :param state: the state to create the node from
        :return: the initial node
        """
        return Node(state, 0, None, 0)

    def is_root(self):
        """
        True if this node is a root node, False otherwise. An node is considered to be root if the parent is None.

        :return: True if this node is a root node
        """
        return self.parent is Node.ROOT_PARENT

    def copy(self):
        return Node(self.state, self.depth, self.parent, self.cost)

    def __repr__(self):
        return "Node({},{},{},{})".format(
            self.state, self.depth, self.parent.state if self.parent else self.parent, self.cost)

    def __str__(self):
        return self.__repr__()

    def get_parent_trace(self, node_footprint=__repr__):
        if self.is_root():
            return node_footprint(self)

        parent_stack_trace = [self]
        trace_node = self
        while not trace_node.is_root():
            parent_stack_trace.append(trace_node.parent)
            trace_node = trace_node.parent

        return '--> \n'.join([node_footprint(node) for node in reversed(parent_stack_trace)])
