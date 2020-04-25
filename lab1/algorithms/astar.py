from sortedcontainers import SortedList
from operator import itemgetter, attrgetter

from node import Node


def a_star(s0, succ, goal, h):
    f = lambda node: node.cost + h(node.state)
    open_front = SortedList(key=lambda node: (-f(node), node.cost, +node.depth)) # TODO optimisation could be done on
    open_front_dict = {}  # will map state->Node
    closed_front_dict = {}  # will map state->Node. necessary for non-consistent heuristics

    initial_state = Node(s0, 0, Node.ROOT_PARENT, 0)
    open_front.add(initial_state)
    open_front_dict[initial_state.state] = initial_state

    result_node = None
    while len(open_front) != 0:
        current_node = open_front.pop()
        open_front_dict.pop(current_node.state)
        if current_node.state in closed_front_dict:
            continue  # This is in case that the expanding below puts two nodes of same state into open_front
        closed_front_dict[current_node.state] = current_node

        if goal(current_node.state):
            result_node = current_node
            break

        for child_node in [Node(s, current_node.depth + 1, current_node, current_node.cost + c)
                           for (s, c) in succ(current_node.state)
                           if (s not in closed_front_dict
                               or
                               # This check below is needed for inconsistent heuristics
                               current_node.cost + c < closed_front_dict[s].cost)
                              and (s not in open_front_dict
                                   or
                                   current_node.cost + c < open_front_dict[s].cost
                              )]:  # Love this long line. <3
            if child_node.state in open_front_dict:
                open_front.remove(open_front_dict[child_node.state])
            open_front.add(child_node)
            open_front_dict[child_node.state] = child_node

    if result_node:
        print("States visited -->", len(closed_front_dict))
        print("Number of steps --> ", result_node.depth + 1)
        print("Found path of cost --> ", result_node.cost)
        print(result_node.get_parent_trace(lambda n: n.state))
    else:
        print("No solution could be found. Sorry about that pal")

    print()
    return result_node
