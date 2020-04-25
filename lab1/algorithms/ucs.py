from sortedcontainers import SortedList

from node import Node


def uniform_cost_search(s0, succ, goal):
    open_front = SortedList(key=lambda node: -node.cost)
    closed_front = set()

    initial_node = Node(s0, 0, Node.ROOT_PARENT, 0)
    open_front.add(initial_node)

    result_node = None
    while len(open_front) != 0:
        current_node = open_front.pop()
        closed_front.add(current_node.state)

        if goal(current_node.state):
            result_node = current_node
            break

        open_front.update([Node(s, current_node.depth + 1, current_node, current_node.cost + c)
                           for (s, c) in succ(current_node.state) if s not in closed_front])

    if result_node:
        print("Visited states -->", len(closed_front))
        print("Number of steps --> ", result_node.depth + 1)
        print("Found path of cost --> ", result_node.cost)
        print(result_node.get_parent_trace(lambda n: n.state))
    else:
        print("No solution could be found. Sorry about that pal")

    print()
    return result_node
