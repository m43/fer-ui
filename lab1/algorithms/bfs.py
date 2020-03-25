import queue

from node import Node


def breadthFirstSearch(s0, succ, goal):
    open_front = queue.Queue()
    closed_front_counter = 0
    front = set()  # both open and closed front, all of em

    initial_node = Node(s0, 0, Node.ROOT_PARENT, 0)
    open_front.put(initial_node)

    result_node = None
    while not open_front.empty():
        closed_front_counter += 1
        current_node = open_front.get()
        front.add(current_node.state)
        if goal(current_node.state):
            result_node = current_node
            break

        for child_node in [Node(s, current_node.depth + 1, current_node)
                           for (s, _) in succ(current_node.state) if s not in front]:
            open_front.put(child_node)
            front.add(child_node.state)

    if result_node:
        print("States visited -->", closed_front_counter)
        print("Number of steps --> ", result_node.depth + 1)
        print(result_node.get_parent_trace(lambda n: n.state))
    else:
        print("No solution could be found. Sorry about that pal")

    print()
    return result_node